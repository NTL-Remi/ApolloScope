#!/bin/bash

echo_blue () { echo -e "\e[34m$1\e[39m"; }

# move cwd to script directory (should be 'Apolloscope/tests/')
cd "${0%/*}" # (script name minus the last path component '/*')

# run pytest and generate coverage report
pytest --cov=apolloscope \
       --cov-report html \
       "$@"
