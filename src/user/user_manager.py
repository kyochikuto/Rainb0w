import os
from datetime import date
from random import randint
from uuid import uuid4

import bcrypt
import qrcode
from rich import print

from base.config import PUBLIC_IP
from utils.helper import (
    gen_random_string,
    load_json,
    load_toml,
    save_json,
    save_toml,
)
from utils.url_utils import safe_url_encode


def get_users(rainb0w_users_file: str) -> list:
    rainb0w_users = load_toml(rainb0w_users_file)
    if "users" in rainb0w_users:
        return rainb0w_users["users"]
    else:
        rainb0w_users["users"] = []
        return rainb0w_users["users"]


def save_users(users: list, users_toml_file: str):
    """
    This is just a wrapper function to be consistent with 'get_users'
    """
    save_toml({"users": users}, users_toml_file)


def create_new_user(username: str):
    password = gen_random_string(randint(8, 12))
    uuid = str(uuid4())

    user_info = {
        "name": username,
        "password": password,
        "uuid": uuid,
        "vless_ws_url": "",
        "vless_grpc_url": "",
        "vless_reality_url": "",
    }
    return user_info


def add_share_urls(
    user_info: dict,
    rainb0w_config_file: str,
) -> dict:
    rainb0w_config = load_toml(rainb0w_config_file)
    domains = rainb0w_config["DOMAINS"]
    proxies = rainb0w_config["PROXY"]

    # VLESS Websocket
    proxy_config = next(item for item in proxies if item["type"] == "VLESS_WS")
    vless_path = f"{proxy_config['path']}"
    user_info["vless_ws_url"] = (
        f"vless://{user_info['uuid']}@{domains['CDN_COMPAT_DOMAIN']}:443?security=tls&encryption=none&alpn=http/1.1&host={proxy_config['host']}&path={safe_url_encode(vless_path)}&type=ws&fp=firefox&sni={domains['CDN_COMPAT_DOMAIN']}#{user_info['name']}%20[VLESS%20Websocket]"
    )

    # VLESS gRPC
    proxy_config = next(item for item in proxies if item["type"] == "VLESS_GRPC")
    user_info["vless_grpc_url"] = (
        f"vless://{user_info['uuid']}@{domains['CDN_COMPAT_DOMAIN']}:443?mode=gun&security=tls&encryption=none&alpn=h2,http/1.1&type=grpc&serviceName={proxy_config['service_name']}&fp=firefox&sni={domains['CDN_COMPAT_DOMAIN']}#{user_info['name']}%20[VLESS%20gRPC]"
    )

    # VLESS REALITY
    proxy_config = rainb0w_config["REALITY"]
    user_info["vless_reality_url"] = f"vless://{user_info['uuid']}@{PUBLIC_IP}:{proxy_config['PORT']}?security=reality&encryption=none&pbk={proxy_config['PUBLIC_KEY']}&headerType=none&fp=chrome&spx=%2F&type=tcp&flow=xtls-rprx-vision&sni={proxy_config['SNI']}&sid={proxy_config['SHORT_ID']}#{user_info['name']}%20[REALITY]".strip()

    return user_info


def add_user_to_proxies(
    user_info: dict,
    rainb0w_config_file: str,
    rainb0w_users_file: str,
    singbox_config_file: str,
):
    print(f"Adding '{user_info['name']}' as a new user...")
    config = load_json(singbox_config_file)

    for inbound in config["inbounds"]:
        if inbound["type"] in ["vless", "vmess"]:
            new_client = {"name": user_info["name"], "uuid": user_info["uuid"]}
            if inbound["tag"] == "REALITY":
                new_client["flow"] = "xtls-rprx-vision"

            inbound["users"].append(new_client)
        else:
            pass

    user_info = add_share_urls(user_info, rainb0w_config_file)
    rainb0w_users = get_users(rainb0w_users_file)
    rainb0w_users.append(user_info)
    save_users(rainb0w_users, rainb0w_users_file)
    save_json(config, singbox_config_file)


def remove_user(
    username: str,
    rainb0w_users_file: str,
    singbox_config_file: str,
):
    rainb0w_users = get_users(rainb0w_users_file)
    singbox_config = load_json(singbox_config_file)
    if rainb0w_users:
        for user in rainb0w_users:
            if user["name"] == username:
                print(f"Removing the user '{username}'...")
                for inbound in singbox_config["inbounds"]:
                    if "users" in inbound:
                        for user in inbound["users"]:
                            if user["name"] == username:
                                inbound["users"].remove(user)

        rainb0w_users = [user for user in rainb0w_users if user["name"] != username]

        save_json(singbox_config, singbox_config_file)
        save_users(rainb0w_users, rainb0w_users_file)


def print_client_info(username: str, rainb0w_users_file: str):
    rainb0w_users = get_users(rainb0w_users_file)
    if rainb0w_users:
        for user in rainb0w_users:
            if user["name"] == username:
                print(
                    f"""\nShare urls for '{username}':

[bold green]VLESS (Websocket):[/bold green] [white]{user["vless_ws_url"]}[/white]\n
[bold green]VLESS (gRPC):[/bold green] [white]{user["vless_grpc_url"]}[/white]\n
[bold green]VLESS (REALITY):[/bold green] [white]{user["vless_reality_url"]}[/white]\n

[bold yellow]NOTE: DO NOT SHARE THESE INFORMATION OVER SMS,
USE EMAILS OR OTHER SECURE WAYS OF COMMUNICATION INSTEAD![/bold yellow]""".lstrip()
                )
                break


def prompt_username():
    username = input("\nEnter a username for your first user: ")
    while not username or not username.isascii() or not username.islower():
        print(
            "\nInvalid username! Enter only ASCII characters and numbers in lowercase."
        )
        username = input("Enter a username for your first user: ")

    return username
