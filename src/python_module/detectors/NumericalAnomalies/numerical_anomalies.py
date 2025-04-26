"""
数值异常检测器 (Numerical Anomalies Detector)

本检测器利用增强的区间分析功能，专注于识别智能合约中高可信度的数值异常，包括：
1. 数值溢出/下溢风险
2. 除零错误
3. DeFi特定的数值约束违规
4. 不合理的数值操作

该检测器过滤掉低置信度的警告，只保留具有高置信度的发现，以减少误报。
"""

from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither_enhanced.src.python_module.interval_analysis import launch_analysis
from slither_enhanced.src.python_module.interval_analysis.range_analysis import Interval

class IntervalBasedNumericalAnomalies(AbstractDetector):
    """
    基于区间分析的数值异常检测器
    
    使用增强的区间分析功能，识别智能合约中高可信度的数值异常
    """
    
    ARGUMENT = 'interval-numerical-anomalies'
    HELP = '基于增强区间分析的高可信度数值异常检测'
    IMPACT = DetectorClassification.HIGH
    CONFIDENCE = DetectorClassification.HIGH
    
    WIKI = 'https://github.com/slither_enhanced/wiki/NumericalAnomalies'
    
    WIKI_TITLE = '数值异常检测'
    WIKI_DESCRIPTION = '检测智能合约中的数值溢出、下溢、除零错误和其他数值异常'
    WIKI_EXPLOIT_SCENARIO = '''
```solidity
contract VulnerableContract {
    function transfer(address to, uint256 amount) public {
        // 没有检查余额，可能导致下溢
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
    
    function divide(uint256 a, uint256 b) public returns (uint256) {
        // 没有检查除数是否为零
        return a / b;
    }
}
```
'''
    WIKI_RECOMMENDATION = '使用SafeMath库或Solidity 0.8.0+的内置溢出检查。始终验证除数不为零。考虑使用require语句确保数值操作在合理范围内。'
    
    def _is_high_confidence_issue(self, issue):
        """
        评估问题是否为高可信度
        
        Args:
            issue: 区间分析产生的问题
            
        Returns:
            bool: 如果是高可信度问题则返回True
        """
        # 检查是否有明确的问题描述
        if 'issue' not in issue and 'violation' not in issue:
            return False
            
        issue_desc = issue.get('issue', issue.get('violation', ''))
        
        # 高可信度问题类型
        high_confidence_patterns = [
            "确定性除零错误",  # 确定的除零错误
            "确定性除零风险",  # 高风险的除零问题
            "常量下溢",        # 确定的常量下溢
            "常量溢出",        # 确定的常量溢出
            "可能下溢",        # 具体路径上的下溢
            "可能溢出",        # 具体路径上的溢出
        ]
        
        # 检查是否为高可信度模式
        if any(pattern in issue_desc for pattern in high_confidence_patterns):
            return True
            
        # 检查是否为精确区间（非全范围区间）
        if 'interval' in issue:
            interval_str = issue['interval']
            if interval_str != "⊤" and "[0, 2**256 - 1]" not in interval_str:
                # 具有明确边界的区间，通常表示更高的确定性
                return True
                
        # 检查是否为SafeMath相关问题
        if "SafeMath" in issue_desc and ("溢出" in issue_desc or "下溢" in issue_desc):
            # SafeMath相关的溢出/下溢通常是误报，低置信度
            return False
            
        # 检查是否有明确的合约和函数上下文
        if 'contract' in issue and 'function' in issue and 'variable' in issue:
            # DeFi特定约束违规
            if "违规" in issue_desc and ("最小值违规" in issue_desc or "最大值违规" in issue_desc):
                return True
        
        # 默认为低置信度
        return False
        
    def _format_result(self, issue):
        """
        格式化检测结果
        
        Args:
            issue: 区间分析产生的问题
            
        Returns:
            dict: 格式化的检测结果
        """
        # 创建基本结果结构
        result = {
            'elements': [],
            'description': ''
        }
        
        # 构建描述信息
        if 'issue' in issue:
            result['description'] = f"发现数值异常: {issue['issue']}"
        else:
            # 构建更详细的描述
            contract = issue.get('contract', 'Unknown')
            function = issue.get('function', 'Unknown')
            variable = issue.get('variable', 'Unknown')
            violation = issue.get('violation', 'Unknown')
            interval = issue.get('interval', 'Unknown')
            
            result['description'] = f"在合约 {contract} 的函数 {function} 中发现数值异常:\n"
            result['description'] += f"变量 {variable} 的区间为 {interval}\n"
            result['description'] += f"违规: {violation}"
            
            # 添加元素信息（修复处理 contract_obj 的错误）
            if hasattr(self.compilation_unit, "get_contract_from_name"):
                try:
                    contract_obj = self.compilation_unit.get_contract_from_name(contract)
                    # 检查 contract_obj 是否为列表
                    if isinstance(contract_obj, list):
                        # 如果是列表，取第一个元素（假设是最相关的）
                        if contract_obj and hasattr(contract_obj[0], "functions"):
                            # 遍历所有合约中的函数
                            for contract_item in contract_obj:
                                function_obj = next((f for f in contract_item.functions if f.name == function), None)
                                if function_obj:
                                    result['elements'].append(function_obj)
                                    break
                    elif contract_obj and hasattr(contract_obj, "functions"):
                        # 正常处理单个合约对象的情况
                        function_obj = next((f for f in contract_obj.functions if f.name == function), None)
                        if function_obj:
                            result['elements'].append(function_obj)
                except Exception as e:
                    self.logger.error(f"查找合约或函数时出错: {e}")
        
        return result
    
    def _detect(self):
        """
        执行检测
        
        Returns:
            list: 检测结果列表
        """
        try:
            # 使用增强的区间分析获取所有结果
            raw_results = launch_analysis(self.compilation_unit)
            
            # 过滤出高可信度问题
            high_confidence_issues = [issue for issue in raw_results if self._is_high_confidence_issue(issue)]
            
            # 格式化结果
            formatted_results = []
            for issue in high_confidence_issues:
                try:
                    result = self._format_result(issue)
                    if result and 'description' in result and result['description']:
                        info = [result['description']]
                        res = self.generate_result(info)
                        # 添加元素信息
                        if 'elements' in result and result['elements']:
                            for element in result['elements']:
                                if element:
                                    res.add(element)
                        formatted_results.append(res)
                except Exception as e:
                    self.logger.error(f"处理问题时出错: {e}")
                    import traceback
                    traceback.print_exc()
            
            return formatted_results
        except Exception as e:
            self.logger.error(f"区间分析执行出错: {e}")
            import traceback
            traceback.print_exc()
            return [] 