#!/usr/bin/env python3

"""
测试Slither Enhanced插件是否能被正确加载
"""

import sys
import importlib
import pkg_resources

def test_plugin_entry_points():
    """
    检查entry_points是否正确注册
    """
    print("检查插件entry_points...")
    
    # 查找所有slither_analyzer.plugin入口点
    found_plugins = []
    for entry_point in pkg_resources.iter_entry_points(group='slither_analyzer.plugin'):
        print(f"发现插件: {entry_point.name} -> {entry_point.module_name}")
        found_plugins.append(entry_point.name)
    
    # 检查我们的插件是否在列表中
    expected_plugins = [
        "unchecked-balance-change",
        "unbounded-flashloan-risk", 
        "interval-violation"
    ]
    
    for plugin in expected_plugins:
        if plugin in found_plugins:
            print(f"✅ 插件 '{plugin}' 已正确注册")
        else:
            print(f"❌ 插件 '{plugin}' 未找到")

def test_plugin_imports():
    """
    测试是否可以导入插件模块
    """
    print("\n测试插件模块导入...")
    
    modules_to_test = [
        "slither_enhanced",
        "slither_enhanced.src",
        "slither_enhanced.src.python_module",
        "slither_enhanced.src.python_module.detectors",
        "slither_enhanced.src.python_module.detectors.UncheckedTokenBalanceChange",
        "slither_enhanced.src.python_module.detectors.UncheckedTokenBalanceChange.UncheckedTokenBalanceChange",
        "slither_enhanced.src.python_module.detectors.UnboundedFlashLoanRisk",
        "slither_enhanced.src.python_module.detectors.UnboundedFlashLoanRisk.UnboundedFlashLoanRisk",
        "slither_enhanced.src.python_module.detectors.IntervalViolationDetector",
        "slither_enhanced.src.python_module.detectors.IntervalViolationDetector.IntervalViolationDetector",
        "slither_enhanced.src.python_module.interval_analysis",
    ]
    
    for module in modules_to_test:
        try:
            importlib.import_module(module)
            print(f"✅ 成功导入 '{module}'")
        except ImportError as e:
            print(f"❌ 无法导入 '{module}': {e}")

def test_make_plugin_function():
    """
    测试make_plugin函数是否能正确执行
    """
    print("\n测试make_plugin函数...")
    
    try:
        from slither_enhanced import make_plugin
        detectors, printers = make_plugin()
        print(f"✅ make_plugin函数执行成功，返回 {len(detectors)} 个检测器和 {len(printers)} 个打印器")
    except Exception as e:
        print(f"❌ make_plugin函数执行失败: {e}")

if __name__ == "__main__":
    print("Slither Enhanced插件测试\n" + "=" * 30)
    test_plugin_entry_points()
    test_plugin_imports()
    test_make_plugin_function()
    print("\n测试完成") 