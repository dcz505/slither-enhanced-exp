
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Baseline重入攻击
 * @dev 基准测试合约 - 重入攻击
 */
contract BaselineReentrancy {
    uint256 public value;
    address public owner;
    
    constructor() {
        owner = msg.sender;
        value = 100;
    }
    
    function setValue(uint256 newValue) public {
        // 可能导致重入攻击
        // Slither应该检测出这个问题
        (bool success, ) = msg.sender.call{
            value: address(this).balance / 10
        }("");
        require(success, "Transfer failed");
        value = newValue;
    }
    
    function withdraw() public {
        require(msg.sender == owner, "Not owner");
        payable(msg.sender).transfer(address(this).balance);
    }
    
    receive() external payable {}
}
