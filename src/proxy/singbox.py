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
        if inbound["tag"] == "VLESS_GRPC":
            proxy_config = next(
                (item for item in proxy_params if item["type"] == "VLESS_GRPC")
            )
            inbound["transport"]["service_name"] = proxy_config["service_name"]
        elif inbound["tag"] == "VLESS_WS":
            proxy_config = next(
                (item for item in proxy_params if item["type"] == "VLESS_WS")
            )
            inbound["transport"]["path"] = proxy_config["path"]
            inbound["transport"]["headers"]["Host"] = proxy_config["host"]
        elif inbound["tag"] == "HYSTERIA":
            proxy_config = next(
                (item for item in proxy_params if item["type"] == "HYSTERIA")
            )
            inbound["obfs"]["password"] = proxy_config["obfs"]
            inbound["masquerade"] = proxy_config["masquerade"]
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
    warp_conf = load_json(warp_conf_file)
    proxy_conf = load_json(config_file_path)

    proxy_conf["endpoints"][0]["private_key"] = warp_conf["private_key"]

    save_json(proxy_conf, config_file_path)
