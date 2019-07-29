#!/bin/bash

echo_blue () { echo -e "\e[34m$1\e[39m"; }

run () {
    pytest --html=test_report.html \
           --self-contained-html \
           "$@"
}

# move cwd to script directory (should be 'Apolloscope/tests/')
cd "${0%/*}" # (script name minus the last path component '/*')

declare -a parameters  # accumulator array for parameters
coverage=false  # boolean for trunning the coverage analysis
badge_update=false

# check custom parameters, store the rest in the accumulator
while test $# -gt 0
do
    if [[ "$1" == "--coverage" ]]
    then
        coverage=true
    else
        parameters+="$1"
    fi
    shift
done

# run pytest
if [[ $coverage = true ]]
then
    run --cov=apolloscope \
        --cov-report html \
        "${parameters[@]}"
else
    run
fi
