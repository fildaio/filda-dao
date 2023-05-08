// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

interface IVotingEscrow {
    function deposit_for(address addr, uint256 amount) external;

    function locked(address addr) external view returns(int128 amount, uint256 end);
}
