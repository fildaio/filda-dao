import brownie
import pytest
from brownie import chain, history
from brownie.test import given, strategy
from hypothesis import settings

ESTOKEN_AMOUNT = 10 ** 18

def test_mint(esToken, admin, bob):
    with brownie.reverts("only admin"):
        esToken.mint(bob, ESTOKEN_AMOUNT, {'from': bob})

    esToken.mint(bob, ESTOKEN_AMOUNT, {'from': admin})
    assert esToken.balanceOf(bob) == ESTOKEN_AMOUNT

def test_transfer_admin(esToken, admin, bob):
    with brownie.reverts("only admin"):
        esToken.transferAdmin(bob, {'from': bob})

    esToken.transferAdmin(bob, {'from': admin})

    with brownie.reverts("not pending admin"):
        esToken.acceptAdmin({'from': admin})
    esToken.acceptAdmin({'from': bob})

    assert esToken.admin() == bob

def test_set_handler(esToken, admin, bob, esTokenTool):
    with brownie.reverts("only admin"):
        esToken.setHandler(esTokenTool, {'from': bob})

    esToken.setHandler(esTokenTool, {'from': admin})
    assert esToken.handler() == esTokenTool
