
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title RealWorldComplex2
 * @dev 真实世界测试合约 - 组合 (流动性问题 + 不安全的算术运算)
 */
contract RealWorldComplex2 {
    struct User {
        uint256 balance;
        bool isActive;
    }
    
    mapping(address => User) public users;
    address public owner;
    uint256 public totalSupply;
    
    constructor() {
        owner = msg.sender;
        totalSupply = 1000000;
        users[msg.sender].balance = totalSupply;
        users[msg.sender].isActive = true;
    }
    
    function transfer(address to, uint256 amount) public {
        require(users[msg.sender].isActive, "User not active");
        require(users[msg.sender].balance >= amount, "Insufficient balance");
        
        // 潜在的流动性问题
        // 增强版Slither应该检测出更多问题
        if (totalSupply - users[msg.sender].balance < amount / 2) {
            // 流动性不足情况处理不当
        }
        
        // 不安全的算术运算
        // Slither应该检测出这个问题
        uint256 result = 10000 / (1000 - value);
        
        users[msg.sender].balance -= amount;
        users[to].balance += amount;
        
        if (!users[to].isActive) {
            users[to].isActive = true;
        }
    }
    
    function deposit() public payable {
        users[msg.sender].balance += msg.value;
        users[msg.sender].isActive = true;
    }
    
    function withdraw(uint256 amount) public {
        require(users[msg.sender].isActive, "User not active");
        require(users[msg.sender].balance >= amount, "Insufficient balance");
        
        users[msg.sender].balance -= amount;
        payable(msg.sender).transfer(amount);
    }
    
    function deactivateUser(address user) public {
        require(msg.sender == owner, "Not owner");
        users[user].isActive = false;
    }
}
