// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title UncheckedBalance
 * @dev 演示代币余额变更后未检查的风险场景
 * 包含多种余额检查缺失模式
 */
contract UncheckedBalance {
    address public owner;
    address public tokenA;
    address public tokenB;
    
    event Swap(address indexed user, uint256 amountIn, uint256 amountOut);
    event Deposit(address indexed user, uint256 amount);
    event Withdrawal(address indexed user, uint256 amount);
    
    constructor(address _tokenA, address _tokenB) {
        owner = msg.sender;
        tokenA = _tokenA;
        tokenB = _tokenB;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    // 模拟接口 - 仅用于测试目的
    function balanceOf(address token, address account) private view returns (uint256) {
        // 实际中这会调用token合约的balanceOf
        return 100; // 假设返回值
    }
    
    function transfer(address token, address to, uint256 amount) private returns (bool) {
        // 实际中这会调用token合约的transfer
        return true; // 假设总是成功
    }
    
    function transferFrom(address token, address from, address to, uint256 amount) private returns (bool) {
        // 实际中这会调用token合约的transferFrom
        return true; // 假设总是成功
    }
    
    // 危险: 交换函数未检查最终余额
    function unsafeSwap(uint256 amountIn, uint256 amountOut) external {
        // 转移用户的tokenA到合约
        transferFrom(tokenA, msg.sender, address(this), amountIn);
        
        // 转移合约的tokenB到用户
        transfer(tokenB, msg.sender, amountOut);
        
        // 危险: 没有检查转账后的余额变化
        // 危险: 即使转账失败返回true，也没有验证实际到账金额
        
        emit Swap(msg.sender, amountIn, amountOut);
    }
    
    // 危险: 存款函数未检查余额变化
    function unsafeDeposit(uint256 amount) external {
        uint256 initialBalance = balanceOf(tokenA, address(this));
        
        // 转移用户的tokenA到合约
        transferFrom(tokenA, msg.sender, address(this), amount);
        
        // 危险: 没有检查转账后实际收到的金额
        // 假设转账已成功，但实际可能收到的金额不足
        
        emit Deposit(msg.sender, amount);
    }
    
    // 危险: 提款函数未检查余额变化
    function unsafeWithdraw(uint256 amount) external {
        // 危险: 没有检查合约是否有足够的余额
        
        // 转移合约的tokenA到用户
        transfer(tokenA, msg.sender, amount);
        
        // 危险: 没有检查转账后的余额变化
        
        emit Withdrawal(msg.sender, amount);
    }
    
    // 安全: 正确检查余额变化的存款函数
    function safeDeposit(uint256 amount) external {
        uint256 initialBalance = balanceOf(tokenA, address(this));
        
        // 转移用户的tokenA到合约
        transferFrom(tokenA, msg.sender, address(this), amount);
        
        // 安全: 检查实际收到的金额
        uint256 newBalance = balanceOf(tokenA, address(this));
        uint256 actualAmount = newBalance - initialBalance;
        require(actualAmount >= amount, "Received less than expected");
        
        emit Deposit(msg.sender, actualAmount);
    }
    
    // 安全: 正确检查余额变化的提款函数
    function safeWithdraw(uint256 amount) external {
        // 安全: 检查合约是否有足够的余额
        uint256 contractBalance = balanceOf(tokenA, address(this));
        require(contractBalance >= amount, "Insufficient balance");
        
        uint256 initialBalance = balanceOf(tokenA, msg.sender);
        
        // 转移合约的tokenA到用户
        transfer(tokenA, msg.sender, amount);
        
        // 安全: 检查用户实际收到的金额
        uint256 newBalance = balanceOf(tokenA, msg.sender);
        uint256 actualAmount = newBalance - initialBalance;
        require(actualAmount >= amount, "Received less than expected");
        
        emit Withdrawal(msg.sender, actualAmount);
    }
    
    // 让合约能够接收ETH
    receive() external payable {}
} 