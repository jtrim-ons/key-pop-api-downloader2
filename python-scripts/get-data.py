"""Download all national-level data from the API and save to gzipped files."""

import gzip
import os.path
import requests
import sys
import time

import key_pop_api_downloader as pgp

def get_file(compressed_file_path, url, config):
    """Download from the API, gzip and save a single file.

    Parameters
    ----------
    compressed_file_path : str
        The target filename
    url : str
        The URL of the JSON file to download
    config : dict
        A config object
    """
    if config["skip_existing_files"] and os.path.isfile(compressed_file_path):
        print("Skipping existing file {}".format(compressed_file_path))
        return
    print("Downloading {}".format(compressed_file_path))
    for i in range(10):   # Try ten times to download
        try:
            response_bytes = requests.get(url, stream=True).content
            break
        except requests.exceptions.ConnectionError:
            print('Connection error')
            time.sleep((i + 1) * 10)
    with gzip.open(compressed_file_path, 'wb') as f:
        f.write(response_bytes)
    time.sleep(0.5)


def is_household_var(classification_code, all_classifications):
    """Return True if and only if classification_code is for a household variable.

    Parameters
    ----------
    classification_code : string
        The variable's classification code
    all_classifications : dict
        A dictionary of information including population type for each classification code
    """
    expected_result = any(
        classification_code.startswith(prefix)
        for prefix in [
            'hh_', 'accommodation_type', 'number_bedrooms', 'occupancy_rating_bedrooms',
            'number_of_cars', 'heating_type'
        ]
    )
    result = 'UR' not in all_classifications[classification_code]['poptypes']
    if expected_result != result:
        # To be extra-cautious, we test it two ways and make sure they're consistent
        raise Exception('Unexpected is_household_var() result for ' + classification_code)
    return result


def get_files(num_vars, config):
    """Download from the API, gzip and save all the data files with `num_vars` input variables.

    Parameters
    ----------
    num_vars : int
        The number of input variables (that is, variables chosen by the user in the web-app)
    config : dict
        A config object
    """
    input_classification_combinations = pgp.get_input_classification_combinations(
        config["input_classifications"], num_vars
    )
    for cc in input_classification_combinations:
        if num_vars > 0:
            c_str = ",".join(cc)
            url = config["url_pattern"].format("UR", c_str)
            print(url)
            compressed_file_path = 'downloaded/{}var/{}.json.gz'.format(num_vars, c_str.replace(',', '-'))
            get_file(compressed_file_path, url, config)
        for c in config["output_classifications"]:
            if pgp.remove_classification_number(c) in [pgp.remove_classification_number(c_) for c_ in cc]:
                # The API won't give data for two versions of the same variable
                continue
            c_str = ",".join(list(cc) + [c])
            url = config["url_pattern"].format(
                "UR_HH" if is_household_var(c, config["all_classifications"]) else "UR",
                c_str
            )
            print(url)
            compressed_file_path = 'downloaded/{}var/{}.json.gz'.format(num_vars, c_str.replace(',', '-'))
            get_file(compressed_file_path, url, config)


def main():
    input_classifications, output_classifications = pgp.load_input_and_output_classification_codes()
    config = {
        "url_pattern": pgp.get_config("input-txt-files/config.json", "national_url_pattern"),
        "skip_existing_files": '--skip-existing' in sys.argv,
        "input_classifications": input_classifications,
        "output_classifications": output_classifications,
        "all_classifications": pgp.load_all_classifications()
    }
    max_var_selections = pgp.get_config("input-txt-files/config.json", "max_var_selections")

    for num_vars in range(0, max_var_selections + 1):
        get_files(num_vars, config)


if __name__ == "__main__":
    main()
