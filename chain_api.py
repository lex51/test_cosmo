import requests
import json

# import hashlib

from requests.exceptions import JSONDecodeError, ReadTimeout
from tinydb import TinyDB, Query
from db_crud import chain_monitoring_by_user

# from utils import get_last_proposals, get_last_proposals_range
from trello_api import get_last_id_trello_by_chain, select_prop_for_publ_trello
from conf import Conf

import asyncio

from loguru import logger as lg

lg.add("logs/chain_monitor.log", level="DEBUG")


with open("chains.json", "r") as f:
    all_chain_data = json.load(f)


def get_props_chain(chain):

    try:
        chain_api_list = [
            i.get("api") for i in all_chain_data if i.get("addr_prefix") == chain
        ][0]
        chain_name = [
            i.get("chain_name") for i in all_chain_data if i.get("addr_prefix") == chain
        ][0]
    except BaseException as be:
        lg.warning(f"catch {be} \n{chain} - chain")
        return "", ""
    for api in chain_api_list:
        try:
            url = f"{api}/cosmos/gov/v1beta1/proposals"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                break
        except (JSONDecodeError, ReadTimeout) as err:
            lg.warning(f"catch {err} for\n{api}\n{chain} - chain")
    return r.json(), chain_name


async def monitoring_chains_for_users(period=Conf.monitoring_period):
    """period in minutes"""
    while True:

        # TODO work with db take it to db_crud
        db = TinyDB("db.json")
        chains_table = db.table("chains")

        try:
            user_monitoring_list = await chain_monitoring_by_user()

            user_monitoring_list = [
                chains_table.search(Query().name == i)[0].get("chain")
                for i in user_monitoring_list
            ]
        except IndexError:
            lg.warning("problem with get index in chain_monitoring_list")
            continue

        for chain_pref in user_monitoring_list:
            try:
                prop, chain_name = get_props_chain(chain_pref)
                chain_prop_data = prop
                # print(await get_last_id_trello_by_chain(chain_name))
                await select_prop_for_publ_trello(
                    prop["proposals"], chain_name, chain_pref
                )

            except BaseException:
                continue

            # asyncio.sleep(60)  # * period)
            # time.sleep(60 * period)
        await asyncio.sleep(60 * period)
