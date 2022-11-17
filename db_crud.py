from tinydb import TinyDB, Query
import json

# import os


db = TinyDB("db.json")


def find_chain(table: str, name: str) -> list:

    table = db.table(table)
    return table.search(Query()[name])


def add_chain_monitoring(user, chain: str):

    # db = TinyDB("db.json")
    table = db.table("monitoring")
    #  need to get last prop_id
    # r = get_props_chain(chain)
    # print(get_last_proposals(r))
    if bool(table.search(Query()["user"] == user)) is False:
        table.insert({"chain_list": [chain], "user": user})
    else:
        current_chain_list: list = table.search(Query()["user"] == user)[0].get(
            "chain_list"
        )
        current_chain_list.extend([chain])

        table.update(
            {"chain_list": list(set(current_chain_list))}, Query()["user"] == user
        )


def init_db():

    with open("chains.json", "r") as f:
        chain_data = json.load(f)
    # if os.path.exists("db.json"):
    #     os.remove("db.json")
    # db = TinyDB("db.json")

    # save only addr_prefix
    chain_data = [(i.get("addr_prefix"), i.get("chain_name")) for i in chain_data]

    table = db.table("chains")

    for i in chain_data:
        table.insert({"chain": i[0], "name": i[1]})


async def chain_monitoring_by_user() -> list:
    """return unic chain_list for all users"""
    try:
        # db = TinyDB("db.json")
        table = db.table("monitoring")
        # return table.search(Query()["user"] == user)[0].get("chain_list")
        return list(
            set(sum([i.get("chain_list") for i in table.all()], []))
        )  # flat list out of a list of lists ^)
    except:
        return []


async def get_all_chains() -> list:
    """
    return [str, str...]"""
    chains_table = db.table("chains")

    return list(
        set([i.get("name") for i in chains_table])
        - set(await chain_monitoring_by_user())
    )
