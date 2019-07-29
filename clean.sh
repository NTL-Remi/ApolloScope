#!/bin/bash
# Delete temporary files, such as Python byte code and test outputs.

echo_blue () { echo -e "\e[34m$1\e[39m"; }

remove () {
    echo_blue "removing $1"
    find . -path "$1" \
           -not -path "./.venv/*" \
           | xargs rm -r 2>/dev/null
}

# move cwd to script directory (should be 'Apolloscope/')
cd "${0%/*}" # (script name minus the last path component '/*')

# list of files and folders to be deleted, relative to script
to_remove=(
    "*/.hypothesis"
    "*/.pytest_cache"
    "*/__pycache__"
    "./logs"
    )

# confiramation prompt
for name in "${to_remove[@]}"  # for each name
do
    while true  # until valid answer
    do
        read -p "Delete $name [y/n] ? " REPLY
        case $REPLY in
            [Yy])
                remove "$name"
                break
                ;;
            [Nn]) 
                break
                ;;
        esac
    done
done
