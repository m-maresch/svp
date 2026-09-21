#!/bin/bash

source ./bin/activate

LC_NUMERIC=C python src/svp/main.py $@
