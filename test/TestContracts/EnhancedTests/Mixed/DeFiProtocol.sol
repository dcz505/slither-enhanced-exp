// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IERC20 {
    function transfer(address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
}

interface IFlashloanCallback {
    function flashloanCallback(address token, uint256 amount) external;
}

contract DeFiProtocol {
    mapping(address => mapping(address => uint256)) public userDeposits; // token => user => amount
    mapping(address => uint256) public poolReserves; // token => amount
    uint256 public constant FEE_DENOMINATOR = 10000;
    uint256 public swapFee = 30; // 0.3%
    address public owner;
    
    constructor() {
        owner = msg.sender;
    }
    
    function deposit(address token, uint256 amount) external {
        IERC20(token).transfer(address(this), amount);
        userDeposits[token][msg.sender] += amount;
        poolReserves[token] += amount;
    }
    
    function withdraw(address token, uint256 amount) external {
        require(userDeposits[token][msg.sender] >= amount, "Insufficient balance");
        
        // 未检查余额变化，可能存在漏洞
        userDeposits[token][msg.sender] -= amount;
        poolReserves[token] -= amount;
        
        // 可能的重入漏洞
        IERC20(token).transfer(msg.sender, amount);
    }
    
    function executeFlashloan(address token, uint256 amount, address callbackTarget) external {
        // 闪电贷风险 - 没有对金额限制
        require(amount <= poolReserves[token], "Amount exceeds pool reserves");
        
        IERC20(token).transfer(callbackTarget, amount);
        IFlashloanCallback(callbackTarget).flashloanCallback(token, amount);
        
        // 数值计算风险 - 没有检查计算溢出
        uint256 fee = (amount * swapFee) / FEE_DENOMINATOR;
        uint256 requiredAmount = amount + fee;
        
        // 余额检查风险 - 只检查当前余额，没有比较与之前的差值
        require(IERC20(token).balanceOf(address(this)) >= poolReserves[token], "Flashloan not repaid");
    }
    
    function swap(address tokenA, address tokenB, uint256 amountA) external returns (uint256) {
        // 转入tokenA
        uint256 balanceABefore = IERC20(tokenA).balanceOf(address(this));
        IERC20(tokenA).transfer(address(this), amountA);
        uint256 actualAmountA = IERC20(tokenA).balanceOf(address(this)) - balanceABefore;
        
        // 计算兑换金额 - 数值计算风险
        uint256 amountB = calculateSwapOutput(tokenA, tokenB, actualAmountA);
        
        // 转出tokenB - 未检查代币余额
        IERC20(tokenB).transfer(msg.sender, amountB);
        
        return amountB;
    }
    
    function calculateSwapOutput(address tokenA, address tokenB, uint256 amountA) internal view returns (uint256) {
        uint256 reserveA = poolReserves[tokenA];
        uint256 reserveB = poolReserves[tokenB];
        
        // 数值精度问题风险
        uint256 amountWithFee = amountA * (FEE_DENOMINATOR - swapFee);
        uint256 numerator = amountWithFee * reserveB;
        uint256 denominator = (reserveA * FEE_DENOMINATOR) + amountWithFee;
        
        return numerator / denominator;
    }
}