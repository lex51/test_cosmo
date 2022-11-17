def get_last_proposals(d: dict) -> int:

    try:
        return int(d.get("proposals")[-1].get("proposal_id"))

    except BaseException:
        pass


def get_last_proposals_range(d: dict, start_prop_id) -> list:

    res_list = []

    end_prop_id = get_last_proposals(d)
    for i in range(start_prop_id + 1, end_prop_id + 1):
        for prop in d.get("proposals", []):
            if prop.get("proposal_id") == str(i):
                res_list.append(prop)

    return res_list
