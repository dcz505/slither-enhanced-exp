#!/usr/bin/env python3

"""
区间分析命令行工具
此工具允许用户通过命令行直接使用区间分析功能，而不必通过漏洞检测器接口
"""

import argparse
import json
import logging
import sys
import os
from pathlib import Path
import traceback
from termcolor import colored

# 添加slither目录到搜索路径
SCRIPT_DIR = Path(__file__).resolve().parent
ROOT_DIR = SCRIPT_DIR.parent.parent.parent.parent  # 到slither目录
sys.path.append(str(ROOT_DIR))

# 修复Slither导入
try:
    from slither.slither import Slither
    from slither_enhanced.src.python_module.interval_analysis import create_analyzer, launch_analysis
except ImportError:
    print("无法导入Slither或区间分析模块。请确保正确安装。")
    sys.exit(1)

from . import get_analysis_summary

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntervalAnalysis")

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='使用区间分析工具分析智能合约')
    parser.add_argument('filename', help='要分析的Solidity文件/项目')
    parser.add_argument('--json', metavar='FILE', help='将结果以JSON格式保存到指定文件')
    parser.add_argument('--summary', action='store_true', help='只输出摘要')
    parser.add_argument('--debug', action='store_true', help='启用调试输出')
    parser.add_argument('--solc-remaps', help='Solidity编译器重映射，用";"分隔', default="")
    return parser.parse_args()

def process_results(results, summary=False):
    """处理并格式化分析结果"""
    if summary:
        # 创建问题类型计数
        issue_counts = {}
        contract_counts = {}
        
        for result in results:
            issue = result.get('violation', result.get('issue', 'Unknown'))
            contract = result.get('contract', 'Global')
            
            # 更新问题计数
            if issue in issue_counts:
                issue_counts[issue] += 1
            else:
                issue_counts[issue] = 1
                
            # 更新合约计数
            if contract in contract_counts:
                contract_counts[contract] += 1
            else:
                contract_counts[contract] = 1
        
        # 打印摘要
        print("\n===== 区间分析摘要 =====")
        print(f"总问题数: {len(results)}")
        
        print("\n问题类型统计:")
        for issue, count in issue_counts.items():
            print(f"  {issue}: {count}")
            
        print("\n每个合约的问题数:")
        for contract, count in contract_counts.items():
            print(f"  {contract}: {count}")
    else:
        # 详细输出每个问题
        for result in results:
            if 'contract' in result and 'function' in result and 'violation' in result:
                contract = result['contract']
                function = result['function']
                variable = result['variable']
                violation = result['violation']
                interval = result['interval']
                
                print(f"\n[{colored(contract, 'cyan')}.{colored(function, 'green')}]")
                print(f"  变量: {colored(variable, 'yellow')}")
                
                # 根据严重程度着色
                color = 'red' if ('溢出' in violation or '下溢' in violation or '除零' in violation) else 'yellow'
                print(f"  违规: {colored(violation, color)}")
                print(f"  区间: {interval}")
            
            elif 'issue' in result:
                issue = result['issue']
                print(f"\n[{colored('全局问题', 'cyan')}]")
                print(f"  {colored(issue, 'red')}")

def main():
    """主函数"""
    args = parse_args()
    
    # 配置日志级别
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        # 处理Solidity编译器重映射
        solc_remaps = args.solc_remaps.split(";") if args.solc_remaps else []
        
        # 初始化Slither
        logger.info(f"分析文件: {args.filename}")
        slither = Slither(args.filename, solc_remaps=solc_remaps)
        
        # 获取compilation_unit
        if hasattr(slither, 'compilation_unit'):
            compilation_unit = slither.compilation_unit
        elif hasattr(slither, '_compilation_units') and len(slither._compilation_units) > 0:
            compilation_unit = slither._compilation_units[0]
        else:
            logger.warning("无法获取compilation_unit，尝试使用slither对象")
            compilation_unit = slither
        
        # 运行区间分析
        results = launch_analysis(compilation_unit)
        
        # 处理结果
        if args.json:
            # 保存JSON结果
            with open(args.json, 'w') as f:
                json.dump(results, f, indent=4, default=str)
            print(f"分析结果已保存到: {args.json}")
        else:
            # 显示格式化结果
            process_results(results, args.summary)
        
        return 0
        
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        if args.debug:
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main()) 