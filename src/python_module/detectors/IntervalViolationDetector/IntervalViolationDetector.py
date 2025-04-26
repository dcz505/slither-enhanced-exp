from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither_enhanced.src.python_module.interval_analysis import launch_analysis, create_analyzer
import logging

class IntervalViolationDetector(AbstractDetector):
    """
    使用区间分析模块检测DeFi合约中的数值范围违规
    
    此检测器是DeFiRangeViolationDetector的互补检测器，专注于
    更一般性的区间违规，而DeFiRangeViolationDetector专注于DeFi特定约束
    """

    ARGUMENT = 'interval-violation'
    HELP = '使用增强区间分析检测智能合约中的一般数值范围违规'
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.HIGH

    WIKI = 'https://github.com/your-repo/wiki/interval-violation'
    WIKI_TITLE = '智能合约数值范围违规'
    WIKI_DESCRIPTION = (
        '检测智能合约中可能违反预期范围约束的数值操作，'
        '包括溢出/下溢、除零错误等一般性问题。'
    )
    WIKI_EXPLOIT_SCENARIO = '''
```solidity
function calculateExchangeRate(uint256 tokenAmount) public {
    // 交易量可能非常大，导致汇率溢出
    uint256 exchangeRate = totalPoolValue * PRECISION / tokenAmount;
    // exchangeRate可能超出预期范围
}
```
'''
    WIKI_RECOMMENDATION = (
        '使用SafeMath进行算术操作，并添加显式范围检查以确保数值在预期区间内。'
        '对于Solidity 0.8.x，请额外添加业务逻辑范围检查，确保数值满足预期约束。'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("IntervalViolationDetector")
        
    def _is_defi_specific(self, violation_text):
        """判断是否为DeFi特定约束违规"""
        defi_keywords = [
            "DeFi约束", "DeFi特定", "defi约束", "defi特定", 
            "流动性", "汇率", "利率", "抵押率", "闪电贷", "flash loan",
            "swap", "交换", "exchange", "pool", "池", "token", "令牌"
        ]
        return any(keyword in violation_text for keyword in defi_keywords)
        
    def _is_general_problem(self, violation_text):
        """判断是否为一般性问题"""
        general_keywords = [
            "溢出", "下溢", "除零", "overflow", "underflow", "division by zero",
            "边界检查", "boundary", "bound"
        ]
        return any(keyword in violation_text for keyword in general_keywords)

    def _detect(self):
        """
        使用区间分析模块检测问题
        """
        try:
            results = []
            
            # 启动区间分析
            analysis_results = launch_analysis(self.compilation_unit)
            
            # 处理分析结果 - 专注于一般性问题而不是DeFi特定约束
            for result in analysis_results:
                if 'contract' in result and 'function' in result and 'violation' in result:
                    # 获取违规信息
                    violation = result.get('violation', '')
                    
                    # 跳过DeFi特定约束 - 由DeFiRangeViolationDetector处理
                    if self._is_defi_specific(violation):
                        continue
                    
                    # 只处理一般性问题
                    if not self._is_general_problem(violation):
                        continue
                    
                    # 构建检测结果
                    contract_name = result.get('contract', 'Unknown')
                    contract = None
                    
                    if hasattr(self.compilation_unit, "get_contract_from_name"):
                        contract = self.compilation_unit.get_contract_from_name(contract_name)
                    
                    if not contract:
                        continue
                    
                    # 处理get_contract_from_name返回列表的情况
                    if isinstance(contract, list):
                        if not contract:
                            continue
                        contract = contract[0]  # 使用第一个匹配的合约
                        
                    function_name = result.get('function', 'Unknown')
                    function = None
                    for f in contract.functions:
                        if f.name == function_name:
                            function = f
                            break
                    
                    if not function:
                        continue
                    
                    info = [
                        f"在 {contract_name} 合约的 {function_name} 函数中，",
                        f"变量 {result.get('variable', 'Unknown')} 可能违反数值约束: {violation}.\n",
                        f"计算得到的区间值为: {result.get('interval', 'Unknown')}\n"
                    ]
                    
                    # 添加源代码位置
                    source_location = self.generate_result(info)
                    if function:
                        source_location.add(function)
                    
                    results.append(source_location)
                
                elif 'issue' in result:
                    # 处理通用问题
                    issue = result.get('issue', '')
                    # 跳过DeFi特定问题 - 由DeFiRangeViolationDetector处理
                    if self._is_defi_specific(issue):
                        continue
                        
                    # 只处理一般性问题    
                    if self._is_general_problem(issue):
                        info = [f"检测到潜在问题: {issue}\n"]
                        results.append(self.generate_result(info))
            
            return results
            
        except Exception as e:
            self.logger.error(f"区间分析检测器执行出错: {e}")
            import traceback
            traceback.print_exc()
            return [] 