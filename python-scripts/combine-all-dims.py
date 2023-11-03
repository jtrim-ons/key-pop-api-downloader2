"""Create a JSON file with details for all classifications."""

import copy
import glob
import json
import key_pop_api_downloader as pgp

poptypes = ["UR", "UR_HH"]

all_classifications = {}
all_classifications_by_poptype = {poptype: {} for poptype in poptypes}

for poptype in poptypes:
    for filename in glob.glob("downloaded/classifications-{}/*.json".format(poptype)):
        with open(filename, 'r') as f:
            data = json.load(f)
        for item in data["items"]:
            all_classifications_by_poptype[poptype][item["id"]] = copy.deepcopy(item)
            all_classifications[item["id"]] = item

for classification in all_classifications:
    all_classifications[classification]['poptypes'] = [
        p for p in poptypes if classification in all_classifications_by_poptype[p]
    ]

# Check that classifications with the same name for UR and UR_HH agree
for classification in all_classifications_by_poptype["UR"]:
    if classification in all_classifications_by_poptype["UR_HH"]:
        if (
            json.dumps(all_classifications_by_poptype["UR"][classification]) !=
            json.dumps(all_classifications_by_poptype["UR_HH"][classification])
        ):
            raise Exception('UR and UR_HH disagree on ' + classification)

with open('generated/all-classifications-by-poptype.json', 'w') as f:
    json.dump(all_classifications_by_poptype, f)

with open('generated/all-classifications.json', 'w') as f:
    json.dump(all_classifications, f)

input_classifications, output_classifications = pgp.load_input_and_output_classification_codes()
used_classifications = set(input_classifications + output_classifications)

all_used_classifications = {
    key: val
    for key, val in all_classifications.items()
    if key in used_classifications
}

with open('generated/all-used-classifications.json', 'w') as f:
    json.dump(all_used_classifications, f)
