
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Baseline未检查外部调用返回值
 * @dev 基准测试合约 - 未检查外部调用返回值
 */
contract BaselineUncheck {
    uint256 public value;
    address public owner;
    
    constructor() {
        owner = msg.sender;
        value = 100;
    }
    
    function setValue(uint256 newValue) public {
        // 未检查外部调用返回值
        // Slither应该检测出这个问题
        msg.sender.call{
            value: 0
        }("");
        value = newValue;
    }
    
    function withdraw() public {
        require(msg.sender == owner, "Not owner");
        payable(msg.sender).transfer(address(this).balance);
    }
    
    receive() external payable {}
}
