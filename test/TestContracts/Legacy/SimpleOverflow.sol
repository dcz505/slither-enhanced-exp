// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title SimpleOverflow
 * @dev Tests basic integer overflow detection.
 */
contract SimpleOverflow {
    function potentialOverflow(uint8 a, uint8 b) public pure returns (uint8) {
        // Potential overflow if a + b > 255
        return a + b;
    }

    function potentialUnderflow(uint8 a, uint8 b) public pure returns (uint8) {
        // Potential underflow if a < b
        return a - b;
    }
} 