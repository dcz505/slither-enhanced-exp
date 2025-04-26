#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
脚本结构验证工具：验证测试脚本结构是否正确，所有脚本是否可以正确导入，配置文件是否存在。
这个简单的工具旨在确保脚本整合工作已成功完成。
"""

import os
import sys
import importlib.util
from pathlib import Path
import json

# 颜色输出
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# 当前路径和项目根路径
current_dir = os.path.dirname(os.path.abspath(__file__))
test_dir = os.path.dirname(current_dir)
project_root = os.path.abspath(os.path.join(test_dir, "../../.."))

# 添加项目根目录到Python路径
sys.path.insert(0, project_root)

def print_success(message):
    """打印成功消息"""
    print(f"{GREEN}✓ {message}{RESET}")

def print_warning(message):
    """打印警告消息"""
    print(f"{YELLOW}! {message}{RESET}")

def print_error(message):
    """打印错误消息"""
    print(f"{RED}✗ {message}{RESET}")

def check_path(path, description):
    """检查路径是否存在，并打印状态"""
    full_path = os.path.join(project_root, path)
    if os.path.exists(full_path):
        print_success(f"{description}路径正常: {path}")
        return True
    else:
        print_error(f"{description}路径不存在: {path}")
        return False

def check_script(script_path, module_path):
    """检查脚本是否存在并可以导入"""
    full_path = os.path.join(project_root, script_path)
    if not os.path.exists(full_path):
        print_error(f"脚本不存在: {script_path}")
        return False
    
    try:
        spec = importlib.util.spec_from_file_location("module", full_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print_success(f"脚本导入成功: {script_path}")
        return True
    except Exception as e:
        print_error(f"脚本导入失败: {script_path} - {str(e)}")
        return False

def check_config_file(config_path):
    """检查配置文件是否存在并有效"""
    full_path = os.path.join(project_root, config_path)
    if not os.path.exists(full_path):
        print_error(f"配置文件不存在: {config_path}")
        return False
    
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            json.load(f)
        print_success(f"配置文件有效: {config_path}")
        return True
    except json.JSONDecodeError:
        print_error(f"配置文件无效（JSON解析错误）: {config_path}")
        return False
    except Exception as e:
        print_error(f"配置文件检查失败: {config_path} - {str(e)}")
        return False

def verify_structure():
    """验证整个脚本结构"""
    print("\n" + "="*50)
    print("Slither Enhanced 脚本结构验证")
    print("="*50 + "\n")
    
    success_count = 0
    total_checks = 0
    
    # 检查目录结构
    print("\n【目录结构检查】")
    
    paths = [
        ("slither/slither_enhanced/scripts", "工具脚本"),
        ("slither/slither_enhanced/test/scripts", "测试脚本"),
        ("slither/slither_enhanced/test/scripts/interval_analysis", "区间分析测试脚本"),
        ("slither/slither_enhanced/test/configs", "配置文件"),
        ("slither/slither_enhanced/test/TestContracts", "测试合约"),
        ("slither/slither_enhanced/test/results", "测试结果")
    ]
    
    for path, desc in paths:
        total_checks += 1
        if check_path(path, desc):
            success_count += 1
    
    # 检查关键脚本
    print("\n【关键脚本检查】")
    
    scripts = [
        # 测试脚本
        ("slither/slither_enhanced/test/scripts/run_paper_evaluation.py", "slither.slither_enhanced.test.scripts.run_paper_evaluation"),
        ("slither/slither_enhanced/test/scripts/run_benchmark_test.py", "slither.slither_enhanced.test.scripts.run_benchmark_test"),
        ("slither/slither_enhanced/test/scripts/run_real_world_test.py", "slither.slither_enhanced.test.scripts.run_real_world_test"),
        ("slither/slither_enhanced/test/scripts/run_performance_test.py", "slither.slither_enhanced.test.scripts.run_performance_test"),
        ("slither/slither_enhanced/test/scripts/run_complete_test.py", "slither.slither_enhanced.test.scripts.run_complete_test"),
        
        # 区间分析脚本
        ("slither/slither_enhanced/test/scripts/interval_analysis/run_interval_analysis.py", "slither.slither_enhanced.test.scripts.interval_analysis.run_interval_analysis"),
        
        # 工具脚本
        ("slither/slither_enhanced/scripts/start_visualization.py", "slither.slither_enhanced.scripts.start_visualization"),
        ("slither/slither_enhanced/scripts/build_and_run.py", "slither.slither_enhanced.scripts.build_and_run")
    ]
    
    for script_path, module_path in scripts:
        total_checks += 1
        if check_path(script_path, "脚本"):
            success_count += 1
    
    # 检查配置文件
    print("\n【配置文件检查】")
    
    configs = [
        "slither/slither_enhanced/test/configs/test_configs.json",
        "slither/slither_enhanced/test/configs/test_config.json"
    ]
    
    for config_path in configs:
        total_checks += 1
        if check_config_file(config_path):
            success_count += 1
    
    # 检查文档
    print("\n【文档检查】")
    
    docs = [
        "slither/slither_enhanced/test/README.md",
        "slither/slither_enhanced/test/scripts/README.md",
        "slither/slither_enhanced/scripts/README.md",
        "slither/slither_enhanced/test/README_scripts_structure.md"
    ]
    
    for doc_path in docs:
        if os.path.exists(os.path.join(project_root, doc_path)):
            total_checks += 1
            if check_path(doc_path, "文档"):
                success_count += 1
    
    # 统计结果
    print("\n" + "="*50)
    print(f"结构验证完成: {success_count}/{total_checks} 项检查通过")
    print("="*50)
    
    if success_count == total_checks:
        print_success("\n测试脚本结构完全正确！可以正常使用所有脚本。")
        print("\n建议的使用方式：")
        print("1. 从项目根目录运行")
        print("2. 使用模块导入方式，如：")
        print("   python -m slither.slither_enhanced.test.scripts.run_paper_evaluation")
    else:
        fail_count = total_checks - success_count
        print_warning(f"\n有 {fail_count} 项检查未通过。请处理上述错误后再使用脚本。")
    
    print("\n")
    return success_count == total_checks

if __name__ == "__main__":
    success = verify_structure()
    sys.exit(0 if success else 1) 