# parse jsons
import json
import glob

files = glob.glob("chains/mainnet/*.json")

list_result = []
for file in files:
    with open(file, "r") as f:
        j_data = json.load(f)
        list_result.append(
            {
                "addr_prefix": j_data["addr_prefix"],
                "api": j_data["api"]
                if type(j_data["api"]) == list
                else [j_data["api"]],
                "chain_name": j_data["chain_name"],
            }
        )

with open("chains.json", "w") as f:
    json.dump(list_result, f, ensure_ascii=False, indent=4)
