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

def test_claim(esToken, token, bob, penaltyReceiver):
    assert token.balanceOf(bob) == 0
    esToken.claim(ESTOKEN_AMOUNT, {'from': bob})
    assert esToken.balanceOf(bob) == 0
    assert token.balanceOf(bob) == ESTOKEN_AMOUNT / 2
    assert token.balanceOf(penaltyReceiver) == ESTOKEN_AMOUNT / 2

def test_claim_revert(esToken, bob):
    with brownie.reverts("can not claim zero"):
        esToken.claim(0, {'from': bob})

def test_claim_for_revert(esToken, bob, penaltyReceiver):
    with brownie.reverts("only handler"):
        esToken.claim_for(bob, ESTOKEN_AMOUNT, {'from': penaltyReceiver})

def test_claim_exceed_balance(esToken, bob):
    with brownie.reverts("ERC20: burn amount exceeds balance"):
        esToken.claim(ESTOKEN_AMOUNT * 2, {'from': bob})
