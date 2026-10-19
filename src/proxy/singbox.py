import re
from random import randint
from typing import Optional

from rich import print

from base.config import TLS_CERTS_DIR
from utils.helper import gen_random_string, load_json, load_toml, save_json, save_toml
from utils.url_utils import extract_domain, is_subdomain


def gen_cdn_proxy_params(cdn_subdomain: str) -> list:
    proxy_params = []

    proxy_params.append(
        {
            "type": "VLESS_WS",
            "host": cdn_subdomain,
            "path": f"/{gen_random_string(randint(5, 10))}",
        }
    )

    proxy_params.append(
        {
            "type": "VLESS_GRPC",
            "service_name": gen_random_string(randint(5, 10)),
        }
    )

    return proxy_params


def insert_proxy_params(proxy_params: list, reality_config: dict, config_file_path: str):
    print("Configuring Sing-Box...")
    config = load_json(config_file_path)

    for inbound in config["inbounds"]:
        if inbound["tag"] == "VLESS_GRPC":
            proxy_config = next(
                item for item in proxy_params if item["type"] == "VLESS_GRPC"
            )
            inbound["transport"]["service_name"] = proxy_config["service_name"]
        elif inbound["tag"] == "VLESS_WS":
            proxy_config = next(
                item for item in proxy_params if item["type"] == "VLESS_WS"
            )
            inbound["transport"]["path"] = proxy_config["path"]
            inbound["transport"]["headers"]["Host"] = proxy_config["host"]
        elif inbound["tag"] == "REALITY":
            inbound["listen_port"] = int(reality_config["PORT"])
            inbound["tls"]["server_name"] = reality_config["SNI"]
            inbound["tls"]["reality"]["handshake"]["server"] = reality_config["SNI"]
            inbound["tls"]["reality"]["handshake"]["server_port"] = int(reality_config["PORT"])
            inbound["tls"]["reality"]["private_key"] = reality_config["PRIVATE_KEY"]
            inbound["tls"]["reality"]["short_id"] = reality_config["SHORT_ID"]
        else:
            pass

    save_json(config, config_file_path)


def change_dns_server(dns_tag: str, config_file_path: str):
    config = load_json(config_file_path)
    if "dns" in config:
        dns_config = config["dns"]
        if "final" in dns_config:
            dns_config["final"] = dns_tag

    save_json(config, config_file_path)


def enable_porn_dns_blocking(config_file_path: str):
    print("[bold green]>> Block Porn by DNS")
    change_dns_server("adguard-dns-family", config_file_path)


def disable_porn_dns_blocking(config_file_path: str):
    print("[bold green]>> Unblock Porn by DNS")
    change_dns_server("adguard-dns", config_file_path)


def revert_to_local_dns(config_file_path: str):
    print("[bold green]>> Reverting to local DNS servers")
    change_dns_server("local-dns", config_file_path)


def insert_warp_params(config_file_path: str, warp_conf_file: str):
    print("Configuring WARP endpoint")
    warp_conf = load_json(warp_conf_file)
    proxy_conf = load_json(config_file_path)

    proxy_conf["endpoints"][0]["private_key"] = warp_conf["private_key"]

    save_json(proxy_conf, config_file_path)


def insert_reality_keypair(
    reality_keypair_path: str,
    rainb0w_config_path: str
):
    print("Inserting REALITY x25519 key pair...")
    rainb0w_config = load_toml(rainb0w_config_path)
    try:
        with open(reality_keypair_path, 'r') as f:
            lines = f.read().splitlines()
            if len(lines) < 2:
                raise ValueError("keys.txt must contain at least two lines (private and public keys).")
            private_key = lines[0].strip()
            public_key = lines[1].strip()
            rainb0w_config["REALITY"]["PUBLIC_KEY"] = public_key
            rainb0w_config["REALITY"]["PRIVATE_KEY"] = private_key
            save_toml(rainb0w_config, rainb0w_config_path)
    except FileNotFoundError as e:
        print(f"File error: {e}")

def reset_reality_sni(
    sni: str,
    port: int,
    singbox_config_path: str,
    rainb0w_config_path: str
):
    rainb0w_config = load_toml(rainb0w_config_path)
    proxy_config = load_json(singbox_config_path)

    reality_inbound = next(
        (inb for inb in proxy_config.get("inbounds", []) if inb.get("tag") == "REALITY"),
        None,
    )
    if reality_inbound is None:
        raise ValueError('No inbound with tag "REALITY" found in the configuration.')

    tls = reality_inbound.setdefault("tls", {})
    reality = tls.setdefault("reality", {})
    handshake = reality.setdefault("handshake", {})

    tls["server_name"] = f"{sni}:{port}"
    handshake["server"] = sni
    handshake["port"] = port

    rainb0w_config["REALITY"]["SNI"] = sni
    rainb0w_config["REALITY"]["PORT"] = port

    save_json(proxy_config, singbox_config_path)
    save_toml(rainb0w_config, rainb0w_config_path)


def prompt_reality_destination_server() -> tuple[str | None, int | None]:
    """
    Keep asking the user for a value until it matches
    the ``DOMAIN.TLD:PORT`` pattern.
    """
    while True:
        print(
            "Enter the SNI destination for the REALITY proxy as in `[yellow](SUB.)DOMAIN.TLD[/yellow]:[green]PORT[/green]`"
        )
        user_input = input("SNI destination: ").strip()
        ok, domain, port = validate_domain_port(user_input)

        if ok:
            print(f"✅  Accepted → domain={domain!r}, port={port}")
            return (
                domain,
                port,
            )
        else:
            print(
                "❌  Invalid format.  Expected ``DOMAIN.TLD:PORT`` "
                "with a numeric port between 1‑65535."
            )


def validate_domain_port(value: str) -> tuple[bool, str | None, int | None]:
    """
    Validate that *value* matches the pattern ``DOMAIN.TLD:PORT``.

    Returns a tuple ``(is_valid, domain, port)`` where:
    * ``is_valid`` – ``True`` if the string conforms to the pattern **and**
      the numeric port is in the range 1‑65535.
    * ``domain`` – the extracted domain part when valid, otherwise ``None``.
    * ``port`` – the extracted port as an ``int`` when valid, otherwise ``None``.
    """
    _PATTERN = re.compile(
        r"""
        ^                                   # start of string
        (?P<domain>
            (?:[a-zA-Z0-9]                  # first char of a label
                (?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?   # optional middle chars
            \.)+                            # dot after each label (at least one)
            [a-zA-Z]{2,63}                  # top‑level domain
        )
        :                                   # literal colon
        (?P<port>\d{1,5})                    # 1‑5 digits
        $                                   # end of string
        """,
        re.VERBOSE,
    )
    match = _PATTERN.fullmatch(value.strip())
    if not match:
        return False, None, None

    domain = match.group("domain")
    port = int(match.group("port"))

    # Port numbers must be within the TCP/UDP range
    if not (1 <= port <= 65535):
        return False, None, None

    return True, domain, port
