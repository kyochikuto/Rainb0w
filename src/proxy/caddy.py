from utils.helper import (
    load_json,
    save_json,
)
from utils.url_utils import extract_domain, is_domain, is_subdomain


def configure_caddy(rainb0w_config: dict, caddy_config_file: str):
    print("Configuring Caddy...")
    caddy_config = load_json(caddy_config_file)

    # Configure TLS reverse proxy
    caddy_config["apps"]["layer4"]["servers"]["tls_proxy"]["routes"][0]["match"][0][
        "tls"
    ]["sni"] = [rainb0w_config["DOMAINS"]["CDN_COMPAT_DOMAIN"]]

    # Configure HTTPS web server and reverse proxy
    caddy_config["apps"]["http"]["servers"]["web-secure"]["routes"][0]["match"][0][
        "host"
    ] = [rainb0w_config["DOMAINS"]["MAIN_DOMAIN"]]
    caddy_config["apps"]["http"]["servers"]["fallback"]["routes"][0]["match"][0][
        "host"
    ] = [rainb0w_config["DOMAINS"]["CDN_COMPAT_DOMAIN"]]

    # Configure SNI and TLS
    if is_domain(rainb0w_config["DOMAINS"]["MAIN_DOMAIN"]):
        caddy_config["apps"]["http"]["servers"]["web-secure"][
            "tls_connection_policies"
        ][0]["match"]["sni"] = [
            rainb0w_config["DOMAINS"]["MAIN_DOMAIN"],
            f"*.{rainb0w_config['DOMAINS']['MAIN_DOMAIN']}",
        ]
        caddy_config["apps"]["tls"]["certificates"]["load_files"][0]["certificate"] = (
            f"/etc/letsencrypt/live/{rainb0w_config['DOMAINS']['MAIN_DOMAIN']}/cert.pem"
        )
        caddy_config["apps"]["tls"]["certificates"]["load_files"][0]["key"] = (
            f"/etc/letsencrypt/live/{rainb0w_config['DOMAINS']['MAIN_DOMAIN']}/privkey.pem"
        )
    elif is_subdomain(rainb0w_config["DOMAINS"]["MAIN_DOMAIN"]):
        main_domain = extract_domain(rainb0w_config["DOMAINS"]["MAIN_DOMAIN"])
        caddy_config["apps"]["http"]["servers"]["web-secure"][
            "tls_connection_policies"
        ][0]["match"]["sni"] = [f"*.{main_domain}"]
        caddy_config["apps"]["tls"]["certificates"]["load_files"][0]["certificate"] = (
            f"/etc/letsencrypt/live/{main_domain}/cert.pem"
        )
        caddy_config["apps"]["tls"]["certificates"]["load_files"][0]["key"] = (
            f"/etc/letsencrypt/live/{main_domain}/privkey.pem"
        )

    # VLESS WS
    proxy_config = next(
        (item for item in rainb0w_config["PROXY"] if item["type"] == "VLESS_WS")
    )
    caddy_config["apps"]["http"]["servers"]["fallback"]["routes"][0]["handle"][0][
        "routes"
    ][0]["match"][0]["path"] = [proxy_config["path"]]

    # VLESS gRPC
    proxy_config = next(
        (item for item in rainb0w_config["PROXY"] if item["type"] == "VLESS_GRPC")
    )
    caddy_config["apps"]["http"]["servers"]["fallback"]["routes"][0]["handle"][0][
        "routes"
    ][1]["match"][0]["path"] = [f"/{proxy_config['service_name']}/*"]

    save_json(caddy_config, caddy_config_file)
