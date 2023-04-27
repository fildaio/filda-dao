// SPDX-License-Identifier: MIT
pragma solidity ^0.8.9;

import "@openzeppelin/contracts/utils/Address.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IComptroller.sol";
import "./EsToken.sol";

contract EsTokenTool is Ownable {
    using Address for address;

    IComptroller public comptroller;
    EsToken public esToken;

    constructor(address _comptroller) {
        require(_comptroller.isContract(), "comptroller is not contract");

        comptroller = IComptroller(_comptroller);
        esToken = EsToken(comptroller.getCompAddress());
    }

    function stake(uint256 _amount) external {
        comptroller.claimComp(msg.sender);
        uint256 bal = esToken.balanceOf(msg.sender);
        uint amount = _amount > bal ? bal : _amount;

        esToken.stake_for(msg.sender, amount);
    }

    function claim(uint256 _amount) external {
        comptroller.claimComp(msg.sender);
        uint256 bal = esToken.balanceOf(msg.sender);
        uint amount = _amount > bal ? bal : _amount;

        esToken.claim_for(msg.sender, amount);
    }

}
