// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

interface IEsToken {
    function claim_for(address _account, uint256 _amount) external;

    function stake_for(address _account, uint256 _amount) external;

    function balanceOf(address _account) view external returns (uint256);

    function depositToVe_for(address _account, uint256 _amount) external;
}
