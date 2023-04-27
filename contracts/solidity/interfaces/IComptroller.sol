// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

interface IComptroller {
    function claimComp(address holder) external;
    function getCompAddress() external view returns (address);
}
