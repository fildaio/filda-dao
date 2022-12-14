import itertools

import brownie
import pytest

TYPE_WEIGHTS = [5e17, 1e19]
GAUGE_WEIGHTS = [1e19, 1e18, 5e17]
GAUGE_TYPES = [0, 0, 1]

MONTH = 86400 * 30
WEEK = 7 * 86400


@pytest.fixture(scope="module", autouse=True)
def minter_setup(accounts, gauge_controller, three_gauges,
        coin_a, coin_b, coin_c, mock_lp_token_A, mock_lp_token_B, mock_lp_token_C, chain):

    # ensure the tests all begin at the start of the epoch week
    chain.mine(timestamp=(chain.time() / WEEK + 1) * WEEK)

    # set types
    for weight in TYPE_WEIGHTS:
        gauge_controller.add_type(b"Liquidity", weight, {"from": accounts[0]})

    # add gauges
    for i in range(3):
        gauge_controller.add_gauge(
            three_gauges[i], GAUGE_TYPES[i], GAUGE_WEIGHTS[i], {"from": accounts[0]}
        )

    # transfer tokens
    for acct in accounts[1:4]:
        coin_a._mint_for_testing(acct, 1e18)
        coin_b._mint_for_testing(acct, 1e18)
        coin_c._mint_for_testing(acct, 1e18)

    # approve gauges
    for gauge, acct in itertools.product(three_gauges, accounts[1:4]):
        coin_a.approve(mock_lp_token_A, 1e18, {"from": acct})
        coin_b.approve(mock_lp_token_B, 1e18, {"from": acct})
        coin_c.approve(mock_lp_token_C, 1e18, {"from": acct})


def test_mint(accounts, chain, three_gauges, minter, token, mock_lp_token_A):
    #deposit to three_gauges[0]
    mock_lp_token_A.deposit(1e18, {"from": accounts[1]})

    chain.sleep(MONTH)
    minter.mint(three_gauges[0], {"from": accounts[1]})
    expected = three_gauges[0].integrate_fraction(accounts[1])

    assert expected > 0
    assert token.balanceOf(accounts[1]) == expected
    assert minter.minted(accounts[1], three_gauges[0]) == expected


def test_mint_immediate(accounts, chain, three_gauges, minter, token, mock_lp_token_A):
    #deposit to three_gauges[0]
    mock_lp_token_A.deposit(1e18, {"from": accounts[1]})
    t0 = chain.time()
    chain.sleep((t0 + WEEK) // WEEK * WEEK - t0 + 1)  # 1 second more than enacting the weights

    minter.mint(three_gauges[0], {"from": accounts[1]})
    balance = token.balanceOf(accounts[1])

    assert balance > 0
    assert minter.minted(accounts[1], three_gauges[0]) == balance


def test_mint_multiple_same_gauge(accounts, chain, three_gauges, minter, token, mock_lp_token_A):
    #deposit to three_gauges[0]
    mock_lp_token_A.deposit(1e18, {"from": accounts[1]})

    chain.sleep(MONTH)
    minter.mint(three_gauges[0], {"from": accounts[1]})
    balance = token.balanceOf(accounts[1])

    chain.sleep(MONTH)
    minter.mint(three_gauges[0], {"from": accounts[1]})
    expected = three_gauges[0].integrate_fraction(accounts[1])
    final_balance = token.balanceOf(accounts[1])

    assert final_balance > balance
    assert final_balance == expected
    assert minter.minted(accounts[1], three_gauges[0]) == expected


def test_mint_multiple_gauges(accounts, chain, three_gauges, minter, token, mock_lp_token_A, mock_lp_token_B, mock_lp_token_C):
     #deposit to three_gauges
    mock_lp_token_A.deposit(10 ** 17, {"from": accounts[1]})
    mock_lp_token_B.deposit(2 * 10 ** 17, {"from": accounts[1]})
    mock_lp_token_C.deposit(3 * 10 ** 17, {"from": accounts[1]})

    chain.sleep(MONTH)

    for i in range(3):
        minter.mint(three_gauges[i], {"from": accounts[1]})

    total_minted = 0
    for i in range(3):
        gauge = three_gauges[i]
        minted = minter.minted(accounts[1], gauge)
        assert minted == gauge.integrate_fraction(accounts[1])
        total_minted += minted

    assert token.balanceOf(accounts[1]) == total_minted


def test_mint_after_withdraw(accounts, chain, three_gauges, minter, token, mock_lp_token_A):
    #deposit to three_gauges[0]
    mock_lp_token_A.deposit(1e18, {"from": accounts[1]})

    chain.sleep(2 * WEEK)
    mock_lp_token_A.withdraw(1e18, {"from": accounts[1]})
    minter.mint(three_gauges[0], {"from": accounts[1]})

    assert token.balanceOf(accounts[1]) > 0


def test_mint_multiple_after_withdraw(accounts, chain, three_gauges, minter, token, mock_lp_token_A):
    #deposit to three_gauges[0]
    mock_lp_token_A.deposit(1e18, {"from": accounts[1]})

    chain.sleep(10)
    mock_lp_token_A.withdraw(1e18, {"from": accounts[1]})
    minter.mint(three_gauges[0], {"from": accounts[1]})
    balance = token.balanceOf(accounts[1])

    chain.sleep(10)
    minter.mint(three_gauges[0], {"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == balance


def test_no_deposit(accounts, chain, three_gauges, minter, token):
    minter.mint(three_gauges[0], {"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == 0
    assert minter.minted(accounts[1], three_gauges[0]) == 0


def test_mint_wrong_gauge(accounts, chain, three_gauges, minter, token, mock_lp_token_A):
    #deposit to three_gauges[0]
    mock_lp_token_A.deposit(1e18, {"from": accounts[1]})

    chain.sleep(MONTH)
    minter.mint(three_gauges[1], {"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == 0
    assert minter.minted(accounts[1], three_gauges[0]) == 0
    assert minter.minted(accounts[1], three_gauges[1]) == 0


def test_mint_not_a_gauge(accounts, minter):
    with brownie.reverts("dev: gauge is not added"):
        minter.mint(accounts[1], {"from": accounts[0]})


def test_mint_before_inflation_begins(accounts, chain, three_gauges, minter, token, reward_policy_maker, mock_lp_token_A):
    #deposit to three_gauges[0]
    mock_lp_token_A.deposit(1e18, {"from": accounts[1]})

    chain.sleep(reward_policy_maker.epoch_start_time(reward_policy_maker.epoch_at(chain.time())) - chain.time() - 5)
    minter.mint(three_gauges[0], {"from": accounts[1]})

    assert token.balanceOf(accounts[1]) == 0
    assert minter.minted(accounts[1], three_gauges[0]) == 0
