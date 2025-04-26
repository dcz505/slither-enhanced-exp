#!/usr/bin/env python3

"""
Slither Enhanced 终端报告可视化工具

该工具用于在终端中以格式化方式展示智能合约审计报告
支持显示漏洞详情和区间分析结果
"""

import os
import json
import argparse
import sys
from datetime import datetime
from pathlib import Path
import shutil

# 检查rich库是否存在，如果不存在，提供安装建议
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text
    from rich.tree import Tree
    from rich.progress import track
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich import box
except ImportError:
    print("错误: 未找到必要的依赖库 'rich'")
    print("请通过以下命令安装: pip install rich")
    sys.exit(1)

# 创建控制台对象
console = Console()

# 获取终端宽度
TERM_WIDTH = shutil.get_terminal_size().columns

# 颜色定义，对应不同的严重程度
SEVERITY_COLORS = {
    "high": "red",
    "medium": "yellow",
    "low": "green",
    "informational": "blue",
    "Optimization": "cyan",
}

def format_timestamp(timestamp):
    """将时间戳格式化为可读格式"""
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(timestamp)

def print_header(report_path, data):
    """打印报告头部信息"""
    console.print("\n")
    
    # 创建标题面板
    title = Text("Slither Enhanced 智能合约审计报告", style="bold white on blue")
    panel = Panel(
        title,
        width=min(100, TERM_WIDTH),
        box=box.DOUBLE,
        border_style="blue",
    )
    console.print(panel)
    
    # 报告基本信息
    summary = data.get("summary", {})
    report_time = summary.get("audit_time", "未知")
    file_name = Path(report_path).name
    
    info_table = Table(width=min(100, TERM_WIDTH))
    info_table.add_column("属性", style="cyan")
    info_table.add_column("值")
    
    info_table.add_row("报告文件", file_name)
    info_table.add_row("分析时间", report_time)
    info_table.add_row("Solidity版本", summary.get("solc_version", "未知"))
    info_table.add_row("分析文件数", str(summary.get("file_count", 0)))
    
    console.print(info_table)
    console.print("\n")

def print_summary(data):
    """打印漏洞摘要信息"""
    summary = data.get("summary", {})
    vulnerability_counts = summary.get("vulnerabilities", {})
    
    if not vulnerability_counts:
        console.print("[yellow]未发现漏洞或者报告格式不正确[/yellow]")
        return
    
    # 创建摘要表格
    summary_table = Table(title="漏洞摘要", width=min(100, TERM_WIDTH))
    summary_table.add_column("严重程度", style="bold")
    summary_table.add_column("数量", justify="right")
    summary_table.add_column("状态", justify="center")
    
    for severity, count in vulnerability_counts.items():
        color = SEVERITY_COLORS.get(severity, "white")
        status = "⚠️ 需要修复" if severity in ["high", "medium"] else "📝 建议修复"
        summary_table.add_row(f"[{color}]{severity.capitalize()}[/{color}]", str(count), status)
    
    console.print(summary_table)
    
    # 显示合约列表
    if "contracts" in summary and summary["contracts"]:
        console.print("\n[bold cyan]分析的合约:[/bold cyan]")
        for contract in summary["contracts"]:
            console.print(f"  • {contract}")
    
    console.print("\n")

