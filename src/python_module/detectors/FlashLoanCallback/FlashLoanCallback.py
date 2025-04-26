"""
闪电贷回调风险检测器
"""

from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.core.declarations import Function
from slither.core.cfg.node import NodeType
from slither.core.variables.state_variable import StateVariable
from slither.slithir.operations import SolidityCall, LowLevelCall, HighLevelCall, Send, Transfer
from slither.analyses.data_dependency.data_dependency import is_tainted
from typing import List, Dict, Set, Tuple
import re

class FlashLoanCallback(AbstractDetector):
  """
  检测闪电贷回调函数
  - 状态变量的不安全修改
  - 缺失重入保护
  - 在状态更新后进行外部调用
  """
  
  ARGUMENT = "flashloan-callback-risks"
  HELP = "检测闪电贷回调函数中的风险"
  IMPACT = DetectorClassification.HIGH
  CONFIDENCE = DetectorClassification.HIGH
  
  WIKI = "https://www.example.com/wiki/flashloan-callback-attack"
  WIKI_TITLE = "闪电贷回调风险"
  WIKI_DESCRIPTION = "检测闪电贷回调函数中存在的风险"
  WIKI_EXPLOIT_SCENARIO = """
```solidity
contract vulnerableProtocal {
  mapping(address => uint256) public  userBalances;
  uint public totalSupply;
  
  //Uniswap V2 闪电贷回调函数
  function uniswapV2Call(address sender, uint amount0, uint amount1, bytes calldata data) external {
    // 回调中更新状态变量
    totalSupply += amount0;
    
    // 更新余额
    address user = abi.decode(data, (address));
    userBalances[user] += amount0;
    
    // 缺少重入保护的外部调用
    (bool success, ) = user.call{value: amount0}("");
    require(success, "Transfer failed");
  }
}
```
"""
  WIKI_RECOMMENDATION = """
  1. 在状态更新后进行外部调用时，添加重入保护,使用 `ReentrancyGuard` 或 `ReentrancyGuardUpgradeable` 等库来保护状态变量的修改
  2. 不在回调中直接更新关键状态变量，特别是与价格、余额有关的变量
  3. 验证闪电贷回调的发送者身份
  4. 使用检查-效果-交互模式(先做所有状态修改，最后再进行外部调用)
  """
  
  def _is_flashloan_callback(self, function:Function) -> bool:
    """
    判断一个函数是否是闪电贷回调函数
    
    Args:
      function: 需要判断的函数
    
    Returns:
      bool: 是闪电贷回调函数就返回True,否则False
    """
    
    # 如果函数没有签名属性，直接根据函数名判断
    if not hasattr(function, 'signature') or function.signature is None:
      # 检查函数名称是否包含闪电贷相关内容
      if any(keyword in function.name.lower() for keyword in ["flashloan", "flash", "callback", "uniswap", "execute", "onflash"]):
        return True
      return False
    
    callback_signatures = [
      # Uniswap V2 
      "uniswapV2Call(address,uint256,uint256,bytes)",
      
      # AAVE
      "executeOperation(address[],uint256[],uint256[],address,bytes)",
      "executeOperation(address,uint256,uint256,address,bytes)",
      
      # Compound
      "onFlashLoan(address,address,uint256,uint256,bytes)",
      
      # DyDx - 更新为结构体参数格式
      "callFunction(address,tuple,bytes)",
      "callFunction(address,(address,address,uint256,uint256),bytes)",
      "callFunction(address,AccountInfo,bytes)",
      
      # Balancer
      "receiveFlashLoan(address[],uint256[],uint256[],bytes)",
      
      # 1inch
      "flashCallback(address,uint256,uint256,bytes)",
      
      # MakerDAO
      "onFlashLoanTransfer(address,address,uint256,bytes)",
      
      # Uniswap V3
      "uniswapV3FlashCallback(uint256,uint256,bytes)",
      
      # Curve
      "callback(bytes)"
    ]
    
    # 检查函数签名是否符合闪电贷回调
    try:
      function_sig = str(function.signature) if function.signature else ""
      
      # 规范化函数签名（移除空格）
      clean_sig = re.sub(r'\s+', '', function_sig)
      
      for callback_sig in callback_signatures:
        # 移除空格后进行比较
        clean_callback = re.sub(r'\s+', '', callback_sig)
        if clean_sig == clean_callback:
          return True
      
      # 检查函数名称是否包含闪电贷相关内容
      if any(keyword in function.name.lower() for keyword in ["flashloan", "flash", "callback", "uniswap", "execute", "onflash"]):
        return True
    except Exception as e:
      # 如果发生异常，记录日志但继续执行
      print(f"处理函数签名时出错: {e}")
      # 降级为仅检查函数名
      if any(keyword in function.name.lower() for keyword in ["flashloan", "flash", "callback", "uniswap", "execute", "onflash"]):
        return True
    
    return False
  
  def _has_reentrancy_guard(self, function) -> bool:
    """
    检查是否有重入保护

    
    Args:
      function: 要检查的函数
    
    Returns:
      bool: 存在重入保护就返回True，否则就返回False
    """
    
    # 检查是否使用了重入锁
    reentrancy_modifiers = ["nonreentrant", "noreeentrant", "mutex", "lock", "reentrancyguard"]
    
    for modifier in function.modifiers:
      if any(lock_name in modifier.name.lower() for lock_name in reentrancy_modifiers):
        return True
    
    # 检查函数体中是否有手动实现的锁变量检查
    for node in function.nodes:
      if node.contains_require_or_assert():
        req_str = str(node).lower()
        if any(lock_term in req_str for lock_term in ["lock", "locked", "locker", "_notenter", "_notreenter"]):
          return True
        
    return False
  
  def _find_write_after_call(self, function: Function) -> List[Tuple[StateVariable, Function]]:
    """
    检查函数中是否有"写入状态变量后进行外部调用"的模式
    这违反了"检查-效果-交互"模式，容易导致重入攻击
    
    Args:
      function: 要检查的函数
      
    Returns:
      List[Tuple[StateVariable, Function]]: 存在问题的(状态变量, 外部调用函数)列表
    """
    result = []
    external_calls = []
    state_vars_written = set()
    
    # 首先收集所有的外部调用
    for node in function.nodes:
      for ir in node.irs:
        if isinstance(ir, (LowLevelCall, HighLevelCall, Send, Transfer)):
          if hasattr(ir, "function"):
            external_calls.append((node, ir.function))
          else:
            external_calls.append((node, None))
    
    # 如果没有外部调用，直接返回
    if not external_calls:
      return result
    
    # 检查每个外部调用前是否有状态变量写入
    for node in function.nodes:
      # 记录该节点写入的状态变量
      for state_var in node.state_variables_written:
        state_vars_written.add(state_var)
      
      # 检查该节点是否有外部调用
      for ir in node.irs:
        if isinstance(ir, (LowLevelCall, HighLevelCall, Send, Transfer)):
          # 对于每个已写入的状态变量，检查是否在该外部调用之前
          for state_var in state_vars_written:
            # 如果有外部函数调用，且之前已经修改了状态变量
            if hasattr(ir, "function"):
              result.append((state_var, ir.function))
            else:
              result.append((state_var, None))
    
    return result
  
  def _detect_unsafe_operations(self, function: Function) -> List[str]:
    """
    检测函数中的不安全操作
    
    Args:
      function: 要检查的函数
      
    Returns:
      List[str]: 检测到的不安全操作列表
    """
    unsafe_operations = []
    
    # 检查是否直接使用了msg.value
    for node in function.nodes:
      for ir in node.irs:
        if isinstance(ir, SolidityCall) and "msg.value" in str(ir):
          unsafe_operations.append(f"在闪电贷回调函数中直接使用了msg.value，可能导致资金被盗")
    
    # 检查是否对重要状态变量进行修改
    critical_state_vars = []
    for state_var in function.contract.state_variables:
      if any(keyword in state_var.name.lower() for keyword in 
              ["balance", "supply", "total", "amount", "pool", "reserve", 
               "price", "rate", "value", "token", "fee"]):
        critical_state_vars.append(state_var)
    
    for node in function.nodes:
      for state_var in node.state_variables_written:
        if state_var in critical_state_vars:
          unsafe_operations.append(f"在闪电贷回调中修改了关键状态变量: {state_var.name}")
    
    return unsafe_operations
  
  def _check_sender_validation(self, function: Function) -> bool:
    """
    检查是否对发送者进行了验证
    
    Args:
      function: 要检查的函数
      
    Returns:
      bool: 如果验证了发送者返回True，否则返回False
    """
    for node in function.nodes:
      if node.contains_require_or_assert():
        req_str = str(node).lower()
        if "msg.sender" in req_str and any(term in req_str for term in ["==", "require", "equal"]):
          return True
    
    return False
  
  def _detect(self) -> List:
    """
    实现主要的检测逻辑
    
    Returns:
      List: 检测结果列表
    """
    results = []
    
    for contract in self.compilation_unit.contracts:
      for function in contract.functions:
        # 跳过构造函数、内部函数和私有函数
        if function.is_constructor or function.visibility in ["internal", "private"]:
          continue
        
        # 检查是否是闪电贷回调函数
        is_callback = self._is_flashloan_callback(function)
        
        # 特殊处理 DyDx 的 callFunction
        if not is_callback and function.name == "callFunction":
          # 检查参数是否匹配 DyDx 的回调格式
          if len(function.parameters) >= 2:
            param_types = [str(p.type) for p in function.parameters]
            # DyDx 回调通常有 address 和结构体参数
            if "address" in param_types:
              is_callback = True
        
        if not is_callback:
          continue
        
        # 收集所有风险
        risks = []
        
        # 1. 检查是否缺少重入保护
        if not self._has_reentrancy_guard(function):
          risks.append("缺少重入保护")
        
        # 2. 检查是否有写后调用的模式
        write_after_calls = self._find_write_after_call(function)
        if write_after_calls:
          for var, call in write_after_calls:
            call_name = call.name if call else "外部调用"
            risks.append(f"写入状态变量 '{var.name}' 后进行了 '{call_name}' 的外部调用")
        
        # 3. 检查是否有不安全操作
        unsafe_ops = self._detect_unsafe_operations(function)
        risks.extend(unsafe_ops)
        
        # 4. 检查是否验证了发送者
        if not self._check_sender_validation(function):
          risks.append("没有验证回调的发送者身份")
        
        # 5. 特别检查 DyDx callFunction - 特别关注状态变量修改
        if function.name == "callFunction":
          # 检查是否修改了状态变量
          state_vars_written = set()
          for node in function.nodes:
            state_vars_written.update(node.state_variables_written)
          
          if state_vars_written:
            for var in state_vars_written:
              risks.append(f"DyDx闪电贷回调中修改了状态变量: {var.name}")
        
        # 如果有任何风险，生成报告
        if risks:
          info = [
            f"合约 '{contract.name}' 中的闪电贷回调函数 '{function.name}' 存在以下风险:\n"
          ]
          
          for i, risk in enumerate(risks, 1):
            info.append(f"  {i}. {risk}\n")
          
          # 添加源代码位置信息
          res = self.generate_result(info)
          res.add(function)
          results.append(res)
    
    return results
