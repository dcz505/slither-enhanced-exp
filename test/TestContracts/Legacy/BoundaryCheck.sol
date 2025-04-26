// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title BoundaryCheck
 * @dev Tests checks involving boundary conditions.
 */
contract BoundaryCheck {
    uint256 public constant MAX_VALUE = 100;
    uint256 public value;

    function setValueInRange(uint256 _value) public {
        // Should detect if _value can exceed MAX_VALUE
        require(_value <= MAX_VALUE, "Value out of range");
        value = _value;
    }

    function addWithinLimit(uint256 amount) public {
        // Should detect if value + amount can exceed MAX_VALUE
        uint256 newValue = value + amount;
        require(newValue <= MAX_VALUE, "Addition exceeds limit");
        value = newValue;
    }
} 