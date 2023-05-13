// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";
import "../interfaces/IComptroller.sol";

contract MockComptroller is IComptroller {
    using SafeERC20 for IERC20;

    IERC20 public comp;

    constructor(address _comp) {
        comp = IERC20(_comp);
    }

    function claimComp(address holder) external {
        comp.safeTransfer(holder, 1e18);
    }

    function getCompAddress() external view returns (address) {
        return address(comp);
    }
}
