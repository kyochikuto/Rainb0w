#!/bin/sh

# Set PHP memory limit for WP-CLI operations
export PHP_MEMORY_LIMIT=${PHP_MEMORY_LIMIT:-512M}

# Wait for WordPress and database to be ready
echo "Waiting for WordPress and database to be ready..."
sleep 10

# Wait for database connection
echo "Testing database connection..."
until wp --allow-root db check --path=/var/www/html; do
    echo "Database not ready, waiting 5 seconds..."
    sleep 5
done

echo "Database is ready!"

# Check if WordPress is already installed
if wp --allow-root core is-installed --path=/var/www/html 2>/dev/null; then
    echo "WordPress is already installed!"
    exit 0
fi

echo "Installing WordPress..."

# Fix permissions before installation
echo "Setting up permissions..."
chown -R www-data:www-data /var/www/html 2>/dev/null || true

# Create wp-config.php if it doesn't exist
if [ ! -f "/var/www/html/wp-config.php" ]; then
    echo "Creating wp-config.php..."
    wp --allow-root config create \
        --dbname=${WORDPRESS_DB_NAME} \
        --dbuser=${WORDPRESS_DB_USER} \
        --dbpass=${WORDPRESS_DB_PASSWORD} \
        --dbhost=${WORDPRESS_DB_HOST}:3306 \
        --path=/var/www/html \
        --force \
        --extra-php <<'EOF'
// Set proper URL handling for reverse proxy
if (isset($_SERVER['HTTP_X_FORWARDED_PROTO']) && $_SERVER['HTTP_X_FORWARDED_PROTO'] === 'https') {
    $_SERVER['HTTPS'] = 'on';
}
EOF
    
    # Ensure wp-config.php is owned by www-data immediately after creation
    chown www-data:www-data /var/www/html/wp-config.php 2>/dev/null || true
    chmod 644 /var/www/html/wp-config.php 2>/dev/null || true
    echo "wp-config.php created and permissions set"
fi

# Install WordPress
wp --allow-root core install \
    --url="${WORDPRESS_SITE_URL:-http://localhost}" \
    --title="${WORDPRESS_TITLE:-My WordPress Site}" \
    --admin_user="${WORDPRESS_ADMIN_USER:-admin}" \
    --admin_password="${WORDPRESS_ADMIN_PASSWORD:-admin123}" \
    --admin_email="${WORDPRESS_ADMIN_EMAIL:-admin@example.com}" \
    --path=/var/www/html \
    --skip-email

# Update site URL if specified
if [ -n "${WORDPRESS_SITE_URL}" ]; then
    echo "Updating site URLs..."
    wp --allow-root option update home "${WORDPRESS_SITE_URL}" --path=/var/www/html
    wp --allow-root option update siteurl "${WORDPRESS_SITE_URL}" --path=/var/www/html
fi

# Create uploads directory with proper permissions
echo "Creating uploads directory..."
wp --allow-root eval 'wp_mkdir_p(wp_upload_dir()["basedir"]);' --path=/var/www/html

# Install and activate plugins if specified
if [ -n "${WORDPRESS_PLUGINS}" ]; then
    echo "Installing WordPress plugins: ${WORDPRESS_PLUGINS}"
    for plugin in ${WORDPRESS_PLUGINS}; do
        echo "Installing plugin: $plugin"
        wp --allow-root plugin install "$plugin" --activate --path=/var/www/html
        if [ $? -eq 0 ]; then
            echo "Successfully installed and activated: $plugin"
        else
            echo "Failed to install: $plugin"
        fi
    done
fi

echo "Fixing final permissions..."
# Set ownership first, then permissions
chown -R www-data:www-data /var/www/html 2>/dev/null || true
find /var/www/html -type f -exec chmod 644 {} \; 2>/dev/null || true
find /var/www/html -type d -exec chmod 755 {} \; 2>/dev/null || true
chmod 644 /var/www/html/wp-config.php || true


echo "WordPress installation completed successfully!"
echo "Admin URL: ${WORDPRESS_SITE_URL:-http://localhost}/wp-admin"
echo "Username: ${WORDPRESS_ADMIN_USER:-admin}"
echo "Password: ${WORDPRESS_ADMIN_PASSWORD:-admin123}"

# Keep container running for potential future wp-cli commands
tail -f /dev/null
