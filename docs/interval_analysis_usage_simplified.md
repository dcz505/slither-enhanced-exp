# 区间分析工具使用指南（简化版）

## 命令行工具使用方法

1. 基本分析
```
python -m slither.slither_enhanced.src.python_module.interval_analysis.cli_fixed <合约文件路径>
```

2. 生成摘要报告
```
python -m slither.slither_enhanced.src.python_module.interval_analysis.cli_fixed <合约文件路径> --summary
```

3. 保存JSON结果
```
python -m slither.slither_enhanced.src.python_module.interval_analysis.cli_fixed <合约文件路径> --json results.json
```

## 示例脚本使用方法

1. 分析SimpleSwap示例合约
```
python ./slither/slither_enhanced/scripts/interval_analysis_example_fixed.py
```

2. 分析测试合约
```
python ./slither/slither_enhanced/scripts/interval_analysis_test_contract.py
```

## 疑难解答

如果遇到导入问题，请确保：
1. 设置正确的Python路径
2. 使用正确的导入：`from slither.slither import Slither`
3. 正确获取compilation_unit 