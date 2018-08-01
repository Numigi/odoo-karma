FROM quay.io/numigi/odoo-public:11.0
MAINTAINER numigi <contact@numigi.com>

USER root

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

COPY ./gitoo.yml /
RUN gitoo install_all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}" && rm /gitoo.yml

USER odoo

COPY date_range_field_template /mnt/extra-addons/date_range_field_template
COPY karma /mnt/extra-addons/karma

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
