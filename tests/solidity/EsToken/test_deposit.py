import brownie
import pytest
from brownie import chain, history
from brownie.test import given, strategy
from hypothesis import settings
from tests.conftest import approx

ESTOKEN_AMOUNT = 10 ** 18
DAY = 86400

WEEK = DAY * 7
MAXTIME = 126144000
TOL = 3600 / WEEK

@pytest.fixture(scope="module", autouse=True)
def setup(token, voting_escrow, esToken, admin, alice, bob):
    # We handle setup logic in a fixture to avoid repeating it in each test run

    esToken.mint(bob, ESTOKEN_AMOUNT*2, {'from': admin})
    token.mint(esToken.address, ESTOKEN_AMOUNT*2, {'from': alice})

    esToken.setVeToken(voting_escrow.address, {'from': admin})

    voting_escrow.change_deposit_whitelist(esToken.address, 1, {'from': alice})
    token.approve(voting_escrow.address, ESTOKEN_AMOUNT * 10, {"from": bob})

def test_deposit(esToken, token, voting_escrow, alice, bob):
    with brownie.reverts("create lock first"):
        esToken.depositToVe(ESTOKEN_AMOUNT, {'from': bob})

    token.mint(bob, ESTOKEN_AMOUNT, {'from': alice})
    voting_escrow.create_lock(ESTOKEN_AMOUNT, chain[-1].timestamp + MAXTIME, {'from': bob})

    esToken.depositToVe(ESTOKEN_AMOUNT, {'from': bob})
    assert esToken.balanceOf(bob) == ESTOKEN_AMOUNT
    assert approx(voting_escrow.balanceOf(bob), ESTOKEN_AMOUNT * 2, TOL)

def test_deposit_zero(esToken, token, voting_escrow, alice, bob):
    token.mint(bob, ESTOKEN_AMOUNT, {'from': alice})
    t0 = chain.time()
    voting_escrow.create_lock(ESTOKEN_AMOUNT, t0 + MAXTIME, {'from': bob})

    with brownie.reverts("can not deposit zero"):
        esToken.depositToVe(0, {'from': bob})

def test_deposit_for(esToken, bob, penaltyReceiver):
    with brownie.reverts("only handler"):
        esToken.depositToVe_for(bob, ESTOKEN_AMOUNT, {'from': penaltyReceiver})

def test_vetoken_unlock(esToken, voting_escrow, admin, bob):
    voting_escrow.create_lock_by_xtoken(ESTOKEN_AMOUNT, chain[-1].timestamp + MAXTIME, {'from': bob})

    assert approx(voting_escrow.balanceOf(bob), ESTOKEN_AMOUNT, TOL)

    with brownie.reverts("only VeToken"):
        esToken.unlock(bob, ESTOKEN_AMOUNT, {'from': bob})

def test_deposit_unlock_by_vetoken(esToken, voting_escrow, admin, bob):
    voting_escrow.create_lock_by_xtoken(ESTOKEN_AMOUNT, chain[-1].timestamp + MAXTIME, {'from': bob})

    esToken.depositToVe(ESTOKEN_AMOUNT, {'from': bob})
