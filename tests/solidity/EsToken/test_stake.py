import brownie
import pytest
from brownie import chain, history
from brownie.test import given, strategy
from hypothesis import settings

ESTOKEN_AMOUNT = 10 ** 18
DAY = 86400

@pytest.fixture(scope="module", autouse=True)
def setup(token, esToken, admin, alice, bob):
    # We handle setup logic in a fixture to avoid repeating it in each test run

    esToken.mint(bob, ESTOKEN_AMOUNT, {'from': admin})
    token.mint(esToken.address, ESTOKEN_AMOUNT, {'from': alice})

def test_stake(esToken, bob, distribution):
    esToken.stake(ESTOKEN_AMOUNT, {'from': bob})
    assert esToken.balanceOf(bob) == 0

    (total, unlockable, locked, array) = distribution.lockedBalances(bob)
    assert total == ESTOKEN_AMOUNT
    assert unlockable == 0
    assert locked == ESTOKEN_AMOUNT

def test_stake_revert(esToken, bob):
    with brownie.reverts("can not stake zero"):
        esToken.stake(0, {'from': bob})

def test_stake_for_revert(esToken, bob, penaltyReceiver):
    with brownie.reverts("only handler"):
        esToken.stake_for(bob, ESTOKEN_AMOUNT, {'from': penaltyReceiver})

def test_stake_multi(esToken, bob):
    esToken.stake(ESTOKEN_AMOUNT / 2, {'from': bob})
    assert esToken.balanceOf(bob) == ESTOKEN_AMOUNT / 2

    chain.sleep(DAY)
    chain.mine()
    esToken.stake(ESTOKEN_AMOUNT / 2, {'from': bob})
    assert esToken.balanceOf(bob) == 0

def test_stake_exceed_balance(esToken, bob):
    with brownie.reverts("ERC20: burn amount exceeds balance"):
        esToken.stake(ESTOKEN_AMOUNT * 2, {'from': bob})
