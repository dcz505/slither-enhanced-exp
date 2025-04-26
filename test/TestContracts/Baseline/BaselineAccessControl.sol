
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Baseline权限控制缺失
 * @dev 基准测试合约 - 权限控制缺失
 */
contract BaselineAccessControl {
    uint256 public value;
    address public owner;
    
    constructor() {
        owner = msg.sender;
        value = 100;
    }
    
    function setValue(uint256 newValue) public {
        // 缺少权限控制
        // Slither应该检测出这个问题
        // require(msg.sender == owner, "Not owner");
        value = newValue;
    }
    
    function withdraw() public {
        require(msg.sender == owner, "Not owner");
        payable(msg.sender).transfer(address(this).balance);
    }
    
    receive() external payable {}
}
