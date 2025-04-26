
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title BaselineOverflow
 * @dev 基准测试合约 - 整数溢出
 */
contract BaselineOverflow {
    uint256 public value;
    address public owner;
    
    constructor() {
        owner = msg.sender;
        value = 100;
    }
    
    function setValue(uint256 newValue) public {
        // 可能导致整数溢出
        // Slither应该检测出这个问题
        if (newValue > type(uint256).max - 10) {
            newValue = 10;
        }
        value = newValue;
    }
    
    function withdraw() public {
        require(msg.sender == owner, "Not owner");
        payable(msg.sender).transfer(address(this).balance);
    }
    
    receive() external payable {}
}
