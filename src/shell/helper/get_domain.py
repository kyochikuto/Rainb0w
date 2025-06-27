#!/usr/bin/env python3

import os
import re

import toml
from rich import print

"""
This script returns the domain that was entered during custom installation
to help certbot obtain TLS certs
"""
config_file_handle = open(
    f"{os.path.expanduser('~')}/Rainb0w_Home/rainb0w_config.toml", "r"
)

rainb0w_config = toml.load(config_file_handle)
main_domain = rainb0w_config["DOMAINS"]["MAIN_DOMAIN"]

pattern = r"(.*)\.(.*)\.(.*)"
if re.match(pattern, main_domain):
    main_domain = main_domain[main_domain.index(".") + 1 :]

print(main_domain)

config_file_handle.close()
