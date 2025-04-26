// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/**
 * @title IntervalNumericOverflow
 * @dev A contract demonstrating various numerical issues that can be detected by the interval-numerical-anomalies detector
 */
contract IntervalNumericOverflow {
    uint256 public constant MAX_UINT = 2**256 - 1;
    uint256 public constant LARGE_VALUE = 2**255;
    uint8 public constant MAX_UINT8 = 255;
    
    // Stores balances of users
    mapping(address => uint256) public balances;
    
    // Total supply of tokens
    uint256 public totalSupply;
    
    // Exchange rate variables
    uint256 public exchangeRate = 100; // 1:100 ratio
    uint256 public minExchangeRate = 50;
    uint256 public maxExchangeRate = 200;
    
    // Fees
    uint256 public constant FEE_DENOMINATOR = 10000; // 100% = 10000
    uint256 public feePercentage = 30; // 0.3%
    
    /**
     * @dev Function with potential overflow when multiplying large numbers
     */
    function multiplyLargeNumbers(uint256 a) public pure returns (uint256) {
        // Potentially overflows if a > 2^255
        return a * 2;
    }
    
    /**
     * @dev Function with division by potential zero
     */
    function dividePotentialZero(uint256 a, uint256 b) public pure returns (uint256) {
        // Can divide by zero if b = 0
        return a / b;
    }
    
    /**
     * @dev Calculates fee amount with potential precision loss
     */
    function calculateFee(uint256 amount) public view returns (uint256) {
        // Potential precision loss if amount * feePercentage < FEE_DENOMINATOR
        return (amount * feePercentage) / FEE_DENOMINATOR;
    }
    
    /**
     * @dev Updates exchange rate with potential constraint violations
     */
    function updateExchangeRate(uint256 newRate) public {
        // The interval analysis should detect that newRate might violate constraints
        exchangeRate = newRate;
    }
    
    /**
     * @dev Complex calculation with multiple potential numerical issues
     */
    function complexCalculation(uint256 depositAmount, uint256 multiplier) public view returns (uint256) {
        // Multiple potential overflows and constraint violations
        uint256 baseAmount = depositAmount * exchangeRate;
        uint256 bonusAmount = (baseAmount * multiplier) / 100;
        uint256 feeAmount = calculateFee(baseAmount + bonusAmount);
        
        return baseAmount + bonusAmount - feeAmount;
    }
    
    /**
     * @dev Function with uint8 overflow
     */
    function incrementUint8(uint8 value) public pure returns (uint8) {
        // Will overflow if value = 255
        return value + 1;
    }
    
    /**
     * @dev Mint function with potential overflow
     */
    function mint(address account, uint256 amount) public {
        // Potential overflow if totalSupply + amount > MAX_UINT
        // or if balances[account] + amount > MAX_UINT
        totalSupply += amount;
        balances[account] += amount;
    }
    
    /**
     * @dev Function demonstrating unsafe arithmetic with negative range checking
     */
    function unsafeSubtraction(uint256 a, uint256 b) public pure returns (uint256) {
        // Potential underflow if a < b
        return a - b;
    }
} 