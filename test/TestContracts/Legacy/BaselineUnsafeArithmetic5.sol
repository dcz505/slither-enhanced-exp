
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Baseline不安全的算术运算
 * @dev 基准测试合约 - 不安全的算术运算
 */
contract BaselineUnsafeArithmetic {
    uint256 public value;
    address public owner;
    
    constructor() {
        owner = msg.sender;
        value = 100;
    }
    
    function setValue(uint256 newValue) public {
        // 不安全的算术运算
        // Slither应该检测出这个问题
        uint256 result = 10000 / (1000 - value);
        value = newValue;
    }
    
    function withdraw() public {
        require(msg.sender == owner, "Not owner");
        payable(msg.sender).transfer(address(this).balance);
    }
    
    receive() external payable {}
}
