// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title UnboundedFlashloan
 * @dev 演示无界闪电贷风险的测试合约
 * 包含无界闪电贷使用的多种风险模式
 */
contract UnboundedFlashloan {
    address public owner;
    mapping(address => uint256) public balances;
    uint256 public totalSupply;
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not owner");
        _;
    }
    
    // 存款函数
    function deposit() external payable {
        balances[msg.sender] += msg.value;
        totalSupply += msg.value;
    }
    
    // 提款函数
    function withdraw(uint256 amount) external {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        balances[msg.sender] -= amount;
        totalSupply -= amount;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
    
    // 危险: 无界闪电贷实现，没有金额限制
    function flashLoan(address receiver, uint256 amount, bytes calldata data) external {
        // 危险: 没有检查amount与合约余额的关系
        // 危险: 没有贷款上限
        
        // 记录贷款前的余额
        uint256 balanceBefore = address(this).balance;
        
        // 转移资金给接收者
        (bool success, ) = receiver.call{value: amount}("");
        require(success, "Transfer to receiver failed");
        
        // 调用接收者的回调函数
        (bool callbackSuccess, ) = receiver.call(
            abi.encodeWithSignature("executeFlashloan(bytes)", data)
        );
        require(callbackSuccess, "Callback failed");
        
        // 危险: 没有验证回调函数执行后的资金是否已返还
        uint256 balanceAfter = address(this).balance;
        require(balanceAfter >= balanceBefore, "Flashloan not repaid");
    }
    
    // 另一个危险的闪电贷实现，使用不安全的回调
    function unsafeFlashLoan(address receiver, bytes calldata data) external {
        // 危险: 使用全部合约余额进行闪电贷
        uint256 amount = address(this).balance;
        
        // 转移全部资金给接收者
        (bool success, ) = receiver.call{value: amount}("");
        require(success, "Transfer to receiver failed");
        
        // 直接执行接收者提供的任意数据
        (bool callbackSuccess, ) = receiver.call(data);
        require(callbackSuccess, "Callback failed");
        
        // 危险: 没有明确验证贷款是否被偿还
        require(address(this).balance >= amount, "Loan not repaid");
    }
    
    // 不安全的贷款操作，没有实现闪电贷模式
    function unsafeLoan(address receiver, uint256 amount) external onlyOwner {
        // 危险: 没有检查amount，即使是管理员也可能耗尽资金
        (bool success, ) = receiver.call{value: amount}("");
        require(success, "Transfer failed");
    }
    
    // 接收函数
    receive() external payable {}
} 