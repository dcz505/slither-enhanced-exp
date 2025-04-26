# Slither 增强版测试指南

本目录包含用于测试 Slither 增强版插件模块的脚本和工具。这些测试脚本可以评估增强版在不同测试集上的性能表现，并生成可视化的评估报告。

## 测试集说明

测试系统支持以下测试集：

1. **基准测试集** (`../TestContracts/Baseline/`): 基础合约测试集，用于评估插件的基本功能。
2. **SmartBugs数据集** (`../TestContracts/dataset/`): 从 SmartBugs 提取的数据集，包含各种类型的漏洞。
3. **区间分析测试集** (如果存在): 专门用于测试区间分析功能的合约集。

## 快速开始

### Windows 系统

在 Windows 系统上，直接运行以下命令：

```
.\run_enhanced_test.bat
```

### Linux/MacOS 系统

在 Linux 或 MacOS 系统上，请先确保脚本有执行权限，然后运行：

```
chmod +x run_enhanced_test.sh
./run_enhanced_test.sh
```

## 高级用法

两个脚本都支持以下命令行参数：

- `--max-files N`: 每个测试集最多测试的文件数，默认为 5
- `--output-dir DIR`: 结果输出目录，默认为 `../results`
- `--test-sets SETS`: 要测试的测试集，逗号分隔，默认为 `baseline,smartbugs`
- `--verbose`: 显示详细输出
- `--help`: 显示帮助信息

例如，如果只想测试 SmartBugs 数据集中的 10 个合约：

```
.\run_enhanced_test.bat --test-sets smartbugs --max-files 10
```

## 测试输出

测试完成后，结果将保存在指定的输出目录（默认为 `../results/evaluation_[时间戳]`）中，包括：

1. 详细的 CSV 格式测试结果
2. 可视化图表（需要安装 matplotlib 和 seaborn）
3. Markdown 格式的评估报告

## 主要测试脚本说明

- `slither_test_runner.py`: 主测试脚本，执行实际的测试和评估
- `run_enhanced_test.bat`: Windows 系统下的便捷启动脚本
- `run_enhanced_test.sh`: Linux/MacOS 系统下的便捷启动脚本

## 注意事项

1. 测试前请确保 Slither 已正确安装并可在命令行中使用
2. 为获得完整的评估报告和图表，请安装 pandas, numpy, matplotlib 和 seaborn 包
3. 测试过程可能需要较长时间，特别是在测试大量合约或使用复杂检测器时

## 测试脚本开发

如需修改或扩展测试脚本，请参考 `slither_test_runner.py` 的源代码及注释。主要的扩展点包括：

1. 添加新的测试集目录
2. 扩展检测器配置
3. 定制评估指标和可视化方式 