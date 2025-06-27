import base64
import json
import os
import random
import shutil
import string
import time

import bcrypt
import psutil
import requests
import toml
import yaml


def load_conf(conf_file: str):
    with open(conf_file, mode="+r") as f:
        return f.read()
    
def save_conf(data, conf_file: str):
    with open(conf_file, mode="w") as f:
        f.write(data)  

def load_json(json_file: str):
    with open(json_file, mode="+r") as f:
        return json.load(f)


def save_json(data, json_file: str):
    with open(json_file, mode="w") as f:
        json.dump(data, f)


def load_yaml(yaml_file: str):
    with open(yaml_file, mode="+r") as f:
        return yaml.safe_load(f)


def save_yaml(data, yaml_file: str):
    with open(yaml_file, mode="w") as f:
        yaml.safe_dump(data, f, allow_unicode=True, encoding="utf-8")


def load_toml(toml_file: str):
    with open(toml_file, mode="+r") as f:
        return toml.load(f)


def save_toml(data, toml_file: str):
    with open(toml_file, mode="w") as f:
        toml.dump(data, f)


def is_string_in_file(file_path: str, string_to_search: str):
    with open(file_path, "r") as f:
        file_content = f.read()
        if string_to_search in file_content:
            return True
        else:
            return False


def get_public_ip():
    response = requests.get("https://api.ipify.org")
    return response.text.strip()


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def prompt_clear_screen():
    input("Press 'Enter' to continue...")
    clear_screen()


def progress_indicator(step_title: str):
    clear_screen()
    width = shutil.get_terminal_size().columns
    print(f"{'#' * 32}".center(width))
    print(f"{step_title}".center(width))
    print(f"{'#' * 32}".center(width))
    print()


def print_typewriter(text: str):
    for char in text:
        print(char, end="", flush=True)
        time.sleep(random.uniform(0.05, 0.15))


def print_txt_file(txt_file: str):
    with open(txt_file, "r") as file:
        text = file.read()
        print(text)


def gen_random_string(length: int):
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


def gen_bcrypt_password(password: str):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password


def base64_encode(data):
    return base64.b64encode(str(data).encode("utf-8"))


def bytes_to_raw_str(bytes_obj: bytes):
    """
    Byte objects are wrapped in b'' when printed in Python, this func
    strips them and returns a raw str representation
    """
    string = ""
    for byte in bytes_obj:
        string += chr(byte)
    return string


def bytes_to_url_safe_base64(data):
    return base64.b64encode(data).decode("utf-8").replace("+", "-").replace("/", "_")


def bytes_to_hex(byte_arr):
    hex_list = []
    for byte in byte_arr:
        current = byte if byte >= 0 else byte + 256
        hex_list.append(format(current >> 4, "x"))
        hex_list.append(format(current & 0xF, "x"))
    return "".join(hex_list)


def get_mem_size():
    return int(psutil.virtual_memory().total / (1024**2))


def copy_dir(src_path, dest_path):
    src_dirname = os.path.basename(src_path)
    if not os.path.exists(dest_path):
        os.makedirs(dest_path)
    dest_dirpath = os.path.join(dest_path, src_dirname)
    shutil.copytree(src_path, dest_dirpath, dirs_exist_ok=True)


def copy_file(src_path, dest_path):
    shutil.copy(src_path, dest_path)


def remove_dir(path):
    shutil.rmtree(path)
