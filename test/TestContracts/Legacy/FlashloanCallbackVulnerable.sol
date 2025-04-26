// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title FlashloanCallbackVulnerable
 * @dev 演示闪电贷回调风险的测试合约
 * 包含多种闪电贷回调风险模式
 */
contract FlashloanCallbackVulnerable {
    address public owner;
    mapping(address => uint256) public balances;
    bool private locked;
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not the owner");
        _;
    }
    
    // 防止重入攻击的修饰符，但在某些函数中未使用
    modifier nonReentrant() {
        require(!locked, "Reentrant call");
        locked = true;
        _;
        locked = false;
    }
    
    // 存款函数
    function deposit() external payable {
        balances[msg.sender] += msg.value;
    }
    
    // 有缺陷的提款函数 - 不使用nonReentrant
    function withdrawUnsafe() external {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        
        // 危险: 在余额清零前调用外部合约
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        
        // 余额在转账后才清零，可能导致重入攻击
        balances[msg.sender] = 0;
    }
    
    // 安全的提款函数
    function withdrawSafe() external nonReentrant {
        uint256 amount = balances[msg.sender];
        require(amount > 0, "No balance to withdraw");
        
        // 先清零余额，再转账
        balances[msg.sender] = 0;
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
    }
    
    // 模拟闪电贷回调函数，未经正确保护
    function flashLoanCallback(address borrower, uint256 amount, bytes calldata data) external {
        // 危险: 没有足够的验证，任何人都可以调用
        (bool success, ) = borrower.call(data);
        require(success, "Callback execution failed");
    }
    
    // 另一个有漏洞的闪电贷回调，缺少足够的访问控制
    function executeFlashLoanOperation(address target, bytes memory data) external returns (bool) {
        // 危险: 没有验证调用者身份，也没有验证target地址
        (bool success, ) = target.call(data);
        return success;
    }
    
    // 管理员功能 - 在闪电贷回调中可能被恶意调用
    function transferOwnership(address newOwner) external onlyOwner {
        owner = newOwner;
    }
    
    // 紧急提款函数 - 可能在闪电贷回调中被滥用
    function emergencyWithdraw() external onlyOwner {
        payable(owner).transfer(address(this).balance);
    }
    
    // 接收以太币
    receive() external payable {}
} 