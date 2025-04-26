# Slither Enhanced

Slither Enhanced 是针对 [Slither 安全分析工具](https://github.com/crytic/slither) 的增强插件，专注于改进智能合约安全分析能力，特别是针对DeFi应用的安全检查。

## 📢 项目状态声明

⚠️ **重要提示**：
- 本项目是个人的尝试开发的作品，目前处于**早期开发阶段**
- 代码可能存在多处问题，架构和API可能会有重大变更
- **暂不接受外部贡献或协作请求**
- 仅作为个人学习和研究的记录

## 主要特点

- **区间分析引擎**: 先进的数值边界分析，提高整数溢出和下溢检测准确性
- **DeFi特定检测器**: 专为DeFi协议设计的漏洞检测器
  - **闪电贷回调风险检测器**: 识别闪电贷回调函数中的风险模式
  - **无界闪电贷风险检测器**: 发现可能导致无界闪电贷风险的设计缺陷
  - **未检查余额变更检测器**: 检测代币转移后未验证余额变更的情况
- **改进的报告输出**: 增强可读性的终端输出和交互式HTML报告

## 安装

### 从源码安装

```bash

# 安装插件
pip install -e .
```

### 依赖项

- Python 3.8+
- Slither 0.9.0+


## 架构

```
slither_enhanced/
├── docs/                     # 文档
├── scripts/                  # 实用脚本
├── src/                      # 源代码
│   ├── python_module/        # 模块核心
│   │   ├── detectors/        # 自定义检测器
│   │   │   ├── FlashLoanCallback/      # 闪电贷回调检测器
│   │   │   ├── UncheckedTokenBalanceChange/ # 未检查余额变更检测器
│   │   │   ├── UnboundedFlashLoanRisk/      # 无界闪电贷风险检测器
│   │   │   ├── IntervalViolationDetector/   # 区间违规检测器
│   │   │   |── numerical_anomalies.py       # 数值异常检测器
|   |   |   └── ...                          # 正在修改调整中
│   │   └── interval_analysis/  # 区间分析模块
│   ├── frontend/             # 前端界面
│   │   ├── terminal/         # 终端报告可视化
│   │   ├── staticWeb/        # 静态HTML报告页面
│   │   └── web/              # Web UI
├── test/                     # 测试用例
│   ├── TestContracts/        # 测试合约
│   ├── scripts/              # 测试脚本
│   └── results/              # 测试结果
└── setup.py                  # 安装配置
```


## 快速开始

### 基本用法

Slither Enhanced 可以像标准 Slither 一样使用，但提供了额外的检测器和分析能力:

```bash
# 运行原始Slither
slither contract.sol

# 仅使用特定的增强检测器
slither contract.sol --detect flashloan-callback-risks

interval-analyze contract.sol
```

### 检测器列表

Slither Enhanced暂时包含以下检测器:

- `flashloan-callback-risks`: 检测闪电贷回调函数中的风险模式
- `unbounded-flashloan-risk`: 检测可能导致无界闪电贷风险的设计缺陷
- `unchecked-balance-change`: 检测代币转移后未验证余额变更的情况
- `interval-violation`: 使用区间分析检测整数相关的安全问题
- `interval-numerical-anomalies`: 检测基于区间分析的数值异常情况

### 区间分析

区间分析是Slither Enhanced的核心功能，可用于精确追踪智能合约中变量的数值范围:

详细信息请参阅 [区间分析使用说明](docs/INTERVAL_ANALYSIS.md)。

## 测试框架

Slither Enhanced 包含全面的测试框架，用于评估和比较增强版与原始Slither的性能：

详细的测试框架说明请参阅 [测试框架文档](test/README.md)。


## 示例

```bash
# 示例1：检测闪电贷回调风险
slither contract.sol --detect flashloan-callback-risks

# 示例2：结合多个检测器
slither contract.sol --detect flashloan-callback-risks,unbounded-flashloan-risk,unchecked-balance-change

# 示例3：生成详细报告
slither contract.sol --json report.json --detect interval-violation,interval-numerical-anomalies 
```

## 贡献

⚠️ **注意**：本项目处于早期开发阶段。

目前**不接受**外部贡献、协作或合并请求。此存储库主要用于记录个人学习和研究工作。

## 许可证

本项目采用 [AGPL-3.0](LICENSE) 许可证。它是基于 [Slither](https://github.com/crytic/slither) (同样采用AGPL-3.0) 开发的。测试中使用的数据集部分来源于 [SmartBugs Curated Dataset](https://github.com/smartbugs/smartbugs-curated/tree/main)，该数据集采用MIT许可证。 

### 致谢

特别感谢[Slither项目](https://github.com/crytic/slither)和其维护者提供的出色工具，本项目作为对该工具的扩展和增强尝试，遵循其开源精神和规范。