// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title NileFi Milestone Escrow Contract
 * @dev Smart contract for milestone-based escrow on Hedera (EVM-compatible)
 * 
 * This contract manages escrow funds for NileFi platform.
 * Investors deposit funds, which are held until milestones are verified.
 * 
 * UPGRADE PATH: Deploy this contract to replace custodial escrow in Phase 2
 */

contract NileFiEscrow {
    
    // Contract owner (platform admin)
    address public owner;
    
    // Platform fee percentage (e.g., 2% = 200 basis points)
    uint256 public platformFeeBps = 200; // 2%
    uint256 constant BPS_DENOMINATOR = 10000;
    
    // Escrow status
    enum EscrowStatus { Active, Released, Refunded, Cancelled }
    
    // Funding request structure
    struct FundingRequest {
        string requestId; // UUID from backend
        address payable startupWallet;
        uint256 totalAmount;
        uint256 amountRaised;
        uint256 amountReleased;
        bool isActive;
    }
    
    // Milestone structure
    struct Milestone {
        string milestoneId; // UUID from backend
        string fundingRequestId;
        uint256 amount;
        bool isReleased;
        bool isVerified;
        address verifier; // Who verified this milestone
    }
    
    // Investment structure
    struct Investment {
        address payable investor;
        string fundingRequestId;
        uint256 amount;
        uint256 timestamp;
        EscrowStatus status;
    }
    
    // Mappings
    mapping(string => FundingRequest) public fundingRequests;
    mapping(string => Milestone) public milestones;
    mapping(bytes32 => Investment) public investments; // hash(investor, requestId) => Investment
    mapping(address => uint256) public investorBalances;
    
    // Events
    event FundingRequestCreated(string indexed requestId, address startupWallet, uint256 totalAmount);
    event InvestmentDeposited(address indexed investor, string indexed requestId, uint256 amount);
    event MilestoneVerified(string indexed milestoneId, address verifier);
    event FundsReleased(string indexed milestoneId, address indexed startup, uint256 amount);
    event InvestmentRefunded(address indexed investor, string indexed requestId, uint256 amount);
    event PlatformFeeCollected(uint256 amount);
    
    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can call this");
        _;
    }
    
    modifier fundingRequestExists(string memory requestId) {
        require(fundingRequests[requestId].isActive, "Funding request does not exist");
        _;
    }
    
    constructor() {
        owner = msg.sender;
    }
    
    /**
     * @dev Create a new funding request
     * @param requestId Unique identifier from backend
     * @param startupWallet Wallet address of the startup
     * @param totalAmount Total funding amount needed
     */
    function createFundingRequest(
        string memory requestId,
        address payable startupWallet,
        uint256 totalAmount
    ) external onlyOwner {
        require(!fundingRequests[requestId].isActive, "Request already exists");
        require(startupWallet != address(0), "Invalid startup wallet");
        require(totalAmount > 0, "Amount must be greater than 0");
        
        fundingRequests[requestId] = FundingRequest({
            requestId: requestId,
            startupWallet: startupWallet,
            totalAmount: totalAmount,
            amountRaised: 0,
            amountReleased: 0,
            isActive: true
        });
        
        emit FundingRequestCreated(requestId, startupWallet, totalAmount);
    }
    
    /**
     * @dev Investor deposits funds to escrow
     * @param requestId The funding request to invest in
     */
    function deposit(string memory requestId) 
        external 
        payable 
        fundingRequestExists(requestId) 
    {
        require(msg.value > 0, "Must send HBAR");
        
        FundingRequest storage request = fundingRequests[requestId];
        require(
            request.amountRaised + msg.value <= request.totalAmount,
            "Investment exceeds funding goal"
        );
        
        // Record investment
        bytes32 investmentKey = keccak256(abi.encodePacked(msg.sender, requestId));
        Investment storage investment = investments[investmentKey];
        
        if (investment.amount == 0) {
            // New investment
            investments[investmentKey] = Investment({
                investor: payable(msg.sender),
                fundingRequestId: requestId,
                amount: msg.value,
                timestamp: block.timestamp,
                status: EscrowStatus.Active
            });
        } else {
            // Additional investment
            investment.amount += msg.value;
        }
        
        // Update balances
        investorBalances[msg.sender] += msg.value;
        request.amountRaised += msg.value;
        
        emit InvestmentDeposited(msg.sender, requestId, msg.value);
    }
    
    /**
     * @dev Create a milestone for a funding request
     * @param milestoneId Unique milestone identifier
     * @param fundingRequestId Associated funding request
     * @param amount Amount allocated to this milestone
     */
    function createMilestone(
        string memory milestoneId,
        string memory fundingRequestId,
        uint256 amount
    ) external onlyOwner fundingRequestExists(fundingRequestId) {
        require(bytes(milestones[milestoneId].milestoneId).length == 0, "Milestone already exists");
        require(amount > 0, "Amount must be greater than 0");
        
        milestones[milestoneId] = Milestone({
            milestoneId: milestoneId,
            fundingRequestId: fundingRequestId,
            amount: amount,
            isReleased: false,
            isVerified: false,
            verifier: address(0)
        });
    }
    
    /**
     * @dev Verify a milestone and release funds to startup
     * @param milestoneId The milestone to verify
     */
    function verifyAndRelease(string memory milestoneId) 
        external 
        onlyOwner 
    {
        Milestone storage milestone = milestones[milestoneId];
        require(bytes(milestone.milestoneId).length > 0, "Milestone does not exist");
        require(!milestone.isVerified, "Already verified");
        require(!milestone.isReleased, "Already released");
        
        FundingRequest storage request = fundingRequests[milestone.fundingRequestId];
        require(request.isActive, "Funding request not active");
        require(request.amountRaised >= milestone.amount, "Insufficient funds");
        
        // Mark as verified
        milestone.isVerified = true;
        milestone.verifier = msg.sender;
        
        emit MilestoneVerified(milestoneId, msg.sender);
        
        // Calculate platform fee
        uint256 platformFee = (milestone.amount * platformFeeBps) / BPS_DENOMINATOR;
        uint256 amountToStartup = milestone.amount - platformFee;
        
        // Release funds to startup
        milestone.isReleased = true;
        request.amountReleased += milestone.amount;
        
        // Transfer funds
        (bool success, ) = request.startupWallet.call{value: amountToStartup}("");
        require(success, "Transfer to startup failed");
        
        // Transfer platform fee to owner
        if (platformFee > 0) {
            (bool feeSuccess, ) = owner.call{value: platformFee}("");
            require(feeSuccess, "Platform fee transfer failed");
            emit PlatformFeeCollected(platformFee);
        }
        
        emit FundsReleased(milestoneId, request.startupWallet, amountToStartup);
    }
    
    /**
     * @dev Refund an investor (in case of cancellation)
     * @param requestId The funding request to refund
     * @param investorAddress The investor to refund
     */
    function refund(string memory requestId, address payable investorAddress) 
        external 
        onlyOwner 
        fundingRequestExists(requestId) 
    {
        bytes32 investmentKey = keccak256(abi.encodePacked(investorAddress, requestId));
        Investment storage investment = investments[investmentKey];
        
        require(investment.amount > 0, "No investment found");
        require(investment.status == EscrowStatus.Active, "Investment not active");
        
        uint256 refundAmount = investment.amount;
        
        // Update state before transfer (reentrancy protection)
        investment.status = EscrowStatus.Refunded;
        investorBalances[investorAddress] -= refundAmount;
        
        FundingRequest storage request = fundingRequests[requestId];
        request.amountRaised -= refundAmount;
        
        // Transfer refund
        (bool success, ) = investorAddress.call{value: refundAmount}("");
        require(success, "Refund transfer failed");
        
        emit InvestmentRefunded(investorAddress, requestId, refundAmount);
    }
    
    /**
     * @dev Cancel a funding request (emergency only)
     * @param requestId The request to cancel
     */
    function cancelFundingRequest(string memory requestId) 
        external 
        onlyOwner 
        fundingRequestExists(requestId) 
    {
        FundingRequest storage request = fundingRequests[requestId];
        request.isActive = false;
        // Note: Refunds must be processed individually using refund()
    }
    
    /**
     * @dev Update platform fee (only owner)
     * @param newFeeBps New fee in basis points
     */
    function setPlatformFee(uint256 newFeeBps) external onlyOwner {
        require(newFeeBps <= 1000, "Fee cannot exceed 10%");
        platformFeeBps = newFeeBps;
    }
    
    /**
     * @dev Transfer ownership
     * @param newOwner New owner address
     */
    function transferOwnership(address newOwner) external onlyOwner {
        require(newOwner != address(0), "Invalid address");
        owner = newOwner;
    }
    
    /**
     * @dev Get funding request details
     * @param requestId Request identifier
     */
    function getFundingRequest(string memory requestId) 
        external 
        view 
        returns (
            address startupWallet,
            uint256 totalAmount,
            uint256 amountRaised,
            uint256 amountReleased,
            bool isActive
        ) 
    {
        FundingRequest memory request = fundingRequests[requestId];
        return (
            request.startupWallet,
            request.totalAmount,
            request.amountRaised,
            request.amountReleased,
            request.isActive
        );
    }
    
    /**
     * @dev Get milestone details
     * @param milestoneId Milestone identifier
     */
    function getMilestone(string memory milestoneId) 
        external 
        view 
        returns (
            string memory fundingRequestId,
            uint256 amount,
            bool isVerified,
            bool isReleased
        ) 
    {
        Milestone memory milestone = milestones[milestoneId];
        return (
            milestone.fundingRequestId,
            milestone.amount,
            milestone.isVerified,
            milestone.isReleased
        );
    }
    
    /**
     * @dev Get investment details
     * @param investorAddress Investor address
     * @param requestId Funding request ID
     */
    function getInvestment(address investorAddress, string memory requestId) 
        external 
        view 
        returns (
            uint256 amount,
            uint256 timestamp,
            EscrowStatus status
        ) 
    {
        bytes32 key = keccak256(abi.encodePacked(investorAddress, requestId));
        Investment memory investment = investments[key];
        return (investment.amount, investment.timestamp, investment.status);
    }
    
    // Emergency: allow owner to withdraw stuck funds (use with caution)
    function emergencyWithdraw() external onlyOwner {
        (bool success, ) = owner.call{value: address(this).balance}("");
        require(success, "Emergency withdrawal failed");
    }
    
    // Fallback to receive HBAR
    receive() external payable {}
}
