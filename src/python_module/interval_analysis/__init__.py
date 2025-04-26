from .range_analysis import IntervalAnalysisLauncher, DeFiRangeAnalyzer, Interval, DeFiRangeViolationDetector
import json
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("IntervalAnalysis")

def create_analyzer(compilation_unit):
    """
    创建区间分析器实例
    
    Args:
        compilation_unit: Slither编译单元对象
        
    Returns:
        DeFiRangeAnalyzer: 区间分析器实例
    """
    return DeFiRangeAnalyzer(compilation_unit)

def launch_analysis(compilation_unit):
    """
    启动区间分析
    
    Args:
        compilation_unit: Slither编译单元对象
        
    Returns:
        list: 分析结果列表
    """
    launcher = IntervalAnalysisLauncher(compilation_unit)
    return launcher.launch()

def get_analysis_summary(compilation_unit):
    """
    获取区间分析摘要
    
    Args:
        compilation_unit: Slither编译单元对象
        
    Returns:
        dict: 函数区间分析摘要
    """
    launcher = IntervalAnalysisLauncher(compilation_unit)
    launcher.launch()
    return launcher.get_summary()

def get_compilation_unit(slither):
    """
    获取compilation_unit，适配不同版本的Slither
    
    Args:
        slither: Slither对象
        
    Returns:
        compilation_unit: Slither编译单元对象
    """
    if hasattr(slither, 'compilation_unit'):
        return slither.compilation_unit
    elif hasattr(slither, '_compilation_units') and len(slither._compilation_units) > 0:
        # 较新版本的Slither可能使用_compilation_units列表
        return slither._compilation_units[0]
    else:
        # 如果以上方法都失败，尝试直接使用slither对象
        logger.warning("无法获取compilation_unit，尝试使用slither对象代替")
        return slither

def analyze_file(file_path, output_json=None, summary=False):
    """
    简化的API入口点，适合大语言模型调用
    
    此函数提供了一个简单的接口，可以直接分析Solidity文件
    或项目，并返回分析结果。可选择输出为JSON文件或获取函数摘要。
    
    Args:
        file_path (str): 合约文件或项目目录路径
        output_json (str, optional): 输出JSON文件路径
        summary (bool, optional): 是否生成函数摘要
        
    Returns:
        分析结果（列表或字典）
    """
    from slither.slither import Slither
    
    try:
        # 初始化Slither
        slither = Slither(file_path)
        
        # 获取compilation_unit
        compilation_unit = get_compilation_unit(slither)
        
        # 执行分析
        if summary:
            results = get_analysis_summary(compilation_unit)
        else:
            results = launch_analysis(compilation_unit)
        
        # 输出JSON
        if output_json:
            with open(output_json, 'w') as f:
                json.dump(results, f, indent=4, default=str)
            logger.info(f"分析结果已保存到: {output_json}")
        
        return results
    
    except Exception as e:
        logger.error(f"分析过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return None

# 声明可导出的所有组件
__all__ = [
    'IntervalAnalysisLauncher', 
    'DeFiRangeAnalyzer', 
    'Interval',
    'DeFiRangeViolationDetector',
    'create_analyzer', 
    'launch_analysis',
    'get_analysis_summary',
    'analyze_file',
    'get_compilation_unit'
] 