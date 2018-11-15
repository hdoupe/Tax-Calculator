import os
import json

current_path = os.path.abspath(os.path.dirname(__file__))
pcl_path = os.path.join(
    current_path, "taxcalc/policy_current_law.json"
)

with open(pcl_path, 'r') as f:
    pcl = json.loads(f.read())

for param, item in pcl.copy().items():
    values = []
    curr = {}
    if isinstance(item["value"][0], list):
        for year in range(len(item["value"])):
            for dim1 in range(len(item["value"][0])):
                values.append({"year": item["start_year"] + year,
                               item["col_var"]: item["col_label"][dim1],
                               "value": item["value"][year][dim1]})
    else:
        for year in range(len(item["value"])):
            values.append({"year": item["start_year"] + year,
                            "value": item["value"][year]})

    pcl[param]['value'] = values

with open(pcl_path, 'w') as f:
    f.write(json.dumps(pcl, indent=4))