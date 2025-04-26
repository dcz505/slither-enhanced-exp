"""
区间分析模块 (Range Analysis Module)

本模块实现了增强的区间分析，用于DeFi智能合约的值范围分析。
主要提供以下功能：
1. 区间表示及操作（交集、并集、加宽、收窄等）
2. 具体解释器
3. 工作列表算法实现的路径敏感分析
4. DeFi特定约束验证
5. SafeMath库识别与处理
6. 简单函数调用的跨函数分析
7. 增强的DeFi合约和变量识别

更新日志:
- v1.0: 初始版本，实现基本的区间分析功能
- v1.1: 增加对SafeMath库的识别和处理，改进DeFi相关代码的识别能力，增强跨函数分析
"""

from slither.slithir.operations import Binary, Assignment, Member, TypeConversion, SolidityCall
from slither.slithir.variables import Constant, TemporaryVariable, ReferenceVariable
from slither.core.variables.local_variable import LocalVariable
from slither.core.variables.state_variable import StateVariable
from slither.core.declarations import Contract, Function
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from collections import deque
import copy
import re
import math
import logging

# 配置日志
logger = logging.getLogger("IntervalAnalysis")

class Interval:
    """
    区间表示类，支持区间运算
    
    用于表示变量可能的取值范围。支持：
    - 空区间（bottom，表示没有可能的值）
    - 完整区间（top，表示所有可能的值）
    - 具体边界区间 [min_val, max_val]
    
    区间分析是抽象解释的一种实现，使用区间格(interval lattice)表示程序状态
    """
    def __init__(self, min_val=None, max_val=None):
        """
        初始化区间
        
        Args:
            min_val: 区间最小值，None表示负无穷
            max_val: 区间最大值，None表示正无穷
        
        如果min_val和max_val都为None，表示空区间（bottom）
        如果min_val为float('-inf')且max_val为float('inf')，表示全区间（top）
        """
        self.min_val = min_val
        self.max_val = max_val
        # 空区间(bottom)表示没有可能的值
        self.is_bottom = min_val is None and max_val is None
        # 全区间(top)表示所有可能的值
        self.is_top = (min_val == float('-inf') and max_val == float('inf'))
    
    def __repr__(self):
        """
        区间的字符串表示
        
        Returns:
            str: 区间的字符串形式
                - "⊥" 表示空区间
                - "⊤" 表示全区间
                - "[min, max]" 表示具体边界区间
        """
        if self.is_bottom:
            return "⊥"
        if self.is_top:
            return "⊤"
        return f"[{self.min_val}, {self.max_val}]"
    
    def join(self, other):
        """
        区间并集（最小包围区间）
        
        计算两个区间的最小上确界(least upper bound)，
        即包含两个区间所有可能值的最小区间
        
        Args:
            other: 另一个区间
            
        Returns:
            Interval: 包含两个区间所有值的最小区间
        """
        if self.is_bottom:
            return copy.deepcopy(other)
        if other.is_bottom:
            return copy.deepcopy(self)
        
        # 处理一个区间为 top 的情况
        if self.is_top or other.is_top:
            return Interval(float('-inf'), float('inf'))
        
        # 取两区间的最小下界和最大上界
        new_min = min(self.min_val, other.min_val) if (self.min_val is not None and other.min_val is not None) else None
        new_max = max(self.max_val, other.max_val) if (self.max_val is not None and other.max_val is not None) else None
        return Interval(new_min, new_max)
    
    def meet(self, other):
        """
        区间交集
        
        计算两个区间的最大下确界(greatest lower bound)，
        即同时满足两个区间约束的最大区间
        
        Args:
            other: 另一个区间
            
        Returns:
            Interval: 两个区间的交集
        """
        if self.is_bottom or other.is_bottom:
            return Interval()  # 返回空区间
        
        # 处理一个区间为 top 的情况
        if self.is_top:
            return copy.deepcopy(other)
        if other.is_top:
            return copy.deepcopy(self)
        
        # 取两区间的最大下界和最小上界
        new_min = max(self.min_val, other.min_val) if (self.min_val is not None and other.min_val is not None) else None
        new_max = min(self.max_val, other.max_val) if (self.max_val is not None and other.max_val is not None) else None
        
        # 如果下界大于上界，表示交集为空
        if (new_min is not None and new_max is not None) and (new_min > new_max):
            return Interval()  # 空区间
        return Interval(new_min, new_max)
    
    def widen(self, other):
        """
        加宽操作，用于加速不动点计算
        
        在抽象解释中，加宽操作用于控制迭代次数，
        通过快速扩大区间范围达到收敛
        
        Args:
            other: 另一个区间
            
        Returns:
            Interval: 加宽后的区间
        """
        if self.is_bottom:
            return copy.deepcopy(other)
        if other.is_bottom:
            return copy.deepcopy(self)
        
        # 无限上下界的处理：如果other的界限突破了self的界限，则扩展到无穷
        new_min = float('-inf') if (other.min_val is not None and self.min_val is not None and other.min_val < self.min_val) else self.min_val
        new_max = float('inf') if (other.max_val is not None and self.max_val is not None and other.max_val > self.max_val) else self.max_val
        
        return Interval(new_min, new_max)
    
    def narrow(self, other):
        """
        收窄操作，用于恢复精度
        
        在完成加宽操作后，使用收窄操作恢复一部分精度，
        通常用在不动点计算结束后的精化阶段
        
        Args:
            other: 另一个区间（通常是加宽前的区间）
            
        Returns:
            Interval: 收窄后的区间
        """
        if self.is_bottom or other.is_bottom:
            return Interval()
        
        # 如果当前区间边界是无穷，使用other的边界替换
        new_min = other.min_val if self.min_val == float('-inf') else self.min_val
        new_max = other.max_val if self.max_val == float('inf') else self.max_val
        
        return Interval(new_min, new_max)
    
    def __eq__(self, other):
        """
        区间相等比较
        
        Args:
            other: 另一个对象
            
        Returns:
            bool: 如果other是区间且与当前区间相等则返回True
        """
        if not isinstance(other, Interval):
            return False
        return ((self.is_bottom and other.is_bottom) or 
                (self.is_top and other.is_top) or
                (self.min_val == other.min_val and self.max_val == other.max_val))
    
    def is_subset(self, other):
        """
        检查当前区间是否是另一个区间的子集
        
        Args:
            other: 另一个区间
            
        Returns:
            bool: 如果当前区间是other的子集则返回True
        """
        if self.is_bottom:
            return True  # 空集是任何集合的子集
        if other.is_bottom:
            return False  # 非空集不是空集的子集
        if other.is_top:
            return True  # 任何集合都是全集的子集
        if self.is_top:
            return False  # 全集不是任何真子集的子集
        
        # 检查边界条件
        min_cond = (other.min_val is None) or (self.min_val is not None and self.min_val >= other.min_val)
        max_cond = (other.max_val is None) or (self.max_val is not None and self.max_val <= other.max_val)
        return min_cond and max_cond

