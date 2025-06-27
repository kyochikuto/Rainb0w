#!/usr/bin/env python3

import os
import shutil
import signal
import sys

from base.config import (
    CERTBOT_CF_SECRET_FILE,
    NGINX_CONFIG_FILE,
    RAINB0W_BACKUP_DIR,
    RAINB0W_CONFIG_FILE,
    RAINB0W_HOME_DIR,
    RAINB0W_USERS_FILE,
    SINGBOX_CONFIG_FILE,
    WARP_CONF_FILE,
)
from proxy.nginx import configure_nginx
from proxy.singbox import (
    gen_cdn_proxy_params,
    gen_hysteria_proxy_params,
    insert_proxy_params,
    insert_tls_cert_path,
    insert_warp_params,
)
from user.user_manager import add_user_to_proxies, create_new_user, prompt_username
from utils.cf_utils import insert_cloudflare_api_key, prompt_cloudflare_api_key
from utils.helper import (
    gen_random_string,
    load_toml,
    print_txt_file,
    progress_indicator,
    prompt_clear_screen,
    save_toml,
)
from utils.url_utils import (
    prompt_cdn_domain,
    prompt_direct_conn_domain,
    prompt_main_domain,
)
from utils.wp_utils import wp_insert_params


def apply_config(username=None):
    rainb0w_config = load_toml(RAINB0W_CONFIG_FILE)
    rainb0w_users = load_toml(RAINB0W_USERS_FILE)

    # Configure Certbot
    insert_cloudflare_api_key(
        CERTBOT_CF_SECRET_FILE, rainb0w_config["CLOUDFLARE"]["API_KEY"]
    )

    # Insert TLS certs path for inbounds that require it
    insert_tls_cert_path(
        rainb0w_config["DOMAINS"]["MAIN_DOMAIN"],
        SINGBOX_CONFIG_FILE,
    )
    # Configure proxies
    insert_proxy_params(rainb0w_config["PROXY"], SINGBOX_CONFIG_FILE)

    # Configure WARP endpoint
    insert_warp_params(SINGBOX_CONFIG_FILE, WARP_CONF_FILE)

    # Configure NGINX
    configure_nginx(rainb0w_config, NGINX_CONFIG_FILE)

    # WordPress
    wp_insert_params(
        rainb0w_config["DOMAINS"]["MAIN_DOMAIN"],
        "My WordPress Blog",
        gen_random_string(12),
        gen_random_string(12),
        f"{RAINB0W_HOME_DIR}/wordpress/wp.env",
        f"{RAINB0W_HOME_DIR}/wordpress/db.env",
    )

    # If this is a new Express/Custom STATUS, we need to create a default user
    # if it's a 'Restore' we will restore the existing users one by one
    if username:
        add_user_to_proxies(
            create_new_user(username),
            RAINB0W_CONFIG_FILE,
            RAINB0W_USERS_FILE,
            SINGBOX_CONFIG_FILE,
        )
    else:
        # Add users from the rainb0w_users.toml into proxies
        for user in rainb0w_users["users"]:
            add_user_to_proxies(
                user,
                RAINB0W_CONFIG_FILE,
                RAINB0W_USERS_FILE,
                SINGBOX_CONFIG_FILE,
            )

    exit(0)


def configure():
    rainb0w_config = load_toml(RAINB0W_CONFIG_FILE)

    if "PROXY" not in rainb0w_config:
        rainb0w_config["PROXY"] = []

    # Display notice
    print_txt_file(f"{os.getcwd()}/notice.txt")
    prompt_clear_screen()

    progress_indicator("Main Domain")
    rainb0w_config["DOMAINS"]["MAIN_DOMAIN"] = prompt_main_domain()

    progress_indicator("Direct Protocols Subdomain")
    rainb0w_config["DOMAINS"]["DIRECT_CONN_DOMAIN"] = prompt_direct_conn_domain()

    progress_indicator("CDN Protocols Subdomain")
    rainb0w_config["DOMAINS"]["CDN_COMPAT_DOMAIN"] = prompt_cdn_domain()

    rainb0w_config["PROXY"] = gen_cdn_proxy_params(
        rainb0w_config["DOMAINS"]["CDN_COMPAT_DOMAIN"],
    )

    rainb0w_config["PROXY"].append(
        gen_hysteria_proxy_params(rainb0w_config["DOMAINS"]["MAIN_DOMAIN"])
    )

    progress_indicator("Cloudflare API Key")
    rainb0w_config["CLOUDFLARE"]["API_KEY"] = prompt_cloudflare_api_key()

    # Save the configuration to file because we're going to pass it around next
    save_toml(rainb0w_config, RAINB0W_CONFIG_FILE)

    # Finally prompt for a username
    progress_indicator("User Management")
    username = prompt_username()

    apply_config(username=username)


def restore_config():
    if os.path.exists(RAINB0W_BACKUP_DIR):
        os.makedirs(RAINB0W_HOME_DIR, exist_ok=True)
        shutil.copyfile(
            f"{RAINB0W_BACKUP_DIR}/{os.path.basename(RAINB0W_CONFIG_FILE)}",
            RAINB0W_CONFIG_FILE,
        )
        shutil.copyfile(
            f"{RAINB0W_BACKUP_DIR}/{os.path.basename(RAINB0W_USERS_FILE)}",
            RAINB0W_USERS_FILE,
        )
        print("Restoring your configuration and users...")
        apply_config()
    else:
        print(f"ERROR: No data found at: {RAINB0W_BACKUP_DIR}")
        print(
            f"Please copy your backup files to \
                    '{RAINB0W_BACKUP_DIR}' and run the installer again!"
        )
        exit(1)


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "Install":
            configure()
        elif sys.argv[1] == "Restore":
            restore_config()
        else:
            print("Unknown installation type passed! Exiting!")
            exit(1)
    else:
        print("Not enough args passed! Exiting!")
        exit(1)


def signal_handler(sig, frame):
    print("\nOkay! Exiting!")
    sys.exit(1)


if __name__ == "__main__":
    # Enable bailing out!
    signal.signal(signal.SIGINT, signal_handler)
    main()
