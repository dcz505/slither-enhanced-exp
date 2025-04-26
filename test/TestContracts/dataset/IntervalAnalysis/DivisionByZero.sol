// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title DivisionByZero
 * @dev Tests potential division by zero errors.
 */
contract DivisionByZero {
    function calculateRatio(uint256 numerator, uint256 denominator) public pure returns (uint256) {
        // Potential division by zero if denominator is 0
        return numerator / denominator;
    }

    function calculateRemainder(uint256 numerator, uint256 denominator) public pure returns (uint256) {
        // Potential division by zero if denominator is 0
        return numerator % denominator;
    }
} 