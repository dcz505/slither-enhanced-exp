// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title IntervalOverflow
 * @dev 用于测试区间分析模块的合约
 * 包含各种可能的数值边界问题
 */
contract IntervalOverflow {
    uint256 public maxSupply = 1_000_000 * 10**18;       // 最大供应量：100万代币
    uint256 public circulatingSupply;                    // 当前流通量
    uint256 public constant MAX_MINT_PER_TX = 10000 * 10**18; // 每次最多铸造1万代币
    
    mapping(address => uint256) public balances;
    mapping(address => bool) public isWhitelisted;
    
    uint256 public feePercentage = 3;                   // 3% 费率
    uint256 public constant MAX_FEE_PERCENTAGE = 10;     // 最大10%
    
    address public owner;
    
    constructor() {
        owner = msg.sender;
        isWhitelisted[msg.sender] = true;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    // 基本的铸造函数
    function mint(uint256 amount) external {
        require(amount <= MAX_MINT_PER_TX, "Exceeds max mint amount");
        require(circulatingSupply + amount <= maxSupply, "Exceeds max supply");
        
        circulatingSupply += amount;
        balances[msg.sender] += amount;
    }
    
    // 包含数学计算的函数 - 可能存在溢出风险
    function compoundInterest(uint256 principal, uint256 rate, uint256 periods) external pure returns (uint256) {
        uint256 result = principal;
        
        // 危险：周期数过多时会产生溢出
        for (uint256 i = 0; i < periods; i++) {
            result = result + (result * rate / 100);
        }
        
        return result;
    }
    
    // 含有区间分析困难的复杂计算
    function calculateReward(uint256 amount, uint256 duration) external view returns (uint256) {
        // 基础奖励率
        uint256 baseRate = 5;
        
        // 时间奖励因子 - 最多额外10%
        uint256 timeFactor = duration > 365 days ? 10 : (duration * 10 / 365 days);
        
        // 金额奖励因子 - 最多额外5%
        uint256 amountFactor = amount > 10000 * 10**18 ? 5 : (amount * 5 / (10000 * 10**18));
        
        // 总奖励率
        uint256 totalRate = baseRate + timeFactor + amountFactor;
        
        // 危险：这里可能产生较大数值
        return amount * totalRate / 100;
    }
    
    // 不安全的除法
    function unsafeDivision(uint256 a, uint256 b) external pure returns (uint256) {
        // 危险：未检查被除数是否为0
        return a / b;
    }
    
    // 不安全的权重计算
    function calculateWeightedAverage(uint256[] calldata values, uint256[] calldata weights) external pure returns (uint256) {
        require(values.length == weights.length, "Array length mismatch");
        
        uint256 sum = 0;
        uint256 weightSum = 0;
        
        for (uint256 i = 0; i < values.length; i++) {
            // 危险：可能溢出
            sum += values[i] * weights[i];
            weightSum += weights[i];
        }
        
        // 危险：除以0风险
        return sum / weightSum;
    }
    
    // 复杂路径中的边界问题
    function complexPathCalculation(uint256 input, bool useAlternativePath) external pure returns (uint256) {
        uint256 result;
        
        if (useAlternativePath) {
            // 路径1：加法和乘法组合
            result = input * 3;
            if (input > 1000) {
                result = result + (input * input / 1000);
            }
        } else {
            // 路径2：除法和指数组合
            if (input > 0) {
                uint256 factor = 10000 / input;
                // 危险：快速增长的指数
                result = factor * factor;
            } else {
                result = 0;
            }
        }
        
        return result;
    }
    
    // 设置费率
    function setFeePercentage(uint256 newFeePercentage) external onlyOwner {
        require(newFeePercentage <= MAX_FEE_PERCENTAGE, "Fee too high");
        feePercentage = newFeePercentage;
    }
    
    // 更新最大供应量
    function updateMaxSupply(uint256 newMaxSupply) external onlyOwner {
        // 危险：未检查新最大供应量与当前流通量的关系
        maxSupply = newMaxSupply;
    }
    
    // 跨函数的区间分析用例
    function transfer(address to, uint256 amount) external returns (bool) {
        return _transfer(msg.sender, to, amount);
    }
    
    function _transfer(address from, address to, uint256 amount) internal returns (bool) {
        require(from != address(0), "Transfer from zero address");
        require(to != address(0), "Transfer to zero address");
        require(balances[from] >= amount, "Insufficient balance");
        
        // 计算费用 - 可能引入舍入误差
        uint256 fee = (amount * feePercentage) / 100;
        uint256 transferAmount = amount - fee;
        
        // 更新余额
        balances[from] -= amount;
        balances[to] += transferAmount;
        
        // 费用给所有者
        balances[owner] += fee;
        
        return true;
    }
} 