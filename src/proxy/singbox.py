from random import randint

from base.config import TLS_CERTS_DIR
from utils.helper import gen_random_string, load_json, save_json
from utils.url_utils import extract_domain, is_subdomain


def insert_tls_cert_path(
    main_domain: str,  config_file_path: str
):
    proxy_config = load_json(config_file_path)
    if is_subdomain(main_domain):
        main_domain = extract_domain(main_domain)
        
    # We only need TLS config for Hysteria, TCP inbounds recv cleartext traffic from NGINX reverse proxy
    for inbound in proxy_config["inbounds"]:
        if inbound["tag"] == "HYSTERIA":
            cert_path = f"{TLS_CERTS_DIR}/{main_domain}/fullchain.pem"
            key_path = f"{TLS_CERTS_DIR}/{main_domain}/privkey.pem"
            inbound["tls"]["certificate_path"] = cert_path
            inbound["tls"]["key_path"] = key_path
        else:
            pass

    save_json(proxy_config, config_file_path)


def gen_cdn_proxy_params(cdn_subdomain: str) -> list:
    proxy_params = []

    proxy_params.append(
        {
            "type": "VLESS_HTTPUPGRADE",
            "host": cdn_subdomain,
            "path": f"/{gen_random_string(randint(5, 10))}",
        }
    )

    proxy_params.append(
        {
            "type": "VMESS_WS",
            "host": cdn_subdomain,
            "path": f"/{gen_random_string(randint(5, 10))}",
        }
    )

    return proxy_params


def gen_hysteria_proxy_params(main_domain: str) -> dict:
    hysteria_params = {
        "type": "HYSTERIA",
        "obfs": gen_random_string(randint(8, 12)),
        "masquerade": f"https://{main_domain}",
    }

    return hysteria_params


def insert_proxy_params(proxy_params: list, config_file_path: str):
    print("Configuring Sing-Box...")
    config = load_json(config_file_path)

    for inbound in config["inbounds"]:
        if inbound["tag"] == "VMESS_WS":
            proxy_config = next(
                (item for item in proxy_params if item["type"] == "VMESS_WS")
            )
            inbound["transport"]["path"] = proxy_config["path"]
            inbound["transport"]["headers"]["Host"] = proxy_config["host"]
        elif inbound["tag"] == "VLESS_HTTPUPGRADE":
            proxy_config = next(
                (item for item in proxy_params if item["type"] == "VLESS_HTTPUPGRADE")
            )
            inbound["transport"]["path"] = proxy_config["path"]
            inbound["transport"]["host"] = proxy_config["host"]
        elif inbound["tag"] == "HYSTERIA":
            proxy_config = next(
                (item for item in proxy_params if item["type"] == "HYSTERIA")
            )
            inbound["obfs"]["password"] = proxy_config["obfs"]
            inbound["masquerade"] = proxy_config["masquerade"]
        else:
            pass

    save_json(config, config_file_path)


def change_dns_server(target_tag: str, dns_address: str, config_file_path: str):
    config = load_json(config_file_path)

    for server in config["dns"]["servers"]:
        if server["tag"] == target_tag:
            server["address"] = dns_address

    save_json(config, config_file_path)


def enable_porn_dns_blocking(config_file_path: str):
    print("[bold green]>> Block Porn by DNS")
    change_dns_server("adguard-dns-4", "94.140.14.15", config_file_path)
    change_dns_server("adguard-dns-6", "2a10:50c0::bad1:ff", config_file_path)


def disable_porn_dns_blocking(config_file_path: str):
    print("[bold green]>> Unblock Porn by DNS")
    change_dns_server("adguard-dns-4", "94.140.14.14", config_file_path)
    change_dns_server("adguard-dns-6", "2a10:50c0::ad1:ff", config_file_path)


def insert_warp_params(config_file_path: str, warp_conf_file: str):
    warp_conf = load_json(warp_conf_file)
    proxy_conf = load_json(config_file_path)

    proxy_conf["endpoints"][0]["private_key"] = warp_conf["private_key"]

    save_json(proxy_conf, config_file_path)
