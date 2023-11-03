#!/bin/bash

### Download lists of dimensions and classifications for usual residents.

set -euo pipefail

mkdir -p downloaded

curl -o downloaded/poptypes.json 'https://api.beta.ons.gov.uk/v1/population-types?limit=100'

for poptype in UR UR_HH; do
    curl -o downloaded/dimensions-$poptype.json "https://api.beta.ons.gov.uk/v1/population-types/$poptype/dimensions?limit=200"

    mkdir -p downloaded/classifications-$poptype

    jq '.items[] | .id' downloaded/dimensions-$poptype.json | tr -d '"' | while read dim; do
        echo $dim
        curl -o downloaded/classifications-$poptype/$dim.json "https://api.beta.ons.gov.uk/v1/population-types/$poptype/dimensions/$dim/categorisations"
        sleep 0.8
    done
done
