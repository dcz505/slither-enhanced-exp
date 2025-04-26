#!/usr/bin/env python3

"""
区间分析命令行工具
此工具允许用户通过命令行直接使用区间分析功能，而不必通过漏洞检测器接口
"""

import argparse
import json
import logging
import sys
from pathlib import Path

# 添加slither目录到搜索路径
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent.parent.parent.parent  # 到slither目录
sys.path.append(str(ROOT_DIR))

# 修复Slither导入
from slither.slither import Slither
from slither.utils.colors import red, green, yellow

from . import launch_analysis, get_analysis_summary

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntervalAnalysis")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='DeFi智能合约区间分析工具')
    parser.add_argument('solidity_file', help='Solidity源文件或项目目录')
    parser.add_argument('--json', help='输出JSON格式结果到指定文件')
    parser.add_argument('--summary', action='store_true', help='输出函数区间分析摘要')
    parser.add_argument('--debug', action='store_true', help='启用调试输出')
    parser.add_argument('--solc-remaps', help='Solidity编译器重映射', default=None)
    return parser.parse_args()

def process_results(results, summary_mode=False):
    """处理并显示分析结果"""
    if not results:
        print(green("✓ 未发现潜在区间问题"))
        return
    
    if summary_mode:
        # 摘要模式
        print(yellow(f"== 函数区间分析摘要 =="))
        for func_name, data in results.items():
            print(yellow(f"\n函数: {func_name}"))
            
            print("  参数:")
            for param, interval in data['params'].items():
                print(f"    - {param}: {interval}")
            
            print("  返回值:")
            for ret, interval in data['return'].items():
                print(f"    - {ret}: {interval}")
    else:
        # 标准结果模式
        print(red(f"! 发现 {len(results)} 个潜在区间问题"))
        for idx, result in enumerate(results, 1):
            if 'contract' in result:
                print(red(f"\n问题 #{idx}:"))
                print(f"  合约: {result['contract']}")
                print(f"  函数: {result['function']}")
                print(f"  变量: {result['variable']}")
                print(f"  违规: {result['violation']}")
                print(f"  区间: {result['interval']}")
            else:
                print(red(f"\n问题 #{idx}: {result['issue']}"))

def main():
    """主函数"""
    args = parse_args()
    
    # 配置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 初始化Slither
        logger.info(f"分析文件: {args.solidity_file}")
        remappings = {}
        if args.solc_remaps:
            remappings = dict(x.split("=") for x in args.solc_remaps.split(","))
        
        slither = Slither(args.solidity_file, solc_remaps=remappings)
        
        # 执行分析
        if args.summary:
            # 从slither中正确获取compilation_unit
            if hasattr(slither, 'compilation_unit'):
                compilation_unit = slither.compilation_unit
            else:
                # 如果没有compilation_unit属性，可能直接使用slither对象
                compilation_unit = slither
                
            results = get_analysis_summary(compilation_unit)
        else:
            # 从slither中正确获取compilation_unit
            if hasattr(slither, 'compilation_unit'):
                compilation_unit = slither.compilation_unit
            else:
                # 如果没有compilation_unit属性，可能直接使用slither对象
                compilation_unit = slither
                
            results = launch_analysis(compilation_unit)
        
        # 处理结果
        process_results(results, args.summary)
        
        # 导出JSON结果
        if args.json:
            with open(args.json, 'w') as f:
                json.dump(results, f, indent=4)
            logger.info(f"结果已保存到: {args.json}")
        
    except Exception as e:
        logger.error(f"分析过程中出错: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 