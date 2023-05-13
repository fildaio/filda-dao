import json
import os

from .. import deployment_config as config
from .. import deploy_dao as dao

from brownie import network

DEPLOYMENTS_JSON = "scripts/" + network.main.show_active() + "/deployments.json"
GAUGE_JSON = "scripts/" + network.main.show_active() + "/gauge.json"

DAO_TOKEN = '0x56c0fa757820c2d9df35cf2874f3268fe717e92f'
xDAO_TOKEN = '0xF1776f8C752B2f897970F27264A1bff3b1597e12'
POLICYMAKER_REWARD = 21333.2 * 10 ** 18

# name, type weight
GAUGE_TYPES = [
    ("Liquidity", 10 ** 18),
]

# lp token, default point rate, point proportion, reward token, reward rate, gauge weight
POOL_TOKENS = {
    "BTT": ("0xE52792E024697A6be770e5d6F1C455550265B2CD", 0, 10000000000000000, "0x107742EB846b86CEaAF7528D5C85cddcad3e409A", 0, 20),
    "USDT": ("0x541a9133c24bFAb3BD55742b1F16B507b1FBBf44", 0, 10000000000000000, "0x834982c9B0690ED7CA35e10b18887C26c25CdC82", 0, 40),
}

def deploy():
    print(DEPLOYMENTS_JSON)
    admin = config.get_live_admin()
    voting_escrow = dao.deploy_part_one(admin, DAO_TOKEN, xDAO_TOKEN, config.REQUIRED_CONFIRMATIONS, DEPLOYMENTS_JSON)

    dao.deploy_part_two(
        admin, DAO_TOKEN, voting_escrow, POLICYMAKER_REWARD, GAUGE_TYPES, POOL_TOKENS, config.REQUIRED_CONFIRMATIONS, DEPLOYMENTS_JSON
    )

def add_gauge():
    admin = config.get_live_admin()

    with open(GAUGE_JSON) as fp:
        gauge_json = json.load(fp)

    with open(DEPLOYMENTS_JSON) as fp:
        deployments = json.load(fp)

    dao.add_gauge(admin, gauge_json["name"], deployments["Minter"], deployments["RewardPolicyMaker"],
            gauge_json["cToken"], eval(gauge_json["pointRate"]), eval(gauge_json["pointProportion"]),
            gauge_json["rewardToken"], eval(gauge_json["rewardRate"]), gauge_json["weight"],
            config.REQUIRED_CONFIRMATIONS, DEPLOYMENTS_JSON)

def deploy_helper():
    admin = config.get_live_admin()
    dao.deploy_reward_helper(admin, DEPLOYMENTS_JSON, config.REQUIRED_CONFIRMATIONS)

