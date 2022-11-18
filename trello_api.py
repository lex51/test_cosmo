from conf import Conf

import requests


url = "https://api.trello.com/1/cards"
headers = {"Accept": "application/json"}


def post_card_to_trello(proposals: list, chain_pref: str, chain_name: str):

    for prop in proposals:

        query = {
            "idList": Conf.trello_board,
            "key": Conf.trello_key,
            "token": Conf.trello_sec,
            "name": f"{chain_name} - {prop.get('proposal_id')}",
            "due": prop.get("voting_end_time"),
            "urlSource": f"ping.pub/{chain_name}/gov/{prop.get('proposal_id')}",
        }

        requests.request("POST", url, headers=headers, params=query)
