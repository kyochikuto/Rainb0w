FROM wordpress:latest

RUN apt-get update \
    && apt-get install -y mariadb-client netcat-openbsd \
    && docker-php-ext-install mysqli pdo pdo_mysql \
    && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LO https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
 && chmod +x wp-cli.phar \
 && mv wp-cli.phar /usr/local/bin/wp