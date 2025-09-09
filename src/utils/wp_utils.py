from dotenv import set_key


def wp_insert_params(
    domain: str,
    blog_name: str,
    db_password: str,
    wp_password: str,
    wp_env_file: str,
    db_env_file: str,
):
    set_key(db_env_file, "MYSQL_PASSWORD", db_password)
    set_key(db_env_file, "MYSQL_ROOT_PASSWORD", db_password)
    set_key(wp_env_file, "WORDPRESS_DB_PASSWORD", db_password)
    set_key(wp_env_file, "WORDPRESS_ADMIN_PASSWORD", wp_password)
    set_key(wp_env_file, "WORDPRESS_ADMIN_EMAIL", f"admin@{domain}")
    set_key(wp_env_file, "WORDPRESS_SITE_URL", f"https://{domain}")
    set_key(wp_env_file, "WORDPRESS_TITLE", blog_name)
