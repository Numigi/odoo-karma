FROM quay.io/numigi/odoo-public:11.0
MAINTAINER numigi <contact@numigi.com>

USER root

COPY .docker_files/requirements.txt .
RUN pip3 install -r requirements.txt

ENV THIRD_PARTY_ADDONS /mnt/third-party-addons
RUN mkdir -p "${THIRD_PARTY_ADDONS}" && chown -R odoo "${THIRD_PARTY_ADDONS}"
COPY ./gitoo.yml /gitoo.yml
RUN gitoo install-all --conf_file /gitoo.yml --destination "${THIRD_PARTY_ADDONS}"

USER odoo

COPY date_range_field_template /mnt/extra-addons/date_range_field_template
COPY karma /mnt/extra-addons/karma
COPY karma_crm /mnt/extra-addons/karma_crm
COPY karma_grade /mnt/extra-addons/karma_grade
COPY karma_partner /mnt/extra-addons/karma_partner
COPY karma_product /mnt/extra-addons/karma_product
COPY karma_project /mnt/extra-addons/karma_project
COPY karma_required_field /mnt/extra-addons/karma_required_field

COPY .docker_files/main /mnt/extra-addons/main
COPY .docker_files/odoo.conf /etc/odoo
