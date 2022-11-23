from conf import Conf

import requests

import datetime 
from dateutil import parser

from loguru import logger as lg

lg.add("logs/trello_monitor.log", level="DEBUG")


url = "https://api.trello.com/1/cards"
headers = {"Accept": "application/json"}


async def post_card_to_board(prop: dict, chain_pref: str, chain_name: str):

    try:
        query = {
            "idList": Conf.trello_board_column_id,
            "key": Conf.trello_key,
            "token": Conf.trello_sec,
            "name": f"{chain_name} - {prop.get('proposal_id')}",
            "due": prop.get("voting_end_time"),
            "urlSource": f"ping.pub/{chain_name}/gov/{prop.get('proposal_id')}",
        }

        requests.request("POST", url, headers=headers, params=query)
        lg.info(f'OK added prop {chain_name} - NO {prop.get("proposal_id")}')
    except BaseException as BE:
        lg.warning(f'catch {BE}')



# all cards from board
async def get_all_cards_from_board() -> list:
    
    try:
        query = {
            "key": Conf.trello_key,
            "token": Conf.trello_sec,
        }
        url = f"https://api.trello.com/1/boards/{Conf.trello_board_id}/cards"

        response = requests.request(
        "GET",
        url,
        params=query
        )

        return response.json()
    except BaseException as BE:
        lg.warning(f'catch error {BE}')
        return {}


async def get_card_info(id) -> tuple:

    try:
        query = {
            "key": Conf.trello_key,
            "token": Conf.trello_sec,
        }

        url = f"https://api.trello.com/1/cards/{id}"
        response = requests.request(
            "GET",
            url,
            headers=headers,
            params=query
        )
        card_info = response.json()
        # return response.json()
        return ( card_info['name'].split(" - ")[0], card_info['name'].split(" - ")[1] )
    except BaseException as BE:
        lg.warning(f'catch {BE} for card id {id}')


async def get_last_id_trello_by_chain(chain):
    """last prop id from trello board for chain"""
    try:
        temp_list = [] # tmp with all cards
        for i in await get_all_cards_from_board():
            temp_list.append(await get_card_info(i['id']))
        res_list = []
        for i in temp_list:
            if i[0] == chain:
                res_list.append(i[1])

        return int(max(res_list, default=0))
    except BaseException as BE:
        lg.warning(f'catch {BE} in chain {chain}')

async def select_prop_for_publ_trello(data_list:list, chain_name, chain_pref):

    start_date = datetime.date(*[int(i) for i in Conf.start_date_monitoring.split('-')]) # date_type
    last_prop_chain = await get_last_id_trello_by_chain(chain_name)
    
    lg.info(f'{len(data_list)} props in {chain_name}')
    if len(data_list):
        for prop_data in data_list:
            if (int(prop_data['proposal_id']) > last_prop_chain) and (parser.parse(prop_data.get('submit_time', '')).date() > start_date):

                await post_card_to_board(prop_data, chain_pref, chain_name)




