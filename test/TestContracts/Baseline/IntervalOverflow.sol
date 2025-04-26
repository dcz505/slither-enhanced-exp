// SPDX-License-Identifier: MIT
pragma solidity ^0.7.6;

/**
 * @title IntervalOverflow
 * @dev 此合约用于测试区间分析检测器
 *      包含多种类型的潜在数值溢出风险
 *      使用0.7.6版本是为了演示未使用SafeMath时的溢出问题
 */
contract IntervalOverflow {
    // 状态变量
    uint256 public totalSupply;
    mapping(address => uint256) public balances;
    
    // 初始化
    constructor(uint256 initialSupply) {
        totalSupply = initialSupply;
        balances[msg.sender] = initialSupply;
    }
    
    // 简单的加法溢出风险
    function unsafeAdd(uint256 a, uint256 b) public pure returns (uint256) {
        return a + b; // Solidity 0.7.6 不会自动检查溢出
    }
    
    // 乘法溢出风险
    function unsafeMultiply(uint256 a, uint256 b) public pure returns (uint256) {
        return a * b; // 可能溢出
    }
    
    // 链式运算溢出风险
    function chainedOperations(uint256 a, uint256 b, uint256 c) public pure returns (uint256) {
        return a + b * c; // b * c 可能溢出，或最终结果可能溢出
    }
    
    // 复杂表达式溢出风险
    function complexExpression(uint256 a, uint256 b) public pure returns (uint256) {
        uint256 c = a * 2;
        uint256 d = b * b;
        return c + d; // 多个步骤都可能溢出
    }
    
    // 条件分支中的溢出风险
    function conditionalOverflow(uint256 a, uint256 b) public pure returns (uint256) {
        if (a > 100 && b > 100) {
            return a * b; // 在这些条件下，高概率溢出
        } else {
            return a + b; // 可能溢出，但概率较低
        }
    }
    
    // 除零风险
    function unsafeDivision(uint256 a, uint256 b) public pure returns (uint256) {
        return a / b; // 如果b为0，将导致除零错误
    }
    
    // 下溢风险
    function unsafeSubtraction(uint256 a, uint256 b) public pure returns (uint256) {
        return a - b; // 如果b > a，将导致下溢
    }
    
    // 环路中的溢出风险
    function loopAddition(uint256 iterations, uint256 value) public pure returns (uint256) {
        uint256 result = 0;
        for (uint256 i = 0; i < iterations; i++) {
            result += value; // 可能在某次迭代中溢出
        }
        return result;
    }
    
    // 转账函数中的溢出风险
    function unsafeTransfer(address to, uint256 amount) public {
        balances[msg.sender] -= amount; // 可能下溢
        balances[to] += amount; // 可能溢出
    }
    
    // 安全转账实现
    function safeTransfer(address to, uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // 检查接收方余额溢出
        require(balances[to] + amount >= balances[to], "Balance overflow");
        
        balances[msg.sender] -= amount;
        balances[to] += amount;
    }
} 