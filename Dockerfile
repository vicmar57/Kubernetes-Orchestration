FROM php:5-apache
ADD h2.php /var/www/html/h2.php
RUN chmod a+rx h2.php