def print_findings(data):
    """打印详细的漏洞发现信息"""
    findings = data.get("vulnerabilities", [])
    if not findings:
        console.print("[yellow]未发现漏洞[/yellow]")
        return
    
    console.print(Panel("漏洞详情", width=min(100, TERM_WIDTH), style="bold"))
    
    # 按严重程度排序漏洞
    severity_order = {"high": 0, "medium": 1, "low": 2, "informational": 3}
    findings.sort(key=lambda x: severity_order.get(x.get("severity", "").lower(), 999))
    
    for i, finding in enumerate(findings):
        # 获取漏洞信息
        severity = finding.get("severity", "unknown").lower()
        confidence = finding.get("confidence", "unknown")
        name = finding.get("name", "未知漏洞")
        description = finding.get("description", "无描述")
        
        # 创建漏洞面板
        color = SEVERITY_COLORS.get(severity, "white")
        finding_id = f"[{i+1}] [{color}]{name}[/{color}]"
        
        finding_panel = Panel(
            Text(description),
            title=finding_id,
            title_align="left",
            width=min(100, TERM_WIDTH),
            border_style=color,
        )
        
        console.print(finding_panel)
        
        # 创建元数据表格
        meta_table = Table(width=min(100, TERM_WIDTH)-4, box=box.SIMPLE)
        meta_table.add_column("属性", style="cyan", width=12)
        meta_table.add_column("值")
        
        meta_table.add_row("严重程度", f"[{color}]{severity.capitalize()}[/{color}]")
        meta_table.add_row("可信度", confidence.capitalize())
        
        console.print(meta_table)
        
        # 显示漏洞位置
        locations = finding.get("locations", [])
        if locations:
            console.print("\n[bold]漏洞位置:[/bold]")
            for location in locations:
                file = location.get("file", "未知文件")
                contract = location.get("contract", "")
                function = location.get("function", "")
                line = location.get("line", 0)
                
                location_str = f"{file}"
                if contract:
                    location_str += f", 合约: {contract}"
                if function:
                    location_str += f", 函数: {function}"
                if line:
                    location_str += f", 行: {line}"
                
                console.print(f"  📍 [cyan]{location_str}[/cyan]")
        
        # 显示修复建议
        recommendation = finding.get("recommendation", "")
        if recommendation:
            console.print("\n[bold]修复建议:[/bold]")
            console.print(f"  🔧 [green]{recommendation}[/green]")
        
        console.print("\n" + "-" * min(100, TERM_WIDTH) + "\n")

def print_interval_analysis(data):
    """打印区间分析结果"""
    interval_analysis = data.get("interval_analysis", {})
    if not interval_analysis:
        console.print("[yellow]未找到区间分析结果[/yellow]")
        return
    
    console.print(Panel("区间分析结果", width=min(100, TERM_WIDTH), style="bold cyan"))
    console.print("[italic]区间分析帮助识别变量可能的取值范围，防止溢出和其他数值相关问题[/italic]\n")
    
    # 创建合约和函数的树状视图
    for contract_name, functions in interval_analysis.items():
        contract_tree = Tree(f"[bold blue]{contract_name}[/bold blue]")
        
        for function_name, data in functions.items():
            function_branch = contract_tree.add(f"[bold cyan]{function_name}[/bold cyan]")
            
            # 显示参数区间
            if "params" in data and data["params"]:
                params_branch = function_branch.add("[yellow]参数区间[/yellow]")
                for param, interval in data["params"].items():
                    params_branch.add(f"[green]{param}[/green]: {interval}")
            
            # 显示返回值区间
            if "return" in data and data["return"]:
                return_branch = function_branch.add("[yellow]返回值区间[/yellow]")
                for ret, interval in data["return"].items():
                    return_branch.add(f"[green]{ret}[/green]: {interval}")
        
        console.print(contract_tree)
        console.print()

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description="Slither Enhanced 终端报告可视化工具")
    parser.add_argument("--report", "-r", required=True, help="JSON报告文件路径")
    parser.add_argument("--no-interval", action="store_true", help="不显示区间分析结果")
    parser.add_argument("--only-summary", action="store_true", help="只显示摘要信息")
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    # 检查报告文件是否存在
    if not os.path.exists(args.report):
        console.print(f"[red]错误: 找不到报告文件 '{args.report}'[/red]")
        return 1
    
    try:
        # 尝试加载JSON文件
        with open(args.report, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        console.print(f"[red]错误: 无法解析JSON文件 '{args.report}'[/red]")
        return 1
    except Exception as e:
        console.print(f"[red]错误: 读取文件时出错: {str(e)}[/red]")
        return 1
    
    # 清屏
    os.system('cls' if os.name == 'nt' else 'clear')
    
    # 显示报告
    print_header(args.report, data)
    print_summary(data)
    
    if not args.only_summary:
        print_findings(data)
        
        # 显示区间分析结果
        if not args.no_interval:
            print_interval_analysis(data)
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 