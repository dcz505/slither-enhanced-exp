// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract NumericalOverflow {
    mapping(address => uint256) public balances;
    
    function deposit() public payable {
        balances[msg.sender] += msg.value;
    }
    
    function riskyMath(uint256 a, uint256 b) public pure returns (uint256) {
        // 潜在溢出风险
        uint256 c = a * b;
        require(a == 0 || c / a == b, "Multiplication overflow");
        return c;
    }
    
    function unsafeWithdraw(uint256 amount) public {
        require(balances[msg.sender] >= amount, "Insufficient balance");
        // 可能存在重入风险
        (bool success, ) = msg.sender.call{value: amount}("");
        require(success, "Transfer failed");
        balances[msg.sender] -= amount;
    }
}