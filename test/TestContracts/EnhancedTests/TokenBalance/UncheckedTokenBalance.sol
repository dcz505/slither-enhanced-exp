// SPDX-License-Identifier: MIT
pragma solidity ^0.8.17;

/**
 * @title UncheckedTokenBalance
 * @dev A contract demonstrating various patterns where token balances are not properly checked
 *      These issues can be detected by the unchecked-balance-change detector
 */
contract UncheckedTokenBalance {
    address public owner;
    mapping(address => uint256) public balances;
    mapping(address => mapping(address => uint256)) public allowances;
    
    // Mapping to track token contracts
    mapping(address => bool) public supportedTokens;
    
    // Events
    event Deposit(address token, address user, uint256 amount);
    event Withdrawal(address token, address user, uint256 amount);
    event TokenAdded(address token);
    event TokenRemoved(address token);
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Not authorized");
        _;
    }
    
    // Admin functions
    function addSupportedToken(address token) external onlyOwner {
        supportedTokens[token] = true;
        emit TokenAdded(token);
    }
    
    function removeSupportedToken(address token) external onlyOwner {
        supportedTokens[token] = false;
        emit TokenRemoved(token);
    }
    
    // ======= VULNERABLE FUNCTIONS WITH UNCHECKED TOKEN BALANCES =======
    
    /**
     * @dev Vulnerable deposit function that doesn't check balance changes
     * Issue: No verification that tokens were actually received
     */
    function unsafeDeposit(address token, uint256 amount) external {
        require(supportedTokens[token], "Token not supported");
        
        // Vulnerable: Just calls transferFrom without checking if the right amount was received
        bool success = IERC20(token).transferFrom(msg.sender, address(this), amount);
        require(success, "Transfer failed");
        
        // Updates internal balance without checking actual token receipt
        balances[msg.sender] += amount;
        
        emit Deposit(token, msg.sender, amount);
    }
    
    /**
     * @dev Vulnerable withdrawal function that doesn't check balance changes
     * Issue: No verification that tokens were actually sent
     */
    function unsafeWithdraw(address token, uint256 amount) external {
        require(supportedTokens[token], "Token not supported");
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Updates internal balance before transfer
        balances[msg.sender] -= amount;
        
        // Vulnerable: Just calls transfer without checking if the right amount was sent
        bool success = IERC20(token).transfer(msg.sender, amount);
        require(success, "Transfer failed");
        
        emit Withdrawal(token, msg.sender, amount);
    }
    
    /**
     * @dev Vulnerable batch transfer that doesn't check balance changes
     * Issue: No verification of balance changes after multiple transfers
     */
    function unsafeBatchTransfer(
        address token,
        address[] calldata recipients,
        uint256[] calldata amounts
    ) external {
        require(supportedTokens[token], "Token not supported");
        require(recipients.length == amounts.length, "Array length mismatch");
        
        uint256 totalAmount = 0;
        for (uint256 i = 0; i < amounts.length; i++) {
            totalAmount += amounts[i];
        }
        
        require(balances[msg.sender] >= totalAmount, "Insufficient balance");
        
        // Updates internal balance before transfers
        balances[msg.sender] -= totalAmount;
        
        // Vulnerable: Transfers tokens without checking if the right amounts were sent
        for (uint256 i = 0; i < recipients.length; i++) {
            IERC20(token).transfer(recipients[i], amounts[i]);
            // No check if transfer was successful
        }
    }
    
    /**
     * @dev Vulnerable token swap function without balance checks
     * Issue: No verification of balance changes for either token
     */
    function unsafeSwap(
        address tokenIn,
        address tokenOut,
        uint256 amountIn,
        uint256 amountOut
    ) external {
        require(supportedTokens[tokenIn], "Input token not supported");
        require(supportedTokens[tokenOut], "Output token not supported");
        
        // Updates internal balances without proper checks
        balances[msg.sender] -= amountIn;
        
        // Transfers tokens without proper balance verification
        IERC20(tokenIn).transferFrom(msg.sender, address(this), amountIn);
        IERC20(tokenOut).transfer(msg.sender, amountOut);
        
        // No check that the right amounts were transferred
    }
    
    /**
     * @dev Vulnerable permit function that doesn't check signature validity
     * Issue: Allows for potential signature replay attacks and lacks balance checks
     */
    function unsafePermitAndTransfer(
        address token,
        address from,
        address to,
        uint256 amount,
        bytes memory signature
    ) external {
        // Should verify signature, but doesn't
        
        // Dangerous absence of balance checks and authorization verification
        IERC20(token).transferFrom(from, to, amount);
        
        // No check if transfer was successful
    }
    
    // ======= SECURE IMPLEMENTATIONS FOR COMPARISON =======
    
    /**
     * @dev Secure deposit function with balance checks
     */
    function safeDeposit(address token, uint256 amount) external {
        require(supportedTokens[token], "Token not supported");
        
        // Record balance before
        uint256 balanceBefore = IERC20(token).balanceOf(address(this));
        
        // Transfer tokens
        bool success = IERC20(token).transferFrom(msg.sender, address(this), amount);
        require(success, "Transfer failed");
        
        // Verify actual balance change
        uint256 balanceAfter = IERC20(token).balanceOf(address(this));
        uint256 actualAmount = balanceAfter - balanceBefore;
        require(actualAmount == amount, "Incorrect amount received");
        
        // Update internal balance with verified amount
        balances[msg.sender] += actualAmount;
        
        emit Deposit(token, msg.sender, actualAmount);
    }
    
    /**
     * @dev Secure withdrawal function with balance checks
     */
    function safeWithdraw(address token, uint256 amount) external {
        require(supportedTokens[token], "Token not supported");
        require(balances[msg.sender] >= amount, "Insufficient balance");
        
        // Record balance before
        uint256 balanceBefore = IERC20(token).balanceOf(address(this));
        
        // Transfer tokens
        bool success = IERC20(token).transfer(msg.sender, amount);
        require(success, "Transfer failed");
        
        // Verify actual balance change
        uint256 balanceAfter = IERC20(token).balanceOf(address(this));
        uint256 actualAmount = balanceBefore - balanceAfter;
        require(actualAmount == amount, "Incorrect amount sent");
        
        // Update internal balance with verified amount
        balances[msg.sender] -= actualAmount;
        
        emit Withdrawal(token, msg.sender, actualAmount);
    }
}

/**
 * @title IERC20
 * @dev Interface for the ERC20 standard token
 */
interface IERC20 {
    function transferFrom(address sender, address recipient, uint256 amount) external returns (bool);
    function transfer(address recipient, uint256 amount) external returns (bool);
    function balanceOf(address account) external view returns (uint256);
} 