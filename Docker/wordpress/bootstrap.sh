# wordpress/bootstrap.sh
#!/bin/bash
set -e

echo "⏳ Waiting for MariaDB..."
until wp db check --allow-root --path=/var/www/html; do
    sleep 5
done
echo "✅ MariaDB is ready"

if ! wp core is-installed --allow-root --path=/var/www/html; then
    echo "🚀 Installing WordPress..."
    wp core install \
      --url="${WORDPRESS_URL}" \
      --title="${WORDPRESS_TITLE}" \
      --admin_user="${WORDPRESS_ADMIN_USER}" \
      --admin_password="${WORDPRESS_ADMIN_PASSWORD}" \
      --admin_email="${WORDPRESS_ADMIN_EMAIL}" \
      --skip-email \
      --allow-root \
      --path=/var/www/html

    echo "📦 Installing default plugins..."
    wp plugin install loginizer wordpress-importer --activate --allow-root --path=/var/www/html

    echo "🎉 WordPress installation complete!"
else
    echo "✅ WordPress already installed"
fi
