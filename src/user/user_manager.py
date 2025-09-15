import os
from datetime import date
from random import randint
from uuid import uuid4

import bcrypt
import qrcode
from rich import print

from base.config import (
    NGINX_HTPASSWD_FILE,
    NGINX_SHARE_PAGE_TEMPLATE_FILE,
    NGINX_USERS_DIR,
)
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
    share_page_password = gen_random_string(randint(4,5))
    uuid = str(uuid4())
    today = date.today()
    formatted_date = today.strftime("%Y%m%d")

    add_or_update_htpasswd(NGINX_HTPASSWD_FILE, username, share_page_password)
    
    user_info = {
        "name": username,
        "password": password,
        "uuid": uuid,
        "hysteria_url": "",
        "vless_ws_url": "",
        "vless_grpc_url": "",
        "share_page_password": share_page_password,
        "date": formatted_date
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
    proxy_config = next(
        (item for item in proxies if item["type"] == "VLESS_WS")
    )
    vless_path = f"{proxy_config['path']}"
    user_info["vless_ws_url"] = (
        f"vless://{user_info['uuid']}@{domains['CDN_COMPAT_DOMAIN']}:443?security=tls&encryption=none&alpn=http/1.1&host={proxy_config['host']}&path={safe_url_encode(vless_path)}&type=ws&fp=randomized&fragment=tlshello%2C100-200%2C1-2&sni={domains['CDN_COMPAT_DOMAIN']}#{user_info['name']}%20[VLESS%20Websocket]"
    )

    # VLESS gRPC
    proxy_config = next(
        (item for item in proxies if item["type"] == "VLESS_GRPC")
    )
    user_info["vless_grpc_url"] = (
        f"vless://{user_info['uuid']}@{domains['CDN_COMPAT_DOMAIN']}:443?mode=gun&security=tls&encryption=none&alpn=h2,http/1.1&type=grpc&serviceName={proxy_config['service_name']}&fp=randomized&sni={domains['CDN_COMPAT_DOMAIN']}#{user_info['name']}%20[VLESS%20gRPC]"
    )

    # Hysteria2
    proxy_config = next((item for item in proxies if item["type"] == "HYSTERIA"))
    user_info["hysteria_url"] = (
        f"hysteria2://{user_info['password']}@{domains['DIRECT_CONN_DOMAIN']}:8443/?obfs=salamander&obfs-password={proxy_config['obfs']}&sni={domains['DIRECT_CONN_DOMAIN']}#{user_info['name']}%20[Hysteria]"
    )

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
            inbound["users"].append(new_client)
        elif inbound["type"] == "hysteria2":
            new_client = {"name": user_info["name"], "password": user_info["password"]}
            inbound["users"].append(new_client)
        else:
            pass

    user_info = add_share_urls(user_info, rainb0w_config_file)
    generate_user_html_page(user_info)
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


def print_client_info(username: str, rainb0w_users_file: str, rainb0w_config_file: str):
    rainb0w_config = load_toml(rainb0w_config_file)
    rainb0w_users = get_users(rainb0w_users_file)
    if rainb0w_users:
        for user in rainb0w_users:
            if user["name"] == username:
                print(
                    f"""\nGet share urls for '{username}' at:

[bold green]URL:[/bold green] [white]https://{rainb0w_config["DOMAINS"]["MAIN_DOMAIN"]}/users/{user['date']}_{user['name']}.html[/white]
[bold green]Username:[/bold green] [white]{user['name']}[/white]
[bold green]Password:[/bold green] [white]{user['share_page_password']}[/white]\n

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

def add_or_update_htpasswd(htpasswd_path, username, password):
    users = {}
    if os.path.exists(htpasswd_path):
        with open(htpasswd_path, 'r') as f:
            for line in f:
                if ':' in line:
                    u, h = line.strip().split(':', 1)
                    users[u] = h

    # Generate bcrypt hash for password
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hashed_str = hashed.decode('utf-8')

    users[username] = hashed_str

    with open(htpasswd_path, 'w') as f:
        for u, h in users.items():
            f.write(f"{u}:{h}\n")


def generate_qr_code(url: str, output_file: str = "qrcode.png",
                     box_size: int = 10, border: int = 4,
                     fill_color: str = "black", back_color: str = "white"):
    """
    Generate a QR code from a URL and save it as a PNG file.

    Args:
        url (str): The URL or data to encode in the QR code.
        output_file (str): Path to save the generated PNG file.
        box_size (int): Size of each box in pixels.
        border (int): Width of the border (boxes).
        fill_color (str): Color of the QR code.
        back_color (str): Background color of the image.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.ERROR_CORRECT_L,
        box_size=box_size,
        border=border,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    img.save(f"{NGINX_USERS_DIR}/img/{output_file}") # pyright: ignore[reportArgumentType]


def generate_user_html_page(user_info: dict):
    os.makedirs(f"{NGINX_USERS_DIR}/img", exist_ok=True)
    hysteria_qrcode_file = f"{user_info['date']}_{user_info['name']}_hysteria_qrcode.png"
    vless_ws_qrcode_file = f"{user_info['date']}_{user_info['name']}_vless_ws_qrcode.png"
    vless_grpc_qrcode_file = f"{user_info['date']}_{user_info['name']}_vless_grpc_qrcode.png"

    generate_qr_code(url=user_info["hysteria_url"], output_file=hysteria_qrcode_file)
    generate_qr_code(url=user_info["vless_grpc_url"], output_file=vless_grpc_qrcode_file)
    generate_qr_code(url=user_info["vless_ws_url"], output_file=vless_ws_qrcode_file)

    with open(NGINX_SHARE_PAGE_TEMPLATE_FILE, "r", encoding="utf-8") as f:
        html_content = f.read()

    html_content = html_content.replace("{USERNAME}", user_info["name"])
    html_content = html_content.replace("{HYSTERIA_SHARE_LINK}", user_info["hysteria_url"])
    html_content = html_content.replace("{HYSTERIA_QRCODE_PATH}", hysteria_qrcode_file)
    html_content = html_content.replace("{VLESS_WS_SHARE_LINK}", user_info["vless_ws_url"])
    html_content = html_content.replace("{VLESS_WS_QRCODE_PATH}", vless_ws_qrcode_file)
    html_content = html_content.replace("{VLESS_GRPC_SHARE_LINK}", user_info["vless_grpc_url"])
    html_content = html_content.replace("{VLESS_GRPC_QRCODE_PATH}", vless_grpc_qrcode_file)

    with open(f"{NGINX_USERS_DIR}/{user_info['date']}_{user_info['name']}.html", "w", encoding="utf-8") as f:
        f.write(html_content)