class DeFiRangeAnalyzer:
    """
    增强的DeFi区间分析器
    
    该分析器专注于DeFi智能合约中的数值变量分析，
    通过抽象解释的方法推断变量可能的取值范围。
    
    特点：
    1. 针对DeFi特定约束进行验证
    2. 使用工作列表算法实现路径敏感分析 
    3. 支持加宽/收窄操作以平衡性能和精度
    """
    
    def __init__(self, compilation_unit):
        """
        初始化区间分析器
        
        Args:
            compilation_unit: Slither编译单元对象，包含合约和函数信息
        """
        # Slither编译单元
        self.compilation_unit = compilation_unit
        # DeFi特定约束
        self._deFi_constraints = self._load_deFi_constraints()
        # 变量区间映射 {variable: Interval}
        self._tracked_vars = {}
        # 函数分析摘要 {function: {parameter: Interval, return: Interval}}
        self._function_summaries = {}
        # 潜在问题列表
        self._potential_issues = []
        
        # 分析参数配置
        self._widening_threshold = 3  # 加宽操作阈值：达到此迭代次数后开始应用加宽
        self._narrowing_iterations = 2  # 收窄迭代次数：在分析结束后精化的迭代次数
        self._max_iterations = 20  # 最大迭代次数：防止无限循环
        self._worklist_batch_size = 5  # 工作列表批处理大小：每次从工作列表取出的节点数
    
    def _load_deFi_constraints(self):
        """
        加载DeFi特定约束
        
        为常见的DeFi变量类型定义合理的取值范围约束，
        用于后续检测值是否在合理范围内
        
        Returns:
            dict: DeFi约束字典，格式为 {约束名: {min: 最小值, max: 最大值}}
        """
        # 扩展更多DeFi相关的约束
        return {
            "token_balance": {"min": 0, "max": 2**256 - 1},
            "price_oracle": {"min": 0, "max": 10**36},  # 支持更大的价格范围
            "leverage_ratio": {"min": 1, "max": 100},
            "fee": {"min": 0, "max": 10**18},  # 费用比例
            "liquidity": {"min": 0, "max": 2**256 - 1},
            "time_lock": {"min": 0, "max": 2**64 - 1},  # 时间锁定
            "slippage": {"min": 0, "max": 10**18},
            "apy": {"min": 0, "max": 10**20},  # 年化收益率
            "interest_rate": {"min": 0, "max": 10**20},  # 利率
            "collateral_ratio": {"min": 0, "max": 10**20}  # 抵押率
        }
    
    def _is_deFi_critical(self, variable):
        """
        增强的DeFi关键变量识别
        
        识别DeFi应用中关键的数值变量，以便进行重点跟踪
        
        Args:
            variable: 需要检查的变量
            
        Returns:
            bool: 如果变量是DeFi关键变量则返回True
        """
        # DeFi相关的关键词模式
        patterns = [
            # 通用的DeFi领域词汇
            "balance", "price", "ratio", "debt", "supply", "reserve", 
            "liquidity", "amount", "fee", "rate", "swap", "pool", 
            "collateral", "token", "share", "yield", "reward",
            # 更专业的DeFi词汇
            "slippage", "impermanent", "apy", "tvl", "borrow", "lend",
            "stake", "unstake", "mint", "burn", "redeem", "oracle",
            "margin", "leverage", "flash", "loan", "liquidat"
        ]
        
        # DeFi接口类型模式
        defi_interface_patterns = [
            # ERC标准接口
            "erc20", "erc721", "erc1155", "ierc20", "ierc721", "ierc1155",
            # DEX接口
            "uniswap", "sushiswap", "pancakeswap", "balancer", "curve",
            "pair", "router", "factory", "amm", "dex",
            # 借贷平台接口
            "compound", "aave", "makerdao", "cream", "lending", "ctoken",
            "vault", "pool", "strategy", "yearn", "harvest",
            # 预言机接口
            "chainlink", "oracle", "price", "feed"
        ]
        
        # 变量名称检查
        var_name = str(variable).lower()
        if any(p in var_name for p in patterns):
            return True
        
        # 类型检查
        if hasattr(variable, "type"):
            type_str = str(variable.type).lower()
            
            # 检查是否为DeFi接口类型
            if any(pattern in type_str for pattern in defi_interface_patterns):
                return True
                
            # 数值类型
            if "uint" in type_str or "int" in type_str:
                return True
            # 对地址类型也进行跟踪（可能是token地址）
            if "address" in type_str:
                return True
        
        return False
    
    def _is_defi_contract(self, contract):
        """
        识别DeFi合约
        
        通过合约名称和函数名称判断是否为DeFi相关合约
        
        Args:
            contract: Slither合约对象
            
        Returns:
            bool: 如果合约可能是DeFi合约则返回True
        """
        defi_patterns = [
            # 函数模式
            "swap", "borrow", "lend", "stake", "deposit", "withdraw", "mint", "burn",
            "redeem", "claim", "liquidate", "flash", "provide", "purchase", "sell",
            # 合约名称模式
            "dex", "pool", "amm", "vault", "yield", "farm", "lending", "staking",
            "oracle", "router", "factory", "exchange", "pair", "token", "erc20", "erc721"
        ]
        
        # 检查合约名称
        contract_name = contract.name.lower()
        if any(pattern in contract_name for pattern in defi_patterns):
            return True
        
        # 检查函数名称
        for function in contract.functions:
            function_name = function.name.lower()
            if any(pattern in function_name for pattern in defi_patterns):
                return True
                
        # 检查基础合约
        for base in contract.inheritance:
            base_name = base.name.lower()
            if any(pattern in base_name for pattern in defi_patterns):
                return True
        
        # 检查状态变量名称
        for var in contract.state_variables:
            var_name = var.name.lower()
            if any(pattern in var_name for pattern in defi_patterns):
                return True
                
        # 检查接口遵循情况（如果合约实现了ERC20/ERC721等接口）
        if hasattr(contract, "is_erc20"):
            if contract.is_erc20():
                return True
                
        if hasattr(contract, "is_erc721"):
            if contract.is_erc721():
                return True
        
        # 检查常见DeFi函数组合
        defi_function_count = 0
        critical_functions = ["transfer", "approve", "transferFrom", 
                              "balanceOf", "totalSupply", "allowance"]
        
        for function in contract.functions:
            if function.name in critical_functions:
                defi_function_count += 1
        
        # 如果合约实现了多个ERC20关键函数，认为它是DeFi相关
        if defi_function_count >= 3:
            return True
        
        return False
    
    def _snapshot_state(self):
        """
        创建状态快照用于变化检测
        
        用于工作列表算法中比较两次迭代间的状态变化
        
        Returns:
            dict: 当前跟踪变量的区间映射的副本
        """
        return copy.deepcopy(self._tracked_vars)
    
    def _state_changed(self, old_state, threshold=0.01):
        """
        检测区间状态是否变化，带有阈值
        
        判断两次迭代之间变量区间是否发生足够大的变化，
        以决定是否需要继续迭代
        
        Args:
            old_state: 上一轮迭代的状态快照
            threshold: 判断状态变化的最小阈值
            
        Returns:
            bool: 如果状态发生足够大的变化则返回True
        """
        # 检查是否有新变量加入跟踪
        for var in self._tracked_vars:
            if var not in old_state:
                return True
            
            old_interval = old_state[var]
            new_interval = self._tracked_vars[var]
            
            # 检查区间类型变化
            if old_interval.is_bottom != new_interval.is_bottom or old_interval.is_top != new_interval.is_top:
                return True
            
            # 检查下界变化
            if (old_interval.min_val is not None and new_interval.min_val is not None and 
                abs(old_interval.min_val - new_interval.min_val) > threshold):
                return True
            
            # 检查上界变化
            if (old_interval.max_val is not None and new_interval.max_val is not None and 
                abs(old_interval.max_val - new_interval.max_val) > threshold):
                return True
            
            # 检查上下界从有限变为无限或相反
            if (old_interval.min_val is None) != (new_interval.min_val is None):
                return True
            if (old_interval.max_val is None) != (new_interval.max_val is None):
                return True
        
        return False
    
    def _process_ir(self, ir):
        """
        统一处理IR指令
        
        处理Slither的中间表示指令，更新变量的区间
        
        Args:
            ir: Slither中间表示指令
        """
        # 根据IR类型调用对应的处理方法
        if isinstance(ir, Binary):
            self._handle_binary_op(ir)
        elif isinstance(ir, Assignment):
            self._handle_assignment(ir)
        elif isinstance(ir, TypeConversion):
            self._handle_type_conversion(ir)
        elif isinstance(ir, Member):
            self._handle_member(ir)
        elif isinstance(ir, SolidityCall):
            self._handle_solidity_call(ir)
        # 增加对函数调用的处理
        elif hasattr(ir, "function") and hasattr(ir, "lvalue") and hasattr(ir, "arguments"):
            self._handle_function_call(ir)
        # 其他类型的IR可以在这里扩展
    
    def _handle_assignment(self, ir):
        """
        处理赋值操作
        
        处理形如 x = y 的赋值操作，其中y可能是常量或变量
        
        Args:
            ir: 赋值操作的IR表示
        """
        target = ir.lvalue
        
        # 常量赋值处理
        if isinstance(ir.rvalue, Constant):
            value = ir.rvalue.value
            # 处理数字字符串
            if isinstance(value, str) and value.isdigit():
                value = int(value)
            # 处理十六进制字符串
            elif isinstance(value, str):
                try:
                    value = int(value, 16) if value.startswith("0x") else int(value)
                except ValueError:
                    # 不能解析为整数的字符串
                    return
            
            # 如果值是整数，创建精确的区间 [value, value]
            if isinstance(value, int):
                self._tracked_vars[target] = Interval(value, value)
        
        # 变量赋值处理
        elif ir.rvalue in self._tracked_vars:
            # 复制右值的区间给左值
            self._tracked_vars[target] = copy.deepcopy(self._tracked_vars[ir.rvalue])
        
        # 特殊类型处理
        elif hasattr(ir.rvalue, "type"):
            type_str = str(ir.rvalue.type).lower()
            
            # 地址类型处理
            if "address" in type_str:
                # 地址可以表示为一个特定区间：[0, 2^160-1]
                self._tracked_vars[target] = Interval(0, 2**160 - 1)
            
            # 布尔类型处理
            elif "bool" in type_str:
                # 布尔值是0或1
                self._tracked_vars[target] = Interval(0, 1)
    
    def _handle_type_conversion(self, ir):
        """
        处理类型转换
        
        处理形如 x = type(y) 的类型转换操作
        
        Args:
            ir: 类型转换的IR表示
        """
        target = ir.lvalue
        source = ir.variable
        
        # 如果源变量有跟踪区间
        if source in self._tracked_vars:
            current_interval = self._tracked_vars[source]
            
            # 判断目标类型
            if hasattr(target, "type"):
                type_str = str(target.type).lower()
                
                # 根据目标类型调整区间
                if "uint" in type_str:
                    # 提取位宽
                    bits = int(re.search(r"uint(\d+)", type_str).group(1)) if re.search(r"uint(\d+)", type_str) else 256
                    # 无符号整数：[0, 2^bits-1]
                    new_min = max(0, current_interval.min_val) if current_interval.min_val is not None else 0
                    new_max = min(2**bits - 1, current_interval.max_val) if current_interval.max_val is not None else 2**bits - 1
                    self._tracked_vars[target] = Interval(new_min, new_max)
                
                elif "int" in type_str:
                    # 提取位宽
                    bits = int(re.search(r"int(\d+)", type_str).group(1)) if re.search(r"int(\d+)", type_str) else 256
                    # 有符号整数：[-2^(bits-1), 2^(bits-1)-1]
                    new_min = max(-(2**(bits-1)), current_interval.min_val) if current_interval.min_val is not None else -(2**(bits-1))
                    new_max = min(2**(bits-1) - 1, current_interval.max_val) if current_interval.max_val is not None else 2**(bits-1) - 1
                    self._tracked_vars[target] = Interval(new_min, new_max)
                
                elif "address" in type_str:
                    # 转换为地址类型
                    self._tracked_vars[target] = Interval(0, 2**160 - 1)
                
                elif "bool" in type_str:
                    # 转换为布尔类型：非零值转为1，零值转为0
                    if current_interval.min_val is not None and current_interval.min_val > 0:
                        # 如果最小值大于0，则结果肯定是true(1)
                        self._tracked_vars[target] = Interval(1, 1)
                    elif current_interval.max_val is not None and current_interval.max_val <= 0:
                        # 如果最大值小于等于0，则结果肯定是false(0)
                        self._tracked_vars[target] = Interval(0, 0)
                    else:
                        # 其他情况可能是true或false
                        self._tracked_vars[target] = Interval(0, 1)
    
    def _handle_member(self, ir):
        """
        处理成员访问
        
        处理形如 x = a.b 的成员访问操作，特别处理Solidity的全局变量
        
        Args:
            ir: 成员访问的IR表示
        """
        # 特殊处理 msg.value, block.timestamp, block.number 等常见成员
        if hasattr(ir, "variable_left") and hasattr(ir, "variable_right"):
            left = str(ir.variable_left).lower()
            right = str(ir.variable_right).lower()
            
            if left == "msg" and right == "value":
                # msg.value 是一个非负整数，表示交易附带的以太币数量
                self._tracked_vars[ir.lvalue] = Interval(0, 2**256 - 1)
            
            elif left == "block" and right == "timestamp":
                # block.timestamp 是当前区块的时间戳（秒级）
                # 使用一个合理的上限值，比如到2100年的秒数
                self._tracked_vars[ir.lvalue] = Interval(0, 4102444800)  # 到2100年的Unix时间戳
            
            elif left == "block" and right == "number":
                # block.number 是当前区块号
                # 假设区块号不会超过2^64-1
                self._tracked_vars[ir.lvalue] = Interval(0, 2**64 - 1)
            
            elif left == "tx" and right == "gasprice":
                # tx.gasprice 是gas价格
                # 使用一个合理的gas价格范围
                self._tracked_vars[ir.lvalue] = Interval(0, 10**18)  # 最大1 Ether/gas
            
            elif right == "balance":
                # address.balance 是账户余额
                self._tracked_vars[ir.lvalue] = Interval(0, 2**256 - 1)
    
    def _handle_solidity_call(self, ir):
        """
        处理Solidity内置函数调用
        
        处理Solidity的内置函数，如数学函数、加密函数等
        
        Args:
            ir: Solidity调用的IR表示
        """
        # 处理 SafeMath 相关操作和其他数学函数
        if hasattr(ir, "function") and hasattr(ir, "arguments"):
            function_name = ir.function.name.lower()
            
            # 检查是否是SafeMath库调用
            is_safemath_call = False
            if hasattr(ir.function, "contract"):
                contract_name = str(ir.function.contract.name).lower()
                # 检查合约名称是否暗示这是SafeMath库
                if "safemath" in contract_name or "math" in contract_name:
                    is_safemath_call = True
            
            # 处理数学运算函数
            if function_name in ["add", "sub", "mul", "div", "mod"]:
                # 获取参数区间
                arg_intervals = []
                for arg in ir.arguments:
                    if arg in self._tracked_vars:
                        arg_intervals.append(self._tracked_vars[arg])
                    elif isinstance(arg, Constant) and isinstance(arg.value, int):
                        arg_intervals.append(Interval(arg.value, arg.value))
                    else:
                        # 参数不在跟踪范围内，无法进行精确分析
                        return
                
                # 确保有足够的参数
                if len(arg_intervals) >= 2:
                    # 应用二元操作
                    result_interval = self._apply_binary_operation(function_name, arg_intervals[0], arg_intervals[1])
                    self._tracked_vars[ir.lvalue] = result_interval
                    
                    # 如果是SafeMath调用，记录此变量为SafeMath处理过，后续跳过溢出检查
                    if is_safemath_call and hasattr(ir, "lvalue"):
                        # 使用属性标记变量是否经过SafeMath处理
                        if not hasattr(self, "_safemath_processed"):
                            self._safemath_processed = set()
                        self._safemath_processed.add(ir.lvalue)
            
            # 处理min/max函数
            elif function_name == "min":
                # min函数返回参数的最小值
                arg_intervals = []
                for arg in ir.arguments:
                    if arg in self._tracked_vars:
                        arg_intervals.append(self._tracked_vars[arg])
                    elif isinstance(arg, Constant) and isinstance(arg.value, int):
                        arg_intervals.append(Interval(arg.value, arg.value))
                
                if len(arg_intervals) >= 2:
                    # 取第一个参数区间的最小值和上限
                    min_val = arg_intervals[0].min_val
                    max_val = min(a.max_val for a in arg_intervals if a.max_val is not None)
                    self._tracked_vars[ir.lvalue] = Interval(min_val, max_val)
            
            elif function_name == "max":
                # max函数返回参数的最大值
                arg_intervals = []
                for arg in ir.arguments:
                    if arg in self._tracked_vars:
                        arg_intervals.append(self._tracked_vars[arg])
                    elif isinstance(arg, Constant) and isinstance(arg.value, int):
                        arg_intervals.append(Interval(arg.value, arg.value))
                
                if len(arg_intervals) >= 2:
                    # 取所有参数区间的最大值的最大值和下限的最大值
                    max_val = max(a.max_val for a in arg_intervals if a.max_val is not None)
                    min_val = max(a.min_val for a in arg_intervals if a.min_val is not None)
                    self._tracked_vars[ir.lvalue] = Interval(min_val, max_val)
    
    def _handle_function_call(self, ir):
        """
        处理函数调用
        
        处理一般函数调用的返回值区间，主要关注DeFi相关函数
        
        Args:
            ir: 函数调用的IR表示
        """
        function = ir.function
        target = ir.lvalue
        
        # 检查是否是已知的DeFi函数
        function_name = function.name.lower() if hasattr(function, "name") else ""
        
        # 检查函数名称是否暗示特定的返回区间
        if "balance" in function_name or "total" in function_name and "supply" in function_name:
            # 余额和总供应量通常是非负值
            self._tracked_vars[target] = Interval(0, 2**256 - 1)
        
        elif "price" in function_name or "rate" in function_name:
            # 价格和汇率通常是非负值，且有合理上限
            self._tracked_vars[target] = Interval(0, 10**36)
        
        elif "allowance" in function_name:
            # 授权额度是非负值
            self._tracked_vars[target] = Interval(0, 2**256 - 1)
        
        elif "decimals" in function_name:
            # 代币小数位通常在0-18之间
            self._tracked_vars[target] = Interval(0, 18)
        
        # 处理返回值为布尔类型的函数
        elif hasattr(function, "return_type") and function.return_type and "bool" in str(function.return_type).lower():
            self._tracked_vars[target] = Interval(0, 1)
        
        # 处理返回值为地址类型的函数
        elif hasattr(function, "return_type") and function.return_type and "address" in str(function.return_type).lower():
            self._tracked_vars[target] = Interval(0, 2**160 - 1)
        
        # 如果无法判断返回值区间，使用默认区间
        elif self._is_deFi_critical(target):
            # 如果是关键变量但无法确定区间，使用默认非负区间
            self._tracked_vars[target] = Interval(0, 2**256 - 1)
    
    def _handle_binary_op(self, ir):
        """
        处理二元运算符
        
        处理形如 x = a op b 的二元运算，如加减乘除、比较等
        
        Args:
            ir: 二元操作的IR表示
        """
        op_type = ir.type_str
        result_var = ir.lvalue
        left = ir.variable_left
        right = ir.variable_right
        
        # 获取操作数区间
        left_interval = self._tracked_vars.get(left, Interval())
        right_interval = self._tracked_vars.get(right, Interval())
        
        # 处理常量右操作数
        if isinstance(right, Constant) and right not in self._tracked_vars:
            value = right.value
            if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
                value = int(value) if isinstance(value, int) else int(value)
                right_interval = Interval(value, value)
            elif isinstance(value, str) and value.startswith("0x"):
                try:
                    value = int(value, 16)
                    right_interval = Interval(value, value)
                except ValueError:
                    pass
        
        # 处理常量左操作数
        if isinstance(left, Constant) and left not in self._tracked_vars:
            value = left.value
            if isinstance(value, int) or (isinstance(value, str) and value.isdigit()):
                value = int(value) if isinstance(value, int) else int(value)
                left_interval = Interval(value, value)
            elif isinstance(value, str) and value.startswith("0x"):
                try:
                    value = int(value, 16)
                    left_interval = Interval(value, value)
                except ValueError:
                    pass
        
        # 使用通用方法计算结果区间
        result_interval = self._apply_binary_operation(op_type, left_interval, right_interval)
        self._tracked_vars[result_var] = result_interval
        
        # 检查潜在问题
        # 检查溢出/下溢
        if op_type in ["+", "-", "*", "**"]:
            self._check_overflow_underflow(op_type, left_interval, right_interval, result_var)
        
        # 检查除零
        if op_type in ["/", "%"]:
            self._check_division_by_zero(right_interval, result_var, left)
    
    def _apply_binary_operation(self, op_type, left_interval, right_interval):
        """
        应用二元操作到区间
        
        根据操作类型计算两个区间的运算结果区间。
        例如，对于加法 [a,b] + [c,d] = [a+c, b+d]
        
        Args:
            op_type: 操作符类型，如 "+", "-", "*", "/", 等
            left_interval: 左操作数区间
            right_interval: 右操作数区间
            
        Returns:
            Interval: 根据操作类型计算的结果区间
        """
        # 如果任一操作数为空区间，结果也为空
        if left_interval.is_bottom or right_interval.is_bottom:
            return Interval()
        
        # 处理有一个操作数为top的情况
        if left_interval.is_top or right_interval.is_top:
            # 除法和取模特殊处理：如果除数可能为0，返回全范围
            if op_type in ["/", "%"] and right_interval.is_top:
                return Interval(0, 2**256 - 1)  # 全范围
            
            # 其他操作类型，结果为top
            return Interval(float('-inf'), float('inf'))
        
        # 确保有具体的边界值(可能为NULL)
        left_min = left_interval.min_val if left_interval.min_val is not None else float('-inf')
        left_max = left_interval.max_val if left_interval.max_val is not None else float('inf')
        right_min = right_interval.min_val if right_interval.min_val is not None else float('-inf')
        right_max = right_interval.max_val if right_interval.max_val is not None else float('inf')
        
        # 根据运算符计算结果区间
        if op_type == "+":
            # 加法: [a,b] + [c,d] = [a+c, b+d]
            new_min = left_min + right_min
            new_max = left_max + right_max
            
            # 处理溢出和无穷
            if new_min == float('-inf') or new_min < -(2**255):
                new_min = -(2**255)
            if new_max == float('inf') or new_max >= 2**256:
                new_max = 2**256 - 1
        
        elif op_type == "-":
            # 减法: [a,b] - [c,d] = [a-d, b-c]
            new_min = left_min - right_max
            new_max = left_max - right_min
            
            # 处理溢出和无穷
            if new_min == float('-inf') or new_min < -(2**255):
                new_min = -(2**255)
            if new_max == float('inf') or new_max >= 2**256:
                new_max = 2**256 - 1
        
        elif op_type == "*":
            # 乘法需要考虑所有组合: [a,b] * [c,d] = [min(ac,ad,bc,bd), max(ac,ad,bc,bd)]
            # 避免直接计算无穷，使用条件判断
            if left_min == float('-inf') or right_min == float('-inf') or left_max == float('inf') or right_max == float('inf'):
                # 如果有无穷参与，结果可能是无穷或很大的值
                # 这里简化处理，返回最大范围
                return Interval(-(2**255), 2**256 - 1)
            
            # 计算四种乘积组合
            products = [
                left_min * right_min,
                left_min * right_max,
                left_max * right_min,
                left_max * right_max
            ]
            new_min = min(products)
            new_max = max(products)
            
            # 处理溢出
            if new_min < -(2**255):
                new_min = -(2**255)
            if new_max >= 2**256:
                new_max = 2**256 - 1
        
        elif op_type == "/":
            # 更严格的除零检查
            if right_min <= 0 and right_max >= 0:
                # 除数区间包含0，这是一个高置信度的除零风险
                # 不是 [0,0]（即不是确定的0），而是区间中包含0
                if not (right_min == 0 and right_max == 0):
                    # 记录潜在问题
                    self._potential_issues.append(f"确定性除零风险: 除数区间 {right_interval} 包含0")
                    # 返回完整范围，表示不确定的结果
                    return Interval(-(2**255), 2**256 - 1)
                else:
                    # 除数确定是0，肯定会导致除零错误
                    self._potential_issues.append(f"确定性除零错误: 除数区间为 [0,0]")
                    return Interval(-(2**255), 2**256 - 1)
            
            # 避免直接计算无穷，使用条件判断
            if left_min == float('-inf') or right_min == float('-inf') or left_max == float('inf') or right_max == float('inf'):
                # 简化处理，根据符号确定范围
                if (right_min > 0 and left_min >= 0) or (right_max < 0 and left_max <= 0):
                    # 被除数和除数同号，结果为正
                    return Interval(0, 2**256 - 1)
                elif (right_min > 0 and left_max <= 0) or (right_max < 0 and left_min >= 0):
                    # 被除数和除数异号，结果为负
                    return Interval(-(2**255), 0)
                else:
                    # 复杂情况，返回全范围
                    return Interval(-(2**255), 2**256 - 1)
            
            # 处理有限区间的除法，需要考虑所有可能的组合
            quotients = []
            
            # 检查除数是否完全为正或完全为负（不跨零）
            is_divisor_positive = right_min > 0  # 除数完全为正
            is_divisor_negative = right_max < 0  # 除数完全为负
            
            # 如果除数区间不跨零，计算所有可能组合
            if is_divisor_positive or is_divisor_negative:
                # 考虑4种可能组合：min/min, min/max, max/min, max/max
                if is_divisor_positive:  # 除数为正
                    quotients.append(left_min // right_min)  # 最小值除以最小值
                    quotients.append(left_min // right_max)  # 最小值除以最大值
                    quotients.append(left_max // right_min)  # 最大值除以最小值
                    quotients.append(left_max // right_max)  # 最大值除以最大值
                else:  # 除数为负
                    quotients.append(left_min // right_max)  # 最小值除以最大值(负数)
                    quotients.append(left_min // right_min)  # 最小值除以最小值(负数)
                    quotients.append(left_max // right_max)  # 最大值除以最大值(负数)
                    quotients.append(left_max // right_min)  # 最大值除以最小值(负数)
                
                # 处理特殊情况：除数接近于0时的极端结果
                if abs(right_min) < 2 or abs(right_max) < 2:
                    if left_min < 0:
                        quotients.append(-(2**255))  # 可能的极大负值
                    if left_max > 0:
                        quotients.append(2**256 - 1)  # 可能的极大正值
            
            if not quotients:
                return Interval(-(2**255), 2**256 - 1)  # 无法确定范围，返回全范围
            
            new_min = max(-(2**255), min(quotients))
            new_max = min(2**256 - 1, max(quotients))
        
        elif op_type == "%":
            # 更严格的除零检查
            if right_min <= 0 and right_max >= 0:
                # 除数区间包含0，这是一个高置信度的除零风险
                if not (right_min == 0 and right_max == 0):
                    self._potential_issues.append(f"确定性除零风险: 模运算除数区间 {right_interval} 包含0")
                else:
                    self._potential_issues.append(f"确定性除零错误: 模运算除数区间为 [0,0]")
                return Interval(0, 2**256 - 1)  # 全范围
            
            # 处理除数区间不包含零的情况
            # 取模结果的绝对值总是小于除数的绝对值
            
            # 计算除数的最大绝对值
            abs_right_max = max(abs(right_min), abs(right_max))
            
            # 根据除数符号和被除数符号确定结果范围
            # 如果除数全部为正
            if right_min > 0:
                if left_min >= 0:  # 被除数全部为正
                    new_min = 0
                    new_max = min(left_max, right_max - 1)
                elif left_max < 0:  # 被除数全部为负
                    # 在Solidity中，对负数取模结果可能是负的
                    new_min = max(-(right_max - 1), left_min)
                    new_max = 0
                else:  # 被除数跨零
                    new_min = -(right_max - 1)
                    new_max = right_max - 1
            # 如果除数全部为负
            elif right_max < 0:
                abs_right_min = abs(right_max)  # 负数的绝对值
                if left_min >= 0:  # 被除数全部为正
                    new_min = 0
                    new_max = min(left_max, abs_right_min - 1)
                elif left_max < 0:  # 被除数全部为负
                    new_min = max(-abs_right_min + 1, left_min)
                    new_max = 0
                else:  # 被除数跨零
                    new_min = -abs_right_min + 1
                    new_max = abs_right_min - 1
            else:
                # 这种情况不应该发生（之前的除零检查已排除除数跨零的情况）
                return Interval(0, 2**256 - 1)  # 保守返回全范围
        
        elif op_type == "**":
            # 幂运算需要考虑底数和指数的符号
            
            # 特殊情况：底数为0或1，或指数为0或1
            if (left_min == 0 and left_max == 0):
                # 0的任何次方(除0外)都是0
                if right_min > 0:
                    return Interval(0, 0)
                # 0的0次方按惯例为1
                if right_min == 0 and right_max == 0:
                    return Interval(1, 1)
                # 0的负次方未定义，但保守返回全范围
                return Interval(0, 2**256 - 1)
            
            if (left_min == 1 and left_max == 1):
                # 1的任何次方都是1
                return Interval(1, 1)
            
            if (right_min == 0 and right_max == 0):
                # 任何数(除0外)的0次方都是1
                return Interval(1, 1)
            
            if (right_min == 1 and right_max == 1):
                # 任何数的1次方是它自己
                return left_interval
            
            # 计算幂运算的各种组合
            powers = []
            
            # 只处理实际可计算的情况，避免溢出错误
            for l in [left_min, left_max]:
                if l != float('-inf') and l != float('inf'):
                    for r in [right_min, right_max]:
                        if r != float('-inf') and r != float('inf'):
                            # 处理特定情况
                            if l >= 0 and r >= 0:  # 正底数的正次方
                                try:
                                    powers.append(int(l ** r))
                                except (OverflowError, ValueError):
                                    powers.append(2**256 - 1)  # 溢出时取最大值
                            elif l > 0 and r < 0:  # 正底数的负次方
                                try:
                                    # 正数的负次方总是正分数，向下取整为0或1
                                    if l == 1:
                                        powers.append(1)  # 1的任何次方都是1
                                    else:
                                        powers.append(0)  # 其他正数的负次方向下取整为0
                                except (OverflowError, ValueError):
                                    powers.append(0)
                            elif l < 0 and r >= 0 and r % 2 == 0:  # 负底数的偶数次方
                                try:
                                    powers.append(int(abs(l) ** r))
                                except (OverflowError, ValueError):
                                    powers.append(2**256 - 1)
                            elif l < 0 and r >= 0 and r % 2 == 1:  # 负底数的奇数次方
                                try:
                                    powers.append(-int(abs(l) ** r))
                                except (OverflowError, ValueError):
                                    powers.append(-(2**255))
                            # 负底数的负次方在整数区间中处理较复杂，谨慎处理
            
            if not powers:
                # 如果没有有效计算值，返回保守区间
                return Interval(-(2**255), 2**256 - 1)
            
            new_min = max(-(2**255), min(powers))
            new_max = min(2**256 - 1, max(powers))
        
        elif op_type in ["<", "<=", ">", ">=", "==", "!="]:
            # 比较运算返回布尔值 (0或1)
            return Interval(0, 1)
        
        elif op_type in ["&&", "||", "and", "or"]:
            # 逻辑运算返回布尔值 (0或1)
            return Interval(0, 1)
        
        elif op_type in ["<<", ">>"]:
            # 移位操作
            if op_type == "<<":
                # 左移：x << y 相当于 x * 2^y，可能溢出
                if right_max < 0:
                    # 负向左移等价于右移
                    new_min = left_min >> abs(right_max) if left_min != float('-inf') else 0
                    new_max = left_max >> abs(right_min) if left_max != float('inf') else 0
                else:
                    # 限制最大移位位数以避免溢出
                    max_shift = min(right_max, 256) if right_max != float('inf') else 256
                    
                    # 左移操作对左区间边界的影响
                    if left_min == float('-inf'):
                        new_min = -(2**255)  # 负无穷左移仍是最小值
                    elif left_min < 0:
                        # 负数左移可能溢出为正或仍为负
                        if left_min < -(2**(255-max_shift)):
                            new_min = -(2**255)  # 溢出到最小值
                        else:
                            new_min = left_min << (int(right_min) if right_min != float('-inf') else 0)
                    else:
                        new_min = left_min << (int(right_min) if right_min != float('-inf') else 0)
                    
                    # 左移操作对右区间边界的影响
                    if left_max == float('inf'):
                        new_max = 2**256 - 1  # 正无穷左移仍是最大值
                    elif left_max > 0 and max_shift > 0:
                        # 正数左移可能溢出
                        if left_max > (2**256 - 1) >> max_shift:
                            new_max = 2**256 - 1  # 溢出到最大值
                        else:
                            new_max = left_max << (int(right_min) if right_min != float('-inf') else 0)
                    else:
                        new_max = left_max << (int(right_min) if right_min != float('-inf') else 0)
                    
                    # 防止溢出
                    if new_min < -(2**255):
                        new_min = -(2**255)
                    if new_max >= 2**256:
                        new_max = 2**256 - 1
            else:
                # 右移：x >> y 相当于 x / 2^y，向下取整
                if right_max < 0:
                    # 负向右移等价于左移
                    # 防止移位过大导致溢出
                    max_shift = min(abs(right_min), 256) if right_min != float('-inf') else 256
                    
                    # 如果左移位数过大可能导致溢出
                    if max_shift > 30:  # 移位超过30位可能溢出
                        new_min = -(2**255)
                        new_max = 2**256 - 1
                    else:
                        new_min = left_min << abs(right_max) if left_min != float('-inf') else -(2**255)
                        new_max = left_max << abs(right_min) if left_max != float('inf') else 2**256 - 1
                        
                        # 防止溢出
                        if new_min < -(2**255):
                            new_min = -(2**255)
                        if new_max >= 2**256:
                            new_max = 2**256 - 1
                else:
                    # 正常右移
                    if left_min == float('-inf'):
                        new_min = -(2**255)  # 负无穷右移仍是最小值
                    else:
                        new_min = left_min >> (int(right_max) if right_max != float('inf') else 256)
                    
                    if left_max == float('inf'):
                        new_max = 2**256 - 1  # 正无穷右移可能仍很大
                    else:
                        new_max = left_max >> (int(right_min) if right_min != float('-inf') else 0)
        
        else:
            # 未知操作符，返回保守的全范围
            return Interval(-(2**255), 2**256 - 1)
        
        # 检查上下界是否为无穷，将其替换为有限区间
        if new_min == float('-inf'):
            new_min = -(2**255)
        if new_max == float('inf'):
            new_max = 2**256 - 1
        
        # 返回计算结果的区间
        return Interval(new_min, new_max)
    
    def _check_overflow_underflow(self, op_type, left_interval, right_interval, result_var):
        """
        检查潜在的溢出/下溢
        
        分析二元操作可能导致的溢出或下溢情况
        
        Args:
            op_type: 操作符类型
            left_interval: 左操作数区间
            right_interval: 右操作数区间
            result_var: 结果变量
        """
        # 如果变量是通过SafeMath处理的，跳过溢出检查
        if hasattr(self, "_safemath_processed") and result_var in self._safemath_processed:
            return
            
        issue = None
        
        if op_type == "+":
            # 检查加法溢出
            if (left_interval.max_val is not None and right_interval.max_val is not None and 
                left_interval.max_val + right_interval.max_val >= 2**256):
                issue = f"潜在加法溢出: {result_var} = {left_interval} + {right_interval}"
        
        elif op_type == "-":
            # 检查减法下溢
            if (left_interval.min_val is not None and right_interval.max_val is not None and 
                left_interval.min_val < right_interval.max_val):
                # 检查变量类型是否为无符号整数
                if hasattr(result_var, "type") and "uint" in str(result_var.type).lower():
                    issue = f"潜在减法下溢: {result_var} = {left_interval} - {right_interval}"
        
        elif op_type == "*":
            # 检查乘法溢出
            if (left_interval.max_val is not None and right_interval.max_val is not None and 
                left_interval.max_val * right_interval.max_val >= 2**256):
                issue = f"潜在乘法溢出: {result_var} = {left_interval} * {right_interval}"
        
        elif op_type == "**":
            # 检查幂运算溢出
            if (left_interval.max_val is not None and right_interval.max_val is not None and 
                left_interval.max_val > 1 and right_interval.max_val > 1):
                # 简单估计：如果底数>1且指数>32，基本肯定会溢出
                if right_interval.max_val > 32:
                    issue = f"潜在幂运算溢出: {result_var} = {left_interval} ** {right_interval}"
        
        if issue:
            self._potential_issues.append(issue)
    
    def _check_division_by_zero(self, right_interval, result_var, left_var):
        """
        检查除零错误
        
        检查除法操作中的除数是否可能为零
        
        Args:
            right_interval: 除数的区间
            result_var: 结果变量
            left_var: 被除数变量
        """
        if right_interval.min_val is not None and right_interval.max_val is not None:
            if right_interval.min_val <= 0 and right_interval.max_val >= 0:
                self._potential_issues.append(f"潜在除零错误: {result_var} = {left_var} / [包含0的区间 {right_interval}]")
    
    def _analyze_function_worklist(self, function):
        """
        使用优化的工作列表算法实现函数级分析
        
        工作列表算法是一种数据流分析技术，用于迭代计算程序点的不动点。
        此实现进行了多项优化:
        1. 批处理节点以减少迭代次数
        2. 智能状态变化检测以避免不必要的重新计算
        3. 使用加宽/收窄操作平衡性能和精度
        
        Args:
            function: 要分析的函数
        """
        # 初始化变量范围
        self._tracked_vars = {}  # 重置跟踪变量
        
        # 为参数初始化区间
        for param in function.parameters:
            if self._is_deFi_critical(param):
                # 根据参数类型推断初始区间
                if hasattr(param, "type"):
                    type_str = str(param.type).lower()
                    if "uint" in type_str:
                        bits = int(re.search(r"uint(\d+)", type_str).group(1)) if re.search(r"uint(\d+)", type_str) else 256
                        self._tracked_vars[param] = Interval(0, 2**bits - 1)
                    elif "int" in type_str:
                        bits = int(re.search(r"int(\d+)", type_str).group(1)) if re.search(r"int(\d+)", type_str) else 256
                        self._tracked_vars[param] = Interval(-(2**(bits-1)), 2**(bits-1) - 1)
                    elif "address" in type_str:
                        self._tracked_vars[param] = Interval(0, 2**160 - 1)
                    elif "bool" in type_str:
                        self._tracked_vars[param] = Interval(0, 1)
                    else:
                        self._tracked_vars[param] = Interval(0, 2**256 - 1)
                else:
                    self._tracked_vars[param] = Interval(0, 2**256 - 1)
        
        # 预处理：收集所有变量并进行分类
        local_vars = set()
        temp_vars = set()
        state_vars = set()
        ref_vars = set() 
        
        # 遍历函数中的所有节点和IR
        for node in function.nodes:
            for ir in node.irs:
                # 收集左值变量
                if hasattr(ir, "lvalue"):
                    var = ir.lvalue
                    if isinstance(var, LocalVariable):
                        local_vars.add(var)
                    elif isinstance(var, TemporaryVariable):
                        temp_vars.add(var)
                    elif isinstance(var, StateVariable):
                        state_vars.add(var)
                    elif isinstance(var, ReferenceVariable):
                        ref_vars.add(var)
                
                # 收集右值变量(可选)
                if hasattr(ir, "rvalue") and ir.rvalue not in self._tracked_vars:
                    var = ir.rvalue
                    if isinstance(var, StateVariable) and self._is_deFi_critical(var):
                        # 为未初始化的关键状态变量设置初始区间
                        if hasattr(var, "type"):
                            type_str = str(var.type).lower()
                            if "uint" in type_str:
                                self._tracked_vars[var] = Interval(0, 2**256 - 1)
                            elif "int" in type_str:
                                self._tracked_vars[var] = Interval(-(2**255), 2**255 - 1)
        
        # 为关键局部变量初始化区间
        for var in local_vars.union(temp_vars):
            if self._is_deFi_critical(var):
                if var not in self._tracked_vars:  # 避免覆盖已有区间
                    if hasattr(var, "type"):
                        type_str = str(var.type).lower()
                        if "uint" in type_str:
                            self._tracked_vars[var] = Interval(0, 2**256 - 1)
                        elif "int" in type_str:
                            self._tracked_vars[var] = Interval(-(2**255), 2**255 - 1)
                        elif "bool" in type_str:
                            self._tracked_vars[var] = Interval(0, 1)
                        else:
                            self._tracked_vars[var] = Interval(0, 2**256 - 1)
                    else:
                        self._tracked_vars[var] = Interval(0, 2**256 - 1)
        
        # 优化的工作列表算法
        # 使用双端队列以支持高效的头尾操作
        worklist = deque(function.nodes)
        processed = set()  # 跟踪已处理过的节点
        iteration = 0
        
        # 跟踪迭代状态，用于判断是否使用加宽
        iteration_states = {}  # 记录每个节点的状态历史 {node: [state1, state2, ...]}
        
        # 迭代直到收敛或达到最大迭代次数
        while worklist and iteration < self._max_iterations:
            # 批处理节点以减少迭代次数
            batch_size = min(self._worklist_batch_size, len(worklist))
            batch_nodes = [worklist.popleft() for _ in range(batch_size)]
            
            for node in batch_nodes:
                # 记录处理前的状态
                old_state = self._snapshot_state()
                
                # 记录当前节点的状态历史
                if node not in iteration_states:
                    iteration_states[node] = []
                iteration_states[node].append(old_state)
                
                # 处理条件分支
                if node.contains_if():
                    self._process_condition(node)
                
                # 处理IR指令
                for ir in node.irs:
                    self._process_ir(ir)
                
                # 判断是否应用加宽操作
                should_widen = len(iteration_states[node]) >= self._widening_threshold
                
                # 应用加宽操作以加速收敛
                if should_widen:
                    for var in self._tracked_vars:
                        if var in old_state:
                            # 应用加宽操作：将当前值与旧值进行加宽
                            self._tracked_vars[var] = old_state[var].widen(self._tracked_vars[var])
                
                # 状态变化检测：如果状态发生变化，添加后继节点到工作列表
                if self._state_changed(old_state):
                    for son in node.sons:
                        if son not in processed or son in worklist:
                            # 只有当后继节点尚未处理或已经在工作列表中时才添加
                            # 避免不必要地重复处理相同节点
                            worklist.append(son)
                
                # 标记节点为已处理
                processed.add(node)
            
            iteration += 1
        
        # 应用收窄操作以提高精度
        # 收窄阶段通常在固定点达到后进行
        if self._narrowing_iterations > 0:
            # 定义固定的节点顺序以保证确定性
            nodes_in_order = list(function.nodes)
            
            for _ in range(self._narrowing_iterations):
                for node in nodes_in_order:
                    # 跳过没有历史状态的节点
                    if node not in iteration_states or not iteration_states[node]:
                        continue
                    
                    old_state = iteration_states[node][-1]  # 使用最后一个历史状态
                    current_state = self._snapshot_state()
                    
                    # 处理条件分支
                    if node.contains_if():
                        self._process_condition(node)
                    
                    # 处理IR指令
                    for ir in node.irs:
                        self._process_ir(ir)
                    
                    # 应用收窄操作
                    for var in self._tracked_vars:
                        if var in old_state:
                            # 应用收窄操作：将当前值与之前的最后一个状态进行收窄
                            self._tracked_vars[var] = self._tracked_vars[var].narrow(old_state[var])
        
        # 保存函数摘要
        self._function_summaries[function] = {
            "params": {param: self._tracked_vars.get(param, Interval()) for param in function.parameters},
            "return": {ret: self._tracked_vars.get(ret, Interval()) for ret in function.returns}
        }
    
    def _process_condition(self, node):
        """
        处理条件表达式细化区间
        
        通过分析条件表达式，精化条件中涉及的变量区间。
        例如，当遇到 `if x > 5` 时，可以推断在条件为真的分支中 x 属于区间 [6, max]
        
        Args:
            node: 包含条件表达式的节点
        """
        if hasattr(node, "expression") and isinstance(node.expression, Binary):
            left = node.expression.variable_left
            right = node.expression.variable_right
            op = node.expression.type_str
            
            # 处理常量比较 (如 x < 10)
            if isinstance(right, Constant):
                # 提取常量值
                threshold = right.value
                if isinstance(threshold, str):
                    try:
                        threshold = int(threshold, 16) if threshold.startswith("0x") else int(threshold)
                    except ValueError:
                        return
                
                if not isinstance(threshold, int):
                    return
                
                # 如果左操作数在跟踪范围内
                if left in self._tracked_vars:
                    current = self._tracked_vars[left]
                    
                    # 基于条件类型细化区间
                    if op == "<":
                        # x < threshold ==> x 在 [min, threshold-1]
                        new_interval = current.meet(Interval(None, threshold - 1))
                    elif op == "<=":
                        # x <= threshold ==> x 在 [min, threshold]
                        new_interval = current.meet(Interval(None, threshold))
                    elif op == ">":
                        # x > threshold ==> x 在 [threshold+1, max]
                        new_interval = current.meet(Interval(threshold + 1, None))
                    elif op == ">=":
                        # x >= threshold ==> x 在 [threshold, max]
                        new_interval = current.meet(Interval(threshold, None))
                    elif op == "==":
                        # x == threshold ==> x 在 [threshold, threshold]
                        new_interval = current.meet(Interval(threshold, threshold))
                    elif op == "!=":
                        # 不等于很难精确表示，但可以处理x!=0的特殊情况
                        if threshold == 0:
                            # x != 0 且 x 原来包含0，分割为 [-inf, -1] 和 [1, inf]
                            if current.min_val is not None and current.min_val <= 0 and current.max_val is not None and current.max_val >= 0:
                                # 创建两个子区间
                                neg_interval = Interval(current.min_val, -1) if current.min_val < 0 else None
                                pos_interval = Interval(1, current.max_val) if current.max_val > 0 else None
                                
                                # 合并子区间
                                if neg_interval and pos_interval:
                                    # 注意：这种处理可能导致精度损失
                                    new_interval = Interval(neg_interval.min_val, pos_interval.max_val)
                                elif neg_interval:
                                    new_interval = neg_interval
                                elif pos_interval:
                                    new_interval = pos_interval
                                else:
                                    # 不可能的情况，返回空区间
                                    new_interval = Interval()
                            else:
                                # x 不包含0，保持不变
                                new_interval = current
                        else:
                            # 一般情况下不处理，保留原有区间
                            new_interval = current
                    else:
                        return
                    
                    # 更新区间
                    if new_interval != current:
                        self._tracked_vars[left] = new_interval
            
            # 处理变量比较 (如 x < y)
            elif left in self._tracked_vars and right in self._tracked_vars:
                left_interval = self._tracked_vars[left]
                right_interval = self._tracked_vars[right]
                
                if op == "<":
                    # x < y ==> x 最大值不超过 y 的最大值-1
                    if right_interval.max_val is not None:
                        new_left = left_interval.meet(Interval(None, right_interval.max_val - 1))
                        self._tracked_vars[left] = new_left
                    # y > x ==> y 最小值不小于 x 的最小值+1
                    if left_interval.min_val is not None:
                        new_right = right_interval.meet(Interval(left_interval.min_val + 1, None))
                        self._tracked_vars[right] = new_right
                
                elif op == "<=":
                    # x <= y ==> x 最大值不超过 y 的最大值
                    if right_interval.max_val is not None:
                        new_left = left_interval.meet(Interval(None, right_interval.max_val))
                        self._tracked_vars[left] = new_left
                    # y >= x ==> y 最小值不小于 x 的最小值
                    if left_interval.min_val is not None:
                        new_right = right_interval.meet(Interval(left_interval.min_val, None))
                        self._tracked_vars[right] = new_right
                
                elif op == ">":
                    # x > y ==> x 最小值不小于 y 的最小值+1
                    if right_interval.min_val is not None:
                        new_left = left_interval.meet(Interval(right_interval.min_val + 1, None))
                        self._tracked_vars[left] = new_left
                    # y < x ==> y 最大值不超过 x 的最大值-1
                    if left_interval.max_val is not None:
                        new_right = right_interval.meet(Interval(None, left_interval.max_val - 1))
                        self._tracked_vars[right] = new_right
                
                elif op == ">=":
                    # x >= y ==> x 最小值不小于 y 的最小值
                    if right_interval.min_val is not None:
                        new_left = left_interval.meet(Interval(right_interval.min_val, None))
                        self._tracked_vars[left] = new_left
                    # y <= x ==> y 最大值不超过 x 的最大值
                    if left_interval.max_val is not None:
                        new_right = right_interval.meet(Interval(None, left_interval.max_val))
                        self._tracked_vars[right] = new_right
                
                elif op == "==":
                    # x == y ==> x 和 y 的区间相交
                    intersection = left_interval.meet(right_interval)
                    self._tracked_vars[left] = intersection
                    self._tracked_vars[right] = intersection
    
    def _check_bounds_violation(self, variable):
        """
        检查区间约束违规
        
        检查变量的区间是否违反了预定义的约束，
        如溢出、下溢或特定DeFi约束
        
        Args:
            variable: 需要检查的变量
            
        Returns:
            str or None: 如果发现违规则返回违规描述，否则返回None
        """
        if variable not in self._tracked_vars:
            return None
        
        current = self._tracked_vars[variable]
        if current.is_bottom:
            # 空区间可能表示不可达代码
            return None
        
        # 检查溢出风险
        if current.max_val is not None and current.max_val >= 2**256:
            return f"{variable} 可能溢出 (> 2^256)"
        
        # 检查下溢风险（对于可能是无符号整数的变量）
        if current.min_val is not None and current.min_val < 0:
            # 通过变量类型检查是否为无符号整数
            if hasattr(variable, "type") and "uint" in str(variable.type).lower():
                return f"{variable} 可能下溢 (< 0)"
        
        # 检查DeFi特定约束
        var_name = str(variable).lower()
        for constraint_name, constraint in self._deFi_constraints.items():
            if constraint_name in var_name:
                # 检查下限
                if current.min_val is not None and current.min_val < constraint["min"]:
                    return f"{variable} 最小值违规 ({current.min_val} < {constraint['min']})"
                # 检查上限
                if current.max_val is not None and current.max_val > constraint["max"]:
                    return f"{variable} 最大值违规 ({current.max_val} > {constraint['max']})"
        
        return None
    
    def analyze(self):
        """
        主分析入口
        
        执行整个分析过程，返回分析结果
        
        Returns:
            list: 分析结果列表，包含发现的所有违规
        """
        results = []
        
        # 逐合约分析
        for contract in self.compilation_unit.contracts_derived:
            # 只分析DeFi合约
            if not self._is_defi_contract(contract):
                continue
            
            # 按函数分析
            for function in contract.functions:
                # 跳过构造函数和外部调用
                if function.is_constructor or function.name == "slitherConstructorVariables":
                    continue
                
                # 执行区间分析
                self._analyze_function_worklist(function)
                
                # 收集违规信息
                for var in self._tracked_vars:
                    violation = self._check_bounds_violation(var)
                    if violation:
                        results.append({
                            "contract": contract.name,
                            "function": function.name,
                            "variable": str(var),
                            "violation": violation,
                            "interval": str(self._tracked_vars[var])
                        })
        
        # 处理潜在问题
        for issue in self._potential_issues:
            results.append({
                "issue": issue
            })
        
        # 返回分析结果
        return results
    
    def export_summary(self):
        """
        导出函数区间分析摘要
        
        生成所有分析过的函数的区间摘要，
        包括参数和返回值的区间
        
        Returns:
            dict: 函数区间分析摘要
        """
        summary = {}
        for function, data in self._function_summaries.items():
            # 生成易读的函数摘要
            summary[f"{function.contract.name}.{function.name}"] = {
                "params": {str(param): str(interval) for param, interval in data["params"].items()},
                "return": {str(ret): str(interval) for ret, interval in data["return"].items()}
            }
        return summary

class IntervalAnalysisLauncher:
    """
    区间分析独立启动器
    
    该类提供了一个统一的入口点来执行区间分析，
    不依赖于Slither的检测器架构
    """
    
    def __init__(self, compilation_unit):
        """
        初始化启动器
        
        Args:
            compilation_unit: Slither编译单元对象
        """
        self.compilation_unit = compilation_unit
        self.analyzer = DeFiRangeAnalyzer(compilation_unit)
    
    def launch(self):
        """
        执行分析并返回结果
        
        Returns:
            list: 分析结果列表
        """
        return self.analyzer.analyze()
    
    def get_summary(self):
        """
        获取分析摘要
        
        Returns:
            dict: 函数区间分析摘要
        """
        return self.analyzer.export_summary()

class DeFiRangeViolationDetector(AbstractDetector):
    """
    Slither检测器集成
    
    此类实现了Slither的AbstractDetector接口，
    允许区间分析作为标准Slither检测器运行。
    
    作为双模式集成的一部分，此检测器允许用户通过Slither标准检测器接口
    运行区间分析，同时也可以通过命令行工具进行更灵活的使用。
    """ 
    ARGUMENT = 'defi-range-violation'  # 确保此参数与命令行中使用的参数一致
    HELP = 'DeFi合约中的数值区间违规检测'
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.HIGH
    
    WIKI = 'https://github.com/slitherv1/wiki/defi-range-violation'
    WIKI_TITLE = 'DeFi数值区间违规'
    WIKI_DESCRIPTION = (
        '检测DeFi合约中可能超出预期区间的数值操作，'
        '包括溢出、下溢、除零风险以及DeFi特定约束违规。'
    )
    WIKI_EXPLOIT_SCENARIO = '''
```solidity
function calculateInterest(uint256 amount, uint256 rate) public returns (uint256) {
    // 如果amount或rate非常大，计算结果可能溢出
    uint256 interest = (amount * rate) / 10000;
    return interest;
}
```
如果amount接近uint256上限且rate较大，乘法操作可能导致溢出，产生错误的结果。
'''
    WIKI_RECOMMENDATION = (
        '对所有数值操作使用SafeMath（Solidity < 0.8.0）或添加明确的溢出检查。'
        '对于可能接受外部输入的值，添加显式的范围检查以确保在安全区间内。'
        '特别是对于DeFi协议，确保所有关键参数（如汇率、利率、金额等）都有合理的区间约束。'
    )

    def _detect(self):
        """
        实现Slither检测器接口
        
        此方法创建区间分析器，运行分析，并将结果转换为
        Slither兼容的格式。
        
        Returns:
            list: 符合Slither检测器格式的结果列表
        """
        # 创建分析器并运行分析
        analyzer = DeFiRangeAnalyzer(self.compilation_unit)
        violations = analyzer.analyze()
        
        # 处理分析结果
        results = []
        for violation in violations:
            if 'contract' in violation and 'function' in violation and 'violation' in violation:
                # 为合约函数相关问题准备详细信息
                contract_name = violation.get('contract', 'Unknown')
                function_name = violation.get('function', 'Unknown')
                variable = violation.get('variable', 'Unknown')
                issue = violation.get('violation', 'Unknown')
                interval = violation.get('interval', 'Unknown')
                
                info = [
                    f"在 {contract_name} 合约的 {function_name} 函数中检测到区间违规:\n",
                    f"变量 {variable} 的区间为 {interval}\n",
                    f"违规: {issue}\n"
                ]
                
                # 创建初步结果
                result = self.generate_result(info)
                
                # 添加源代码位置信息
                contract = self.compilation_unit.get_contract_from_name(contract_name)
                if contract:
                    # 处理get_contract_from_name返回列表的情况
                    if isinstance(contract, list):
                        if contract:
                            contract = contract[0]  # 使用第一个匹配的合约
                        else:
                            contract = None
                            
                    if contract:  # 确保contract不为None或空列表
                        function = next((f for f in contract.functions if f.name == function_name), None)
                        if function:
                            result.add(function)
                
                results.append(result)
            
            elif 'issue' in violation:
                # 处理通用问题
                info = [f"检测到通用问题: {violation['issue']}\n"]
                results.append(self.generate_result(info))
        
        return results