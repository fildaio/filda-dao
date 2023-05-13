import brownie
import pytest
from brownie import chain, history
from brownie.test import given, strategy
from hypothesis import settings

ESTOKEN_AMOUNT = 10 ** 18
DAY = 86400

@pytest.fixture(scope="module", autouse=True)
def setup(token, voting_escrow, esToken, admin, alice, bob, comptroller):
    # We handle setup logic in a fixture to avoid repeating it in each test run

    esToken.mint(comptroller, ESTOKEN_AMOUNT * 2, {'from': admin})
    token.mint(esToken.address, ESTOKEN_AMOUNT * 2, {'from': alice})

    esToken.setVeToken(voting_escrow.address, {'from': admin})
    voting_escrow.change_deposit_whitelist(esToken.address, 1, {'from': alice})
    token.approve(voting_escrow.address, ESTOKEN_AMOUNT * 10, {"from": bob})

def test_stake(esTokenTool, esToken, token, bob, distribution):
    esTokenTool.stake({'from': bob})
    assert esToken.balanceOf(bob) == 0

    (total, unlockable, locked, array) = distribution.lockedBalances(bob)
    assert total == ESTOKEN_AMOUNT
    assert unlockable == 0
    assert locked == ESTOKEN_AMOUNT
    assert token.balanceOf(distribution) == ESTOKEN_AMOUNT

def test_stake_multi(esTokenTool, esToken, bob, distribution):
    esTokenTool.stake({'from': bob})
    assert esToken.balanceOf(bob) == 0

    chain.sleep(DAY)
    chain.mine()
    esTokenTool.stake({'from': bob})

    (total, unlockable, locked, array) = distribution.lockedBalances(bob)
    assert total == ESTOKEN_AMOUNT * 2
    assert unlockable == 0
    assert locked == ESTOKEN_AMOUNT * 2


def test_claim(esTokenTool, esToken, token, bob, penaltyReceiver):
    esTokenTool.claim({'from': bob})

    assert esToken.balanceOf(bob) == 0
    assert token.balanceOf(bob) == ESTOKEN_AMOUNT / 2
    assert token.balanceOf(penaltyReceiver) == ESTOKEN_AMOUNT / 2

def test_deposit(esTokenTool, esToken, voting_escrow, token, alice, bob):
    with brownie.reverts("create lock first"):
        esTokenTool.depositToVe({'from': bob})

    token.mint(bob, ESTOKEN_AMOUNT, {'from': alice})
    t0 = chain.time()
    voting_escrow.create_lock(ESTOKEN_AMOUNT, t0 + DAY * 120, {'from': bob})
    esTokenTool.depositToVe({'from': bob})

    assert esToken.balanceOf(bob) == 0
    assert voting_escrow.balanceOf(bob) != 0
