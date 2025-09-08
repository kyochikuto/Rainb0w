from utils.helper import (
    load_conf,
    save_conf,
)
from utils.url_utils import extract_domain, is_subdomain


def configure_nginx(rainb0w_config: dict, nginx_config_file: str):
    print("Configuring NGINX...")
    nginx_config = load_conf(nginx_config_file)

    main_domain = rainb0w_config["DOMAINS"]["MAIN_DOMAIN"]

    if is_subdomain(main_domain):
        main_domain = extract_domain(main_domain)

    # Insert domains
    nginx_config = nginx_config.replace("MAIN_DOMAIN", main_domain)
    nginx_config = nginx_config.replace(
        "CDN_COMPAT_DOMAIN", rainb0w_config["DOMAINS"]["CDN_COMPAT_DOMAIN"]
    )
    nginx_config = nginx_config.replace(
        "DIRECT_CONN_DOMAIN", rainb0w_config["DOMAINS"]["DIRECT_CONN_DOMAIN"]
    )

    # VLESS Websocket
    proxy_config = next(
        (
            item
            for item in rainb0w_config["PROXY"]
            if item["type"] == "VLESS_WS"
        )
    )
    nginx_config = nginx_config.replace("VLESS_WS_PATH", proxy_config["path"])

    # VLESS gRPC
    proxy_config = next(
        (item for item in rainb0w_config["PROXY"] if item["type"] == "VLESS_GRPC")
    )
    nginx_config = nginx_config.replace("VLESS_GRPC_PATH", proxy_config["path"])

    save_conf(nginx_config, nginx_config_file)
