# Slither Enhanced 测试合约集

此目录包含一系列专门设计用于测试 Slither Enhanced 插件功能的智能合约。这些合约故意包含各种漏洞和边界情况，以验证插件的检测能力。

## 合约说明

### 1. UncheckedBalanceChange.sol

该合约模拟了代币合约中未经检查的余额变更漏洞，包含以下风险点：
- 直接修改用户余额而不进行权限检查
- 更新余额时没有保持状态一致性
- 批量转账中缺少余额检查

### 2. UnboundedFlashLoanRisk.sol

该合约演示了闪电贷回调中的无界状态更改风险，包含以下风险点：
- 在闪电贷回调中直接修改关键价格数据
- 无限制地增加用户余额和借款额度
- 缺少对状态变量修改的边界限制

### 3. IntervalAnalysisTest.sol

该合约包含各种算术和数值操作，用于测试区间分析功能：
- 基本算术运算（加减乘除、取模）的边界情况
- 指数运算可能导致的溢出
- 价格更新和汇率计算中的无界输入
- 复合利息计算中的复杂算式
- 位操作和移位运算

### 4. FlashLoanCallbackTest.sol

该合约展示了闪电贷回调中的各种安全风险：
- 缺少重入保护的闪电贷回调函数
- 不当的状态更新顺序（违反检查-效果-交互模式）
- 未经保护的外部调用
- 安全实现与不安全实现的对比

## 使用方法

### 检测未检查的代币余额变更：

```bash
slither slither/slither_enhanced/test/TestContracts/UncheckedBalanceChange.sol --detect unchecked-balance-change
```

### 检测无限制闪电贷风险：

```bash
slither slither/slither_enhanced/test/TestContracts/UnboundedFlashLoanRisk.sol --detect unbounded-flashloan-risk
```

### 检测闪电贷回调风险：

```bash
slither slither/slither_enhanced/test/TestContracts/FlashLoanCallbackTest.sol --detect flashloan-callback-risks
```

### 执行区间分析：

```bash
slither slither/slither_enhanced/test/TestContracts/IntervalAnalysisTest.sol --detect interval-violation
```

### 运行所有检测器：

```bash
slither slither/slither_enhanced/test/TestContracts/* --detect unchecked-balance-change,unbounded-flashloan-risk,flashloan-callback-risks
```

### 生成JSON报告：

```bash
slither slither/slither_enhanced/test/TestContracts/UncheckedBalanceChange.sol --json report.json --detect unchecked-balance-change
```

## 可视化结果

生成JSON报告后，可以使用Slither Enhanced的可视化工具查看结果：

### 终端可视化：

```bash
python -m slither_enhanced.src.frontend.terminal.report_visualizer --report report.json
```

### 静态网页展示：

将`report.json`拖放到`slither_enhanced/src/frontend/staticWeb/index.html`页面中查看。 