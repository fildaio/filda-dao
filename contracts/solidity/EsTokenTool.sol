// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IComptroller.sol";
import "./interfaces/IEsToken.sol";

contract EsTokenTool is Ownable {
    using Address for address;

    IComptroller public comptroller;
    IEsToken public esToken;

    constructor(address _comptroller, address _esToken) {
        require(_comptroller.isContract(), "comptroller is not contract");
        require(_esToken.isContract(), "estoken is not contract");

        comptroller = IComptroller(_comptroller);
        esToken = IEsToken(_esToken);
    }

    function stake() external {
        comptroller.claimComp(msg.sender);
        uint256 bal = esToken.balanceOf(msg.sender);

        esToken.stake_for(msg.sender, bal);
    }

    function claim() external {
        comptroller.claimComp(msg.sender);
        uint256 bal = esToken.balanceOf(msg.sender);

        esToken.claim_for(msg.sender, bal);
    }

    function depositToVe() external {
        comptroller.claimComp(msg.sender);
        uint256 bal = esToken.balanceOf(msg.sender);

        esToken.depositToVe_for(msg.sender, bal);
    }
}
