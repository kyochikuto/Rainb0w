#!/usr/bin/env python3

import os
import sys

import toml
from rich import print

config_file_handle = open(
    f"{os.path.expanduser('~')}/Rainb0w_Home/rainb0w_config.toml", "r"
)
users_file_handle = open(
    f"{os.path.expanduser('~')}/Rainb0w_Home/rainb0w_users.toml", "r"
)

rainb0w_config = toml.load(config_file_handle)
rainb0w_users = toml.load(users_file_handle)
rainb0w_users = rainb0w_users["users"]
main_domain = rainb0w_config["DOMAINS"]["MAIN_DOMAIN"]

if rainb0w_users:
    for user in rainb0w_users:
        if user["name"] == sys.argv[1]:
            print(
                f"""\nGet share urls for '{user['name']}' at:

[bold green]URL:[/bold green] [white]https://{main_domain}/users/{user['date']}_{user['name']}.html[/white]
[bold green]Username:[/bold green] [white]{user['name']}[/white]
[bold green]Password:[/bold green] [white]{user['share_page_password']}[/white]\n

[bold yellow]NOTE: DO NOT SHARE THESE INFORMATION OVER SMS,
USE EMAILS OR OTHER SECURE WAYS OF COMMUNICATION INSTEAD![/bold yellow]""".lstrip()
            )
            break

config_file_handle.close()
users_file_handle.close()
