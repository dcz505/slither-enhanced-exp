
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title Interval区间边界溢出3
 * @dev 区间分析测试合约 - 区间边界溢出
 */
contract Interval区间边界溢出3 {
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
        // 区间边界可能溢出
        // 增强版Slither应该比原版更好地检测出这个问题
        if (max > type(uint256).max - min) {
            max = type(uint256).max - min;
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
