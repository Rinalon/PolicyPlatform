// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import {ERC20} from "./ERC20.sol";
import {ReentrancyGuard} from "./ReentrancyGuard.sol";

contract BelayToken is ERC20 {
    address public owner;

    constructor() ERC20("BelayToken", "BLY") {
        owner = msg.sender;
        _mint(msg.sender, 1_000_000 * 10**18);
    }

    function mint(address to, uint amount) external {
        require(msg.sender == owner, "Only owner can mint");
        _mint(to, amount);
    }
}

contract Insurance is ReentrancyGuard {
    enum PolicyStatus {None, Available, Active, Completed, Terminated, UnderConsideration, WaitTerminate}
    enum Role { None, Insurer, Policyholder }

    struct PolicyData {
        uint64 startDate;
        uint64 endDate;
        uint64 durationWork;
        uint16 countOfPayout;
        bool hasPendingClaim;
        
        address insurer;
        address policyholder;
        uint payoutAmount;
        uint sumDeposits;
        
        string name;
        string conditions;
        PolicyStatus status;
    }

    struct User {
        uint8 autorise;
        Role role;
        uint[] policys;
        uint hashPass;
    }

    BelayToken public token;
    address public deployer;
    uint public constant MIN_PREMIUM = 10 * 10**18;
    uint public policyCounter;
    mapping(address => User) public addressToUser;
    mapping(uint => PolicyData) public policies;

    modifier onlyInsurer() {
        require(addressToUser[msg.sender].role == Role.Insurer, "Only insurers");
        require(addressToUser[msg.sender].autorise == 1, "Invalid status");
        _;
    }

    modifier onlyPolicyholder() {
        require(addressToUser[msg.sender].role == Role.Policyholder, "Only policyholders");
        require(addressToUser[msg.sender].autorise == 1, "Invalid status");
        _;
    }

    event Register(address indexed user, Role _role, uint256 timestamp);
    event Login(address indexed user, uint256 timestamp);
    event Logout(address indexed user, uint256 timestamp);

    event PolicyCreated(
        uint indexed policyId,
        address indexed insurer,
        string name,
        uint payoutAmount,
        uint durationWork,
        uint timestamp
    );

    event PolicySigned(
        address indexed insurer, 
        address indexed policyholder, 
        uint indexed policyId, 
        uint timestamp
    );
    
    event PolicyDeposited(
        address indexed policyholder, 
        uint indexed policyId, 
        uint amount, 
        uint timestamp
    );

    event PaymentRequest(
        uint indexed policyId, 
        address indexed policyholder, 
        string proofs, 
        uint timestamp
    );
    
    event TerminateRequest(
        address indexed insurer, 
        address indexed policyholder, 
        uint indexed policyId, 
        uint timestamp
    );

    event ClaimApproved(
        address indexed insurer, 
        address indexed policyholder, 
        uint indexed policyId, 
        uint amount, 
        uint timestamp
    );
    
    event ClaimRejected(
        address indexed insurer, 
        address indexed policyholder, 
        uint indexed policyId, 
        string reason, 
        uint timestamp
    );
    
    event PolicyTerminated(
        address indexed insurer, 
        address indexed policyholder, 
        uint indexed policyId, 
        uint timestamp
    );

    constructor(BelayToken _token) {
        require(address(_token) != address(0), "Token address cannot be zero");
        deployer = msg.sender;
        token = _token;
        policyCounter = 0;
    }

    function getUserInfo(address userAddress) external view returns (User memory) {
        return addressToUser[userAddress];
    }

    function getPolicyData(uint id) external view returns (PolicyData memory) {
        return policies[id];
    }

    function getPolicyCount() external view returns (uint) {
        return policyCounter;
    }

    function isRegistered(address userAddress) public view returns (bool) {
        return addressToUser[userAddress].role != Role.None;
    }

    function login(uint _hashPass) external returns (bool) {
        require(isRegistered(msg.sender), "Not registered");
        require(addressToUser[msg.sender].autorise == 0, "Invalid credentials");
        require(addressToUser[msg.sender].hashPass == _hashPass, "Incorrect password");

        addressToUser[msg.sender].autorise = 1;
        emit Login(msg.sender, block.timestamp);
        return true;
    }

    function logout() external {
        require(addressToUser[msg.sender].autorise == 1, "Invalid status");
        addressToUser[msg.sender].autorise = 0;
        emit Logout(msg.sender, block.timestamp);
    }

    function registration(uint _role, uint _hashPass) external {
        require(addressToUser[msg.sender].role == Role.None, "Already registered");
        require(_role == 1 || _role == 2, "Invalid role: 1=Insurer, 2=Policyholder");

        addressToUser[msg.sender] = User({
            autorise: 1,
            role: Role(_role),
            policys: new uint[](0),
            hashPass: _hashPass
        });

        emit Register(msg.sender, Role(_role), block.timestamp);
    }

    function createPolicy(
        string memory _name,
        string memory _conditions,
        uint _payoutAmount,
        uint _durationWork,
        uint _countOfPayout
    ) external onlyInsurer returns (uint) {
        policyCounter++;

        require(_durationWork <= type(uint64).max, "Duration too large");
        require(_countOfPayout <= type(uint16).max, "Count too large");
        require(_payoutAmount > 0, "Payout must be positive");

        policies[policyCounter] = PolicyData({
            name: _name,
            conditions: _conditions,
            payoutAmount: _payoutAmount,
            durationWork: uint64(_durationWork),
            startDate: 0,
            endDate: 0,
            status: PolicyStatus.Available,
            insurer: msg.sender,
            policyholder: address(0),
            sumDeposits: 0,
            countOfPayout: uint16(_countOfPayout),
            hasPendingClaim: false
        });

        addressToUser[msg.sender].policys.push(policyCounter);

        emit PolicyCreated(
            policyCounter,
            msg.sender,
            _name,
            _payoutAmount,
            _durationWork,
            block.timestamp
        );

        return policyCounter;
    }

    function approved(uint policyId) external onlyInsurer nonReentrant {
        require(policies[policyId].policyholder != address(0), "No policyholder assigned");
        require(policies[policyId].insurer == msg.sender, "Not your policy");
        require(policies[policyId].status == PolicyStatus.UnderConsideration, "Incorrect status");
        require(policies[policyId].countOfPayout > 0, "No payouts available");
        
        uint contractBalance = token.balanceOf(address(this));
        require(contractBalance >= policies[policyId].payoutAmount, "Insufficient contract funds");

        require(token.transfer(policies[policyId].policyholder, policies[policyId].payoutAmount), "Payment failed");
        policies[policyId].countOfPayout--;
        policies[policyId].sumDeposits -= policies[policyId].payoutAmount;

        if (policies[policyId].countOfPayout == 0) {
            policies[policyId].status = PolicyStatus.Completed;
        } else {
            policies[policyId].status = PolicyStatus.Active;
        }

        emit ClaimApproved(
            msg.sender,
            policies[policyId].policyholder, 
            policyId, 
            policies[policyId].payoutAmount,
            block.timestamp
        );
    }

    function rejected(uint policyId, string memory reason) external onlyInsurer {
        require(policies[policyId].insurer == msg.sender, "Not your policy");
        require(policies[policyId].status == PolicyStatus.UnderConsideration, "Incorrect status");

        policies[policyId].status = PolicyStatus.Active;

        emit ClaimRejected(
            msg.sender,
            policies[policyId].policyholder,
            policyId,
            reason,
            block.timestamp 
        );
    }

    function concludePolicy(uint policyId, uint premium) external onlyPolicyholder nonReentrant {
        require(policies[policyId].insurer != address(0), "Policy does not exist");
        require(policies[policyId].status == PolicyStatus.Available, "Policy already concluded");
        require(policies[policyId].policyholder == address(0), "Policy already has a policyholder");
        require(premium > 0, "Premium must be positive");
        require(premium >= MIN_PREMIUM, "Premium too small");

        require(token.balanceOf(msg.sender) >= premium, "Insufficient funds");
        require(token.transferFrom(msg.sender, address(this), premium), "Payment failed");

        policies[policyId].sumDeposits += premium;
        policies[policyId].startDate = uint64(block.timestamp);
        policies[policyId].endDate = uint64(block.timestamp + policies[policyId].durationWork);
        policies[policyId].policyholder = msg.sender;
        policies[policyId].status = PolicyStatus.Active;

        addressToUser[msg.sender].policys.push(policyId);

        emit PolicySigned(
            policies[policyId].insurer,
            msg.sender,
            policyId,
            block.timestamp
        );
    }

    function deposit(uint policyId, uint _amount) external onlyPolicyholder nonReentrant {
        require(policies[policyId].insurer != address(0), "Policy does not exist");
        require(policies[policyId].policyholder == msg.sender, "Not your policy");
        require(block.timestamp <= policies[policyId].endDate, "Policy has expired");
        require(_amount > 0, "Amount must be positive");

        require(token.balanceOf(msg.sender) >= _amount, "Insufficient funds");
        require(token.transferFrom(msg.sender, address(this), _amount), "Deposit failed");
        
        policies[policyId].sumDeposits += _amount;

        emit PolicyDeposited(
            msg.sender,
            policyId, 
            _amount, 
            block.timestamp
        );
    }

    function fileClaim(uint policyId, string memory _proofs) external onlyPolicyholder {
        require(policies[policyId].policyholder == msg.sender, "Not your policy");
        require(!policies[policyId].hasPendingClaim, "Claim already pending");
        require(
            block.timestamp <= policies[policyId].endDate &&
            policies[policyId].countOfPayout > 0 &&
            policies[policyId].status == PolicyStatus.Active,
            "Policy not active"
        );

        policies[policyId].hasPendingClaim = true;
        policies[policyId].status = PolicyStatus.UnderConsideration;

        emit PaymentRequest(
            policyId, 
            msg.sender, 
            _proofs, 
            block.timestamp
        );
    }

    function terminateRequest(uint policyId) external onlyPolicyholder {
        require(policies[policyId].policyholder == msg.sender, "Not your policy");
        require(
            block.timestamp <= policies[policyId].endDate &&
            policies[policyId].countOfPayout > 0 &&
            policies[policyId].status == PolicyStatus.Active,
            "Policy not active"
        );
        policies[policyId].status = PolicyStatus.WaitTerminate;
        
        emit TerminateRequest(
            policies[policyId].insurer,
            msg.sender,
            policyId, 
            block.timestamp
        );
    }

    function terminatePolicy(uint policyId) external onlyInsurer nonReentrant {
        require(policies[policyId].insurer == msg.sender, "Not your policy");
        require(
            block.timestamp <= policies[policyId].endDate &&
            policies[policyId].countOfPayout > 0 &&
            policies[policyId].status == PolicyStatus.WaitTerminate,
            "Policy not in termination state"
        );
        
        uint amount = policies[policyId].sumDeposits;
        require(token.balanceOf(address(this)) >= amount, "Insufficient contract funds");

        policies[policyId].status = PolicyStatus.Terminated;

        require(token.transfer(policies[policyId].policyholder, amount), "Payment failed");

        emit PolicyTerminated(
            msg.sender,
            policies[policyId].policyholder,
            policyId,
            block.timestamp
        );
    }
}