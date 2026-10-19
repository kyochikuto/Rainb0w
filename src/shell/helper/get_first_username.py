import os

import toml
from rich import print

"""
This script return the username that was entered during custom installation
to help print their info
"""
users_file_handle = open(
    f"{os.path.expanduser('~')}/Rainb0w_Home/rainb0w_users.toml", "r"
)

rainb0w_users = toml.load(users_file_handle)
rainb0w_user = rainb0w_users["users"][0]

print(rainb0w_user["name"])

users_file_handle.close()
