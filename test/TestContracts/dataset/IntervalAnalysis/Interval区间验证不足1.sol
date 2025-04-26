
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Interval区间验证不足1
 * @dev 区间分析测试合约 - 区间验证不足
 */
contract Interval区间验证不足1 {
    uint256 public minValue;
    uint256 public maxValue;
    address public owner;
    
    constructor() {
        owner = msg.sender;
        minValue = 10;
        maxValue = 1000;
    }
    
    function setInterval(uint256 min, uint256 max) public {
        require(msg.sender == owner, "Not owner");
        // 区间验证不足
        // 增强版Slither应该比原版更好地检测出这个问题
        if (min < 10) {
            // 应该有更严格的检查
            min = 10;
        }
        if (max > 10000) {
            // 应该有更严格的检查
            max = 10000;
        }
        minValue = min;
        maxValue = max;
    }
    
    function checkValue(uint256 value) public view returns (bool) {
        return value >= minValue && value <= maxValue;
    }
    
    function withdraw() public {
        require(msg.sender == owner, "Not owner");
        payable(msg.sender).transfer(address(this).balance);
    }
    
    receive() external payable {}
}
