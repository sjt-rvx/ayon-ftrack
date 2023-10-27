#!/usr/bin/env bash

repo_root=$(dirname "$(realpath ${BASH_SOURCE[0]})")
full_version_command="import os;import re;version={};exec(open(os.path.join('$repo_root', 'version.py')).read(), version);print(version['__version__']);"
full_version="$(python <<< ${full_version_command})"
addon_name="ftrack_$full_version"
#if [[ "$1" == "$string2" ]]; then
#    echo "The strings are also equal."
#fi
dev_addon_path=/cache/dev/ayon-addons-dev/$addon_name/ayon_ftrack
dev_addon_common_path=$dev_addon_path/common

if [[ $1 == "common" ]]; then
    echo meld ftrack_common $dev_addon_common_path
else
    meld client/ayon_ftrack $dev_addon_path
fi

