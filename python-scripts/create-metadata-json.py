"""Create a metadata.json file for use in the frontend."""

import json

def get_list_from_txt_file(input_filename):
    with open(input_filename, 'r') as f:
        return [line.strip() for line in f]


if __name__ == "__main__":
    input_classifications = get_list_from_txt_file('input-txt-files/input-classifications.txt')

    with open('generated/all-used-classifications.json', 'r') as f:
        all_used_classifications = json.load(f)

    with open('input-txt-files/output-classifications-with-details.json', 'r') as f:
        output_classifications_with_details = json.load(f)

    metadata = {
        "inputClassifications": input_classifications,
        "allUsedClassifications": all_used_classifications,
        "outputClassificationsWithDetails": output_classifications_with_details
    }

    with open('generated/metadata.json', 'w') as f:
        json.dump(metadata, f, indent=4)
