import json
import os

from .. import deployment_config as config
from .. import deploy_dao as dao

from brownie import network

DEPLOYMENTS_JSON = "scripts/" + network.main.show_active() + "/deployments.json"
GAUGE_JSON = "scripts/" + network.main.show_active() + "/gauge.json"

DAO_TOKEN = '0x00E71352c91Ff5B820ab4dF08bb47653Db4e32C0'
POLICYMAKER_REWARD = 10 ** 18

# name, type weight
GAUGE_TYPES = [
    ("Liquidity", 10 ** 18),
]

# lp token, default point rate, point proportion, reward token, reward rate, gauge weight
POOL_TOKENS = {
    "HUSD": ("0xF9Ca2eA3b1024c0DB31adB224B407441bECC18BB", 0, 0, "0x42C8A982f42b6069AD310e9910468B593247eace", 0, 20),
    "BUSD": ("0x9f1d0Ed4E041C503BD487E5dc9FC935Ab57F9a57", 0, 0, "0x21c376438dA428F730249aEe27F4454358429974", 0, 20),
    "USDC": ("0xA06be0F5950781cE28D965E5EFc6996e88a8C141", 0, 0, "0x7bC72d7780C2E811814e81FFac828d53f4CDe7c2", 0, 50)
}

def deploy():
    print(DEPLOYMENTS_JSON)
    admin = config.get_live_admin()
    voting_escrow = dao.deploy_part_one(admin, DAO_TOKEN, config.REQUIRED_CONFIRMATIONS, DEPLOYMENTS_JSON)

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

