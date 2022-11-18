import requests
import json
import hashlib

from requests.exceptions import JSONDecodeError, ReadTimeout
from tinydb import TinyDB, Query
from db_crud import chain_monitoring_by_user
from utils import get_last_proposals, get_last_proposals_range
from trello_api import post_card_to_trello
import time
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
        user_monitoring_list = await chain_monitoring_by_user()
        user_monitoring_list = [
            chains_table.search(Query().name == i)[0].get("chain")
            for i in user_monitoring_list
        ]

        for chain in user_monitoring_list:
            try:
                prop, chain_name = get_props_chain(chain)
                json_dump = json.dumps(prop)
                md5_hash = hashlib.md5(json_dump.encode("utf-8")).hexdigest()
                if (
                    bool(chains_table.search(Query().chain == chain)) is False
                    or chains_table.search(Query().chain == chain)[0].get("last_prop")
                    is None
                ) and (
                    chains_table.search(Query().chain == chain)[0].get("hash") == md5_hash
                    or chains_table.search(Query().chain == chain)[0].get("hash") is None
                ):
                    lg.info(f"no new records in chain monitoring list for {chain}")
                    chains_table.update(
                        {
                            "chain": chain,
                            "hash": md5_hash,
                            "last_pror": get_last_proposals(prop)
                            # "status" : "bad" if repr(js_decode_err) else "ok"
                        },
                        Query().chain == chain,
                    )
                if chains_table.search(Query().chain == chain)[0].get("hash") != md5_hash:
                    prop_for_update = get_last_proposals_range(
                        prop,
                        chains_table.search(Query().chain == chain)[0].get("last_pror"),
                    )

                    # INFO UPDATED
                    lg.info(f"find {len(prop_for_update)} records for {chain_name}")
                    post_card_to_trello(prop_for_update, chain, chain_name)

                    chains_table.update(
                        {
                            "hash": md5_hash,
                            # "last_pror": get_last_proposals(prop) #update only hash and on next iteration apdates last_prop
                        },
                        Query().chain == chain,
                    )
            except BaseException:
                continue

            # asyncio.sleep(60)  # * period)
            # time.sleep(60 * period)
        await asyncio.sleep(60 * period)
