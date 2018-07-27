FROM quay.io/numigi/odoo-public:11.0
MAINTAINER numigi <contact@numigi.com>

USER root

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

USER odoo

COPY date_range_computed_field /mnt/extra-addons/date_range_computed_field

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
