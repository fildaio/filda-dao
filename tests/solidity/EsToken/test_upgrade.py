import brownie
import pytest
from brownie import chain, history
from brownie.test import given, strategy
from hypothesis import settings

def test_initilize(esToken, admin, token, distribution, penaltyReceiver):
    with brownie.reverts("Initializable: contract is already initialized"):
        esToken.initialize(token, admin, distribution, penaltyReceiver, 10 ** 24 * 5, {'from': admin})
