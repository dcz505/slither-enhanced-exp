// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/**
 * @title DeFiProtocolWithMultipleVulnerabilities
 * @dev A complex DeFi protocol contract with multiple vulnerabilities
 *      This contract is designed to trigger multiple detectors from the enhanced module
 */
contract DeFiProtocolWithMultipleVulnerabilities {
    // Protocol constants
    uint256 public constant MAX_LTV = 8000; // 80% (scaled by 10000)
    uint256 public constant LIQUIDATION_THRESHOLD = 8500; // 85% (scaled by 10000)
    uint256 public constant LIQUIDATION_BONUS = 500; // 5% (scaled by 10000)
    uint256 public constant FLASH_LOAN_FEE = 0; // 0% fee (vulnerability)
    
    // State variables
    address public owner;
    mapping(address => uint256) public userCollateral;
    mapping(address => uint256) public userBorrows;
    mapping(address => bool) public liquidators;
    mapping(address => uint256) public assetPrices;
    uint256 public totalPoolLiquidity;
    bool private _locked;
    
    // Events
    event Deposit(address user, uint256 amount);
    event Borrow(address user, uint256 amount);
    event Repay(address user, uint256 amount);
    event Liquidation(address liquidator, address user, uint256 collateralAmount, uint256 debtAmount);
    event FlashLoan(address user, uint256 amount);
    event PriceUpdate(address asset, uint256 price);
    
    constructor() {
        owner = msg.sender;
        liquidators[msg.sender] = true;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }
    
    modifier onlyLiquidator() {
        require(liquidators[msg.sender], "Not a liquidator");
        _;
    }
    
    modifier nonReentrant() {
        require(!_locked, "Reentrant call");
        _locked = true;
        _;
        _locked = false;
    }
    
    // ======= BASIC PROTOCOL FUNCTIONS =======
    
    function addLiquidator(address liquidator) external onlyOwner {
        liquidators[liquidator] = true;
    }
    
    function removeLiquidator(address liquidator) external onlyOwner {
        liquidators[liquidator] = false;
    }
    
    function deposit() external payable {
        userCollateral[msg.sender] += msg.value;
        totalPoolLiquidity += msg.value;
        emit Deposit(msg.sender, msg.value);
    }
    
    // ======= VULNERABLE FUNCTION #1: UNCHECKED ARITHMETIC =======
    
    function borrow(uint256 amount) external {
        // Validate borrowing capacity based on collateral
        uint256 collateralValue = userCollateral[msg.sender];
        
        // Vulnerability: Potential overflow in the calculation
        uint256 borrowLimit = (collateralValue * MAX_LTV) / 10000;
        
        // Vulnerability: No check if (userBorrows[msg.sender] + amount) overflows
        require(userBorrows[msg.sender] + amount <= borrowLimit, "Exceeds borrow limit");
        
        userBorrows[msg.sender] += amount;
        
        // Vulnerability: No check if (totalPoolLiquidity - amount) underflows
        require(totalPoolLiquidity >= amount, "Insufficient liquidity");
        totalPoolLiquidity -= amount;
        
        // Transfer borrowed amount to user
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        emit Borrow(msg.sender, amount);
    }
    
    function repay() external payable {
        // Vulnerability: No check if msg.value > userBorrows[msg.sender]
        if (msg.value > userBorrows[msg.sender]) {
            userBorrows[msg.sender] = 0;
        } else {
            userBorrows[msg.sender] -= msg.value;
        }
        
        totalPoolLiquidity += msg.value;
        emit Repay(msg.sender, msg.value);
    }
    
    // ======= VULNERABLE FUNCTION #2: UNBOUNDED FLASH LOAN =======
    
    function flashLoan(uint256 amount, bytes calldata data) external {
        // Vulnerability: No maximum amount check
        require(totalPoolLiquidity >= amount, "Insufficient liquidity");
        
        // Vulnerability: No flash loan fee
        uint256 fee = 0; // Should be (amount * FLASH_LOAN_FEE) / 10000;
        
        // Record the previous balance for validation
        uint256 balanceBefore = address(this).balance;
        
        // Transfer the loan amount to the caller
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Flash loan transfer failed");
        
        // Call the receiver to handle the flash loan
        IFlashLoanReceiver(msg.sender).executeOperation(amount, fee, data);
        
        // Validate that the loan (plus fee) has been returned
        require(
            address(this).balance >= balanceBefore + fee,
            "Flash loan not repaid"
        );
        
        emit FlashLoan(msg.sender, amount);
    }
    
    // ======= VULNERABLE FUNCTION #3: FLASHLOAN CALLBACK INSECURE =======
    
    function executeCallback(address payable recipient, bytes calldata data) external {
        // Vulnerability: No access control or checks
        
        // Anyone can call this function and manipulate protocol's state
        
        // Vulnerability: Unsafe external call from callback
        (bool success, ) = recipient.call(data);
        require(success, "Callback execution failed");
        
        // Vulnerability: No validation or state reset after external call
    }
    
    // ======= VULNERABLE FUNCTION #4: DEFI RANGE VIOLATION =======
    
    function updateAssetPrice(address asset, uint256 newPrice) external onlyOwner {
        // Vulnerability: No range validation on price
        assetPrices[asset] = newPrice;
        
        // Should validate if the price change is within reasonable bounds
        // e.g., require(newPrice > 0 && newPrice < MAX_PRICE, "Invalid price");
        
        emit PriceUpdate(asset, newPrice);
    }
    
    function setLiquidationThreshold(uint256 newThreshold) external onlyOwner {
        // Vulnerability: No range validation
        // Should validate: require(newThreshold > MAX_LTV && newThreshold < 10000, "Invalid threshold");
        
        // This overwrites the constant value (which actually isn't possible in Solidity)
        // but demonstrates the concept of invalid threshold setting
    }
    
    // ======= VULNERABLE FUNCTION #5: LIQUIDATION WITH UNCHECKED TOKEN BALANCE =======
    
    function liquidate(address user) external onlyLiquidator {
        uint256 collateralValue = userCollateral[user];
        uint256 borrowValue = userBorrows[user];
        
        // Calculate liquidation threshold
        uint256 liquidationLimit = (collateralValue * LIQUIDATION_THRESHOLD) / 10000;
        
        // Check if position is eligible for liquidation
        require(borrowValue > liquidationLimit, "Position not liquidatable");
        
        // Calculate liquidation bonus
        uint256 bonus = (collateralValue * LIQUIDATION_BONUS) / 10000;
        uint256 collateralToLiquidator = borrowValue + bonus;
        
        // Vulnerability: Unchecked balance handling
        // No verification that liquidator has enough funds to cover the debt
        
        // Transfer collateral to liquidator
        userCollateral[user] = 0;
        userBorrows[user] = 0;
        
        // Vulnerability: No balance checks on transfers
        (bool success, ) = msg.sender.call{value: collateralToLiquidator}("");
        require(success, "Collateral transfer failed");
        
        emit Liquidation(msg.sender, user, collateralToLiquidator, borrowValue);
    }
    
    // Function to receive ETH
    receive() external payable {}
}

/**
 * @title IFlashLoanReceiver
 * @dev Interface for contracts that want to receive flash loans
 */
interface IFlashLoanReceiver {
    function executeOperation(
        uint256 amount,
        uint256 fee,
        bytes calldata data
    ) external;
} 