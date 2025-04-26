"""
Slither Enhanced插件模块
======================

这个模块是Slither智能合约分析框架的增强插件，提供了额外的漏洞检测器、
区间分析和其他增强功能。

包括:
- DeFi特定的漏洞检测器
- 区间分析功能
- Web用户界面

使用方法:
```
$ pip install -e .
$ slither yourfile.sol --detect interval-violation
$ slither yourfile.sol --detect defi-range-violation
```

也可以使用命令行工具直接进行区间分析:
```
$ interval-analyze yourfile.sol
```
"""

from typing import List, Type, Tuple

from slither.detectors.abstract_detector import AbstractDetector
from slither.printers.abstract_printer import AbstractPrinter


def make_plugin() -> Tuple[List[Type[AbstractDetector]], List[Type[AbstractPrinter]]]:
    """创建Slither插件
    
    返回检测器和打印器的列表，这些将被Slither框架加载
    """
    from slither_enhanced.src.python_module.detectors.UncheckedTokenBalanceChange import UncheckedBalanceChangeDetector
    from slither_enhanced.src.python_module.detectors.UnboundedFlashLoanRisk import UnboundedFlashLoanRisk
    
    # 导入区间分析检测器
    from slither_enhanced.src.python_module.detectors.IntervalViolationDetector import IntervalViolationDetector
    from slither.slither_enhanced.src.python_module.detectors.NumericalAnomalies.numerical_anomalies import IntervalBasedNumericalAnomalies
    
    # 导入DeFiRangeViolationDetector
    from slither_enhanced.src.python_module.interval_analysis.range_analysis import DeFiRangeViolationDetector
    
    # 导入FlashLoanCallback检测器
    from slither_enhanced.src.python_module.detectors.FlashLoanCallback import FlashLoanCallback
    
    detectors: List[Type[AbstractDetector]] = [
        UncheckedBalanceChangeDetector,
        UnboundedFlashLoanRisk,
        IntervalViolationDetector,
        IntervalBasedNumericalAnomalies, 
        DeFiRangeViolationDetector,  # 添加DeFiRangeViolationDetector检测器
        FlashLoanCallback  # 添加FlashLoanCallback检测器
    ]
    
    printers: List[Type[AbstractPrinter]] = []
    
    return detectors, printers
