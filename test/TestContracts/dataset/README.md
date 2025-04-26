# SmartBugs精选数据集

本目录包含从[SmartBugs精选数据集](https://github.com/smartbugs/smartbugs-curated/tree/main)获取的智能合约样本，用于测试Slither增强插件的漏洞检测性能。

## 数据集来源

数据集源自SmartBugs项目，这是一个用于评估智能合约安全分析工具的公开数据集集合。我们选取了其中四个关键漏洞类别的合约，用于对比Slither原版和增强版的检测能力。

数据集原始地址: [https://github.com/smartbugs/smartbugs-curated/tree/main](https://github.com/smartbugs/smartbugs-curated/tree/main)

## 数据集结构

当前数据集包含以下漏洞类别:

1. **arithmetic** - 算术漏洞（整数溢出/下溢等）
2. **reentrancy** - 重入攻击漏洞
3. **access_control** - 访问控制漏洞
4. **denial_of_service** - 拒绝服务漏洞

每个类别目录中包含:
- 示例漏洞合约
- README.md文件，描述该类别的特点和包含的合约
- 原始的漏洞信息

## 用途说明

这些数据集用于两个主要目的:

1. **对比测试** - 评估Slither增强版在现有检测器功能上的改进
2. **新能力测试** - 验证新增检测器对特定漏洞类型的识别能力

通过对完全相同的样本运行原版和增强版Slither，我们可以直接比较两者的检测能力差异，特别是在以下方面:

- 检出率改进
- 检测准确性
- 严重性评估的准确性
- 误报率降低

## 测试配置

在`test_configs.json`中，可以配置要测试的特定合约样本:

```json
"smartbugs_selected_contracts": {
  "arithmetic": [
    "integer_overflow_mul.sol",
    "overflow_simple_add.sol",
    "tokensalechallenge.sol",
    "BECToken.sol"
  ],
  "reentrancy": [
    "reentrancy_cross_function.sol",
    "reentrancy_dao.sol",
    "etherbank.sol",
    "spank_chain_payment.sol"
  ]
  // ...其他类别
}
```

## 许可说明

SmartBugs数据集采用MIT许可证。使用这些数据用于学术研究和工具评估是被允许的，但在发布结果时应当引用原始SmartBugs项目。

## 引用信息

如果使用此数据集进行研究，请引用以下论文:

```
@article{smartbugs,
  title={SmartBugs: A Framework to Analyze Solidity Smart Contracts},
  author={Ferreira Torres, Christof and Baden, Michael and Norvill, Robert and Jonker, Hugo},
  journal={IEEE Access},
  year={2020}
}
``` 