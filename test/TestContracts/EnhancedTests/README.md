# 增强型测试合约集

本目录包含专门设计的智能合约，用于测试Slither增强插件模块的检测能力。每个合约都包含有意引入的漏洞或风险模式，这些漏洞或风险模式可以被相应的检测器识别。

## 目录结构

测试合约按检测器类型分组：

### 1. NumericalAnalysis - 数值分析检测器测试

- `IntervalNumericOverflow.sol`: 包含各种数值溢出、下溢和除零风险的合约
- `DefiRangeViolation.sol`: 包含DeFi特定的范围约束违规的合约

### 2. FlashloanVulnerability - 闪电贷相关漏洞测试

- `FlashloanCallbackInsecure.sol`: 测试闪电贷回调安全问题的合约
- `UnboundedFlashloanRisk.sol`: 测试无边界闪电贷和费用缺失风险的合约

### 3. TokenBalance - 代币余额检测测试

- `UncheckedTokenBalance.sol`: 测试代币余额变化未检查的合约

### 4. Mixed - 混合漏洞测试

- `DeFiProtocolWithMultipleVulnerabilities.sol`: 包含多种漏洞的复杂DeFi协议合约

## 合约说明

### IntervalNumericOverflow.sol

该合约展示了各种可能的数值问题，包括：
- 大数乘法导致的溢出
- 除零错误
- 精度损失
- 变量取值约束违反
- uint8 溢出
- 复杂计算中的多个潜在问题

### DefiRangeViolation.sol

该合约包含DeFi场景中常见的区间违规问题：
- 贷款价值比(LTV)超出安全限制
- 清算阈值设置不当
- 费率设置异常
- 抵押率设置过低
- 流动性不足
- 价格操纵风险

### FlashloanCallbackInsecure.sol

该合约展示了闪电贷回调中的安全问题：
- 缺少发送者验证
- 缺少重入保护
- 回调中的不安全状态变量修改
- 危险的外部调用
- 上下文操纵

### UnboundedFlashloanRisk.sol

该合约演示了闪电贷实现中的常见风险：
- 缺少贷款上限
- 没有收取闪电贷费用
- 不安全的回调处理
- 缺少返还验证

### UncheckedTokenBalance.sol

该合约包含代币处理中常见的余额检查缺失问题：
- 转账后未验证实际收到的代币数量
- 批量转账未检查成功状态
- 代币交换未验证输入输出数量
- 签名验证不足
- 与安全实现对比

### DeFiProtocolWithMultipleVulnerabilities.sol

一个综合性的DeFi协议合约，包含多种漏洞：
- 未检查算术操作
- 无边界闪电贷
- 不安全的闪电贷回调
- DeFi范围违规
- 清算过程中的余额检查缺失

## 使用方法

这些合约专为测试Slither增强插件模块的检测能力而设计。使用这些合约进行测试时，应该能够观察到以下检测器的触发：

1. `interval-numerical-anomalies`：数值异常检测器
2. `flashloan-callback-risks`：闪电贷回调风险检测器
3. `interval-violation`：区间违规检测器
4. `defi-range-violation`：DeFi区间违规检测器
5. `unbounded-flashloan-risk`：无边界闪电贷风险检测器
6. `unchecked-balance-change`：代币余额未检查检测器

测试命令示例：

```bash
slither path/to/contract.sol --detect interval-numerical-anomalies,flashloan-callback-risks,interval-violation,defi-range-violation,unbounded-flashloan-risk,unchecked-balance-change
```

## 注意事项

1. 这些合约**故意**包含漏洞，不应在生产环境中使用
2. 所有合约使用Solidity 0.8.17编译，确保与现代编译器兼容
3. 合约中的漏洞已通过注释清晰标记
4. 某些合约包含正确的实现作为参考对比 