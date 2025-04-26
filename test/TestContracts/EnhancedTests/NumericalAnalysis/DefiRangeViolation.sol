// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/**
 * @title DefiRangeViolation
 * @dev A contract demonstrating DeFi-specific range violations that can be detected by the defi-range-violation detector
 */
contract DefiRangeViolation {
    // Constants for DeFi protocol limits
    uint256 public constant MAX_LTV = 8000; // 80% (scaled by 10000)
    uint256 public constant MIN_COLLATERAL_RATIO = 12500; // 125% (scaled by 10000)
    uint256 public constant MAX_FEE = 1000; // 10% (scaled by 10000)
    uint256 public constant MIN_LIQUIDITY = 1000; // Minimum required liquidity
    
    // Protocol state variables
    uint256 public ltvRatio = 7500; // 75%
    uint256 public collateralRatio = 13333; // 133.33%
    uint256 public liquidationThreshold = 8500; // 85%
    uint256 public swapFee = 300; // 3%
    uint256 public flashLoanFee = 9; // 0.09%
    
    // Asset specific variables
    mapping(address => uint256) public assetLTVs;
    mapping(address => uint256) public assetLiquidationThresholds;
    mapping(address => uint256) public poolLiquidity;
    
    // Price tracking
    mapping(address => uint256) public assetPrices;
    uint256 public lastPriceUpdateBlock;
    
    // Events
    event RangeViolation(string parameter, uint256 value, uint256 minLimit, uint256 maxLimit);
    
    /**
     * @dev Sets LTV ratio for an asset - susceptible to range violations
     */
    function setAssetLTV(address asset, uint256 newLTV) public {
        // Potential range violation: newLTV > MAX_LTV
        assetLTVs[asset] = newLTV;
        
        // The detector should identify potential violations where newLTV exceeds MAX_LTV
    }
    
    /**
     * @dev Sets new global LTV ratio - susceptible to range violations
     */
    function setGlobalLTV(uint256 newLTV) public {
        // Potential range violation: newLTV > MAX_LTV
        ltvRatio = newLTV;
        
        // Should validate: if (newLTV > MAX_LTV) revert LTVTooHigh();
    }
    
    /**
     * @dev Sets liquidation threshold for an asset - susceptible to range violations
     */
    function setLiquidationThreshold(address asset, uint256 newThreshold) public {
        // The detector should identify that the threshold might be inconsistent with LTV
        // Valid relation: liquidationThreshold > LTV
        assetLiquidationThresholds[asset] = newThreshold;
        
        // Missing validation: if (newThreshold <= assetLTVs[asset]) revert InvalidThreshold();
    }
    
    /**
     * @dev Sets swap fee - susceptible to range violations
     */
    function setSwapFee(uint256 newFee) public {
        // Potential range violation: newFee > MAX_FEE
        swapFee = newFee;
        
        // Missing: if (newFee > MAX_FEE) revert FeeTooHigh();
    }
    
    /**
     * @dev Updates collateral ratio - susceptible to range violations
     */
    function updateCollateralRatio(uint256 newRatio) public {
        // Potential violation: newRatio < MIN_COLLATERAL_RATIO
        collateralRatio = newRatio;
        
        // Missing: if (newRatio < MIN_COLLATERAL_RATIO) revert CollateralRatioTooLow();
    }
    
    /**
     * @dev Updates pool liquidity - susceptible to range violations
     */
    function updatePoolLiquidity(address pool, uint256 newLiquidity) public {
        // Potential violation: newLiquidity < MIN_LIQUIDITY
        poolLiquidity[pool] = newLiquidity;
        
        // Missing validation: if (newLiquidity < MIN_LIQUIDITY) revert InsufficientLiquidity();
    }
    
    /**
     * @dev Updates asset price with potential price manipulation detection
     */
    function updateAssetPrice(address asset, uint256 newPrice) public {
        uint256 oldPrice = assetPrices[asset];
        
        // Potential price deviation check missing
        // Missing: if (isLargeDeviation(oldPrice, newPrice)) revert PriceManipulation();
        
        assetPrices[asset] = newPrice;
        lastPriceUpdateBlock = block.number;
    }
    
    /**
     * @dev Calculates borrow capacity based on collateral and LTV
     */
    function calculateBorrowCapacity(uint256 collateralValue, address asset) public view returns (uint256) {
        // Uses LTV to calculate borrow capacity
        uint256 ltv = assetLTVs[asset] > 0 ? assetLTVs[asset] : ltvRatio;
        
        // Potential incorrect calculation if collateralValue*ltv causes overflow
        return (collateralValue * ltv) / 10000;
    }
    
    /**
     * @dev Calculates collateral required for a loan
     */
    function calculateRequiredCollateral(uint256 loanAmount, address asset) public view returns (uint256) {
        // Uses collateral ratio to determine required collateral
        uint256 ltv = assetLTVs[asset] > 0 ? assetLTVs[asset] : ltvRatio;
        
        // Potential division by zero if ltv = 0
        // Potential overflow or precision issues
        return (loanAmount * 10000) / ltv;
    }
    
    /**
     * @dev Simulates a liquidation check
     */
    function checkLiquidation(
        uint256 collateralValue, 
        uint256 debtValue, 
        address asset
    ) public view returns (bool) {
        uint256 threshold = assetLiquidationThresholds[asset] > 0 ? 
                          assetLiquidationThresholds[asset] : 
                          liquidationThreshold;
        
        // Calculates current ratio and checks if liquidation is needed
        uint256 currentRatio = (collateralValue * 10000) / debtValue;
        
        // Potential division by zero if debtValue = 0
        return currentRatio < threshold;
    }
} 