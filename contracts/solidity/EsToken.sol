// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts-upgradeable/token/ERC20/extensions/ERC20CappedUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/IERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/security/ReentrancyGuardUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/token/ERC20/utils/SafeERC20Upgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/AddressUpgradeable.sol";
import "@openzeppelin/contracts-upgradeable/utils/math/SafeMathUpgradeable.sol";
import "./interfaces/IMultiFeeDistribution.sol";
import "./interfaces/IVotingEscrow.sol";

contract EsToken is ERC20CappedUpgradeable, ReentrancyGuardUpgradeable {
    using AddressUpgradeable for address;
    using SafeERC20Upgradeable for IERC20Upgradeable;
    using SafeMathUpgradeable for uint256;

    address public underlying;
    address public admin;
    address public pendingAdmin;
    IMultiFeeDistribution public distribution;
    address public penaltyReceiver;

    address public handler;

    IVotingEscrow public veToken;

    event AdminChanged(address indexed admin);
    event PenaltyReceiverChanged(address indexed receiver);
    event HandlerChanged(address indexed handler);
    event Claimed(address indexed account, uint256 burnedAmount, uint256 receivedAmount);
    event PenaltyTransfered(address indexed receiver, uint256 amount);
    event VeTokenChanged(address indexed veToken);
    event Unlocked(address indexed account, uint256 amount);

    modifier onlyAdmin {
        require(msg.sender == admin, "only admin");
        _;
    }

    modifier onlyHandler {
        require(msg.sender == handler, "only handler");
        _;
    }

    modifier onlyVeToken {
        require(address(veToken) != address(0), "set vetoken first");
        require(msg.sender == address(veToken), "only VeToken");
        _;
    }

    function initialize(address _underlying, address _admin, address _distribution, address _penaltyReceiver, uint256 cap_) public initializer {
        __ERC20Capped_init(cap_);
        __ERC20_init("xFilDA on BTTC", "xFilDA");

        require(_underlying.isContract(), "underlying token must be contract");
        require(_distribution.isContract(), "distribution must be contract");
        require(_admin != address(0), "admin can not be zero address");

        underlying = _underlying;
        admin = _admin;
        distribution = IMultiFeeDistribution(_distribution);
        penaltyReceiver = _penaltyReceiver;
    }

    function mint(address _account, uint256 _amount) external onlyAdmin {
        _mint(_account, _amount);
    }

    function transferAdmin(address _newAdmin) external onlyAdmin {
        pendingAdmin = _newAdmin;
    }

    function acceptAdmin() external {
        require(pendingAdmin != address(0) && msg.sender == pendingAdmin, "not pending admin");
        admin = pendingAdmin;
        pendingAdmin == address(0);
        emit AdminChanged(admin);
    }

    function setPenaltyReceiver(address _penaltyReceiver) external onlyAdmin {
        penaltyReceiver = _penaltyReceiver;
        emit PenaltyReceiverChanged(_penaltyReceiver);
    }

    function setHandler(address _handler) external onlyAdmin {
        handler = _handler;
        emit HandlerChanged(_handler);
    }

    function _stake_for(address _account, uint256 _amount) internal {
        require(_amount > 0, "can not stake zero");

        _burn(_account, _amount);

        IERC20Upgradeable(underlying).approve(address(distribution), _amount);
        distribution.stake(_amount, true, _account);
    }

    function stake(uint256 _amount) external nonReentrant {
        _stake_for(msg.sender, _amount);
    }

    function stake_for(address _account, uint256 _amount) external onlyHandler nonReentrant {
        _stake_for(_account, _amount);
    }

    function _claim_for(address _account, uint256 _amount) internal {
        require(_amount > 0, "can not claim zero");

        _burn(_account, _amount);

        uint256 underlyingAmount = _amount.div(2);
        IERC20Upgradeable(underlying).safeTransfer(_account, underlyingAmount);
        emit Claimed(_account, _amount, underlyingAmount);

        uint256 penalty = _amount.sub(underlyingAmount);
        IERC20Upgradeable(underlying).safeTransfer(penaltyReceiver, penalty);
        emit PenaltyTransfered(penaltyReceiver, penalty);
    }

    // claim will
    function claim(uint256 _amount) external nonReentrant {
        _claim_for(msg.sender, _amount);
    }

    function claim_for(address _account, uint256 _amount) external onlyHandler nonReentrant {
        _claim_for(_account, _amount);
    }

    function setVeToken(address _veToken) external onlyAdmin {
        veToken = IVotingEscrow(_veToken);
        emit VeTokenChanged(_veToken);
    }

    function _depositToVe_for(address _account, uint256 _amount) internal {
        require(_amount > 0, "can not deposit zero");

        (int128 amount, ) = veToken.locked(_account);
        require(amount > 0, "create lock first");

        _unlock(_account, _amount);
        veToken.deposit_for(_account, _amount);
    }

    function depositToVe_for(address _account, uint256 _amount) external onlyHandler nonReentrant {
        _depositToVe_for(_account, _amount);
    }

    function depositToVe(uint256 _amount) external {
        _depositToVe_for(msg.sender, _amount);
    }

    function _unlock(address _account, uint256 _amount) internal {
        _burn(_account, _amount);
        IERC20Upgradeable(underlying).safeTransfer(_account, _amount);
    }

    function unlock(address _account, uint256 _amount) external onlyVeToken {
        _unlock(_account, _amount);
        emit Unlocked(_account, _amount);
    }
}
