FROM php:8.2-fpm
ARG DEBIAN_FRONTEND=noninteractive

#Paso Variables
ARG USER_NAME
ARG USER_ID
ARG DOCKERFILE

# Set proxy for build
ENV DOCKERFILE=$DOCKERFILE

# echo de UserName y UID
RUN echo UserName: $USER_NAME
RUN echo UserID: $USER_ID
RUN echo Proxy: $HTTP_PROXY

RUN sed -i -E 's/(CipherString\s*=\s*DEFAULT@SECLEVEL=)2/\11/' /etc/ssl/openssl.cnf

RUN cd $HOME &&\
    curl -sS https://getcomposer.org/installer | php &&\
    chmod +x composer.phar &&\
    mv composer.phar /usr/local/bin/composer

RUN apt-get -y update \
    && apt-get install -y libicu-dev \ 
    && docker-php-ext-configure intl \  
    && docker-php-ext-install intl pdo_mysql

#install some base extensions
RUN apt-get install -y \
    libzip-dev \
    zip \
    && docker-php-ext-install zip

# Create system user to run Composer and Artisan Commands
RUN if [ "$DOCKERFILE" = "local" ]; \
    then useradd -G www-data,root -u $USER_ID -d /home/$USER_NAME $USER_NAME; \
    else echo "no es local"; \
    fi

RUN if [ "$DOCKERFILE" = "local" ]; \
    then mkdir -p /home/$USER_NAME/.composer && chown -R $USER_NAME:$USER_NAME /home/$USER_NAME; \
    else echo "no es local"; \
    fi    

WORKDIR /var/www

RUN if [ "$DOCKERFILE" = "local" ]; \
    then mkdir -p /var/www/vendor ; chown -R $USER_NAME:$USER_NAME /var/www/vendor; \
    else echo "No es local"; \
    fi 

###Muevo php.ini
COPY php.ini /usr/local/etc/php/php.ini
# ###Habilito ImageMagick PDF
# COPY policy.xml /etc/ImageMagick-6/policy.xml

USER $USER_NAME


