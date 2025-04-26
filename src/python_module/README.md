# Slither Enhanced

该模块为Slither_enhanced中的区间分析和检测器模块

## 具体已集成的检测器

1.  **Numerical Anomalies（数值异常）:** 检测潜在的数值问题 (`numerical_anomalies.py`)。
   该检测器基于区间分析能力，可以检测智能合约中的数值溢出/下溢风险、除零错误、DeFi特定的数值约束违规和不合理的数值操作。过滤掉低置信度的警告，只保留高可信度的发现，减少误报率。
   
2.  **Flash Loan Callback（闪电贷回调）:** 检测是否存在闪电贷回调风险 (`FlashLoanCallback/`)。
   该检测器识别合约中的闪电贷回调函数，并检查三类常见风险：状态变量的不安全修改、缺失重入保护以及在状态更新后进行外部调用。支持主流DeFi协议（如Uniswap、AAVE、Compound等）的闪电贷回调函数识别。
   
3.  **Interval Violation Detector （区间违规）:** 在区间分析增强模块基础上进行的区间分析，识别合约中的区间违规行为 (`IntervalViolationDetector/`)。
   该检测器关注智能合约中变量的取值区间是否违反预期约束，能够检测到数据范围、价值限制和资产比率等方面的违规情况。
   
4.  **Unbounded Flash Loan Risk（无边界闪电贷风险）:** 检测闪电贷无边界相关风险 (`UnboundedFlashLoanRisk/`)。
   该检测器主要识别合约中没有对闪电贷金额设置上限的情况，这可能导致协议遭受大金额攻击，以及识别缺乏闪电贷费用机制的合约。
   
5.  **Unchecked Token Balance Change（代币余额未检查）:** 标记可能未正确检查代币余额变化的情况 (`UncheckedTokenBalanceChange/`)。
   该检测器关注在转账、提款或其他资金移动后没有验证余额变化的智能合约，这种情况可能导致资金丢失或被劫持。

## 区间分析增强模块

区间分析增强模块 (`interval_analysis/`) 是一个专门针对DeFi智能合约的静态分析工具，提供以下功能：

1. **变量区间跟踪**：跟踪智能合约中变量的可能取值范围，帮助发现潜在的数值问题。

2. **路径敏感分析**：根据不同执行路径，针对性分析变量取值区间，提高分析准确度。

3. **DeFi特性优化**：针对DeFi特有的场景（如AMM、借贷协议等）进行了优化，能够更准确地分析价格、比率和金额等关键变量。

4. **API集成**：提供简单的API接口，可以轻松集成到Slither工具链中，或被其他模块调用。

5. **可视化支持**：支持将分析结果输出为JSON格式，便于后续可视化或进一步处理。

主要组件包括：
- `IntervalAnalysisLauncher`：区间分析启动器，协调整个分析过程
- `DeFiRangeAnalyzer`：针对DeFi场景的区间分析器
- `Interval`：表示数值区间的基础类
- `DeFiRangeViolationDetector`：基于区间分析的违规检测器

使用方法：
```python
from slither_enhanced.src.python_module.interval_analysis import analyze_file

# --detect interval-numerical-anomalies,flashloan-callback-risks,interval-violation,defi-range-violation,unbounded-flashloan-risk,unchecked-balance-change
```


# 分析合约文件
results = analyze_file("path/to/contract.sol")

# 输出为JSON文件
results = analyze_file("path/to/contract.sol", output_json="results.json")

# 获取函数摘要
summary = analyze_file("path/to/contract.sol", summary=True)
```

