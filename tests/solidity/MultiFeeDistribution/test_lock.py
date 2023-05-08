import brownie
import pytest
from brownie import chain, history
from brownie.test import given, strategy
from hypothesis import settings

ESTOKEN_AMOUNT = 10 ** 18
DAY = 86400

LOCK_DURATION = DAY * 7

@pytest.fixture(scope="module", autouse=True)
def setup(token, esToken, admin, alice, bob):
    # We handle setup logic in a fixture to avoid repeating it in each test run

    esToken.mint(bob, ESTOKEN_AMOUNT, {'from': admin})
    token.mint(esToken.address, ESTOKEN_AMOUNT, {'from': alice})

def test_lock_unlock(distribution, token, esToken, bob):
    esToken.stake(ESTOKEN_AMOUNT, {'from': bob})

    assert token.balanceOf(distribution) == ESTOKEN_AMOUNT

    t0 = chain.time()
    unlock_time = t0 // DAY * DAY + LOCK_DURATION - t0
    chain.sleep(unlock_time)
    chain.mine()

    (total, unlockable, locked, array) = distribution.lockedBalances(bob)
    assert total == ESTOKEN_AMOUNT
    assert unlockable == ESTOKEN_AMOUNT
    assert locked == 0

    distribution.withdrawExpiredLocks({'from': bob})
    assert token.balanceOf(distribution) == 0
    assert token.balanceOf(bob) == ESTOKEN_AMOUNT

def test_lock_multi(distribution, token, esToken, bob):
    amount = ESTOKEN_AMOUNT / 2

    esToken.stake(amount, {'from': bob})

    t0 = chain.time()
    chain.sleep(DAY)
    chain.mine()

    esToken.stake(amount, {'from': bob})

    unlock_time = t0 // DAY * DAY + LOCK_DURATION - DAY
    chain.sleep(unlock_time - t0)
    chain.mine()

    (total, unlockable, locked, array) = distribution.lockedBalances(bob)
    assert total == ESTOKEN_AMOUNT
    assert unlockable == amount
    assert locked == amount

    distribution.withdrawExpiredLocks({'from': bob})
    assert token.balanceOf(distribution) == amount
    assert token.balanceOf(bob) == amount

    chain.sleep(DAY)
    chain.mine()

    distribution.withdrawExpiredLocks({'from': bob})
    assert token.balanceOf(distribution) == 0
    assert token.balanceOf(bob) == ESTOKEN_AMOUNT
