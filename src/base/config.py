import os

# Path
TLS_CERTS_DIR = "/etc/letsencrypt/live"
RAINB0W_BACKUP_DIR = f"{os.path.expanduser('~')}/Rainb0w_Backup"
RAINB0W_HOME_DIR = f"{os.path.expanduser('~')}/Rainb0w_Home"
RAINB0W_CONFIG_FILE = f"{RAINB0W_HOME_DIR}/rainb0w_config.toml"
RAINB0W_USERS_FILE = f"{RAINB0W_HOME_DIR}/rainb0w_users.toml"
CADDY_CONFIG_FILE = f"{RAINB0W_HOME_DIR}/caddy/etc/config.json"
CADDY_HTML_DIR = f"{RAINB0W_HOME_DIR}/caddy/html"
SINGBOX_CONFIG_FILE = f"{RAINB0W_HOME_DIR}/sing-box/etc/config.json"
CERTBOT_CF_SECRET_FILE = f"{os.path.expanduser('~')}/.secrets/certbot/cloudflare.ini"
WARP_CONF_FILE = (
    f"{os.path.expanduser('~')}/.cache/warp-plus/primary/wgcf-identity.json"
)
