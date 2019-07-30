FROM quay.io/bgruening/galaxy:19.01

MAINTAINER madduri@anl.gov

ENV GALAXY_CONFIG_BRAND=PDACS \
    GALAXY_LOGGING=full

#RUN apt-get install sqlite3 libsqlite3-dev

WORKDIR /galaxy-central

ADD tool_conf.xml /galaxy-central/tool_conf.xml

RUN rm -rf tools
RUN mkdir -m 777 /galaxy-central/database/jobs_directory
RUN /bin/bash -c "source /galaxy_venv/bin/activate; pip install globus-sdk"

COPY tools /galaxy-central/tools
COPY .dev-tokens.json /galaxy-central/database/jobs_directory/

ENV GALAXY_CONFIG_TOOL_CONFIG_FILE /galaxy-central/tool_conf.xml
# overwrite current welcome page
ADD welcome.html $GALAXY_CONFIG_DIR/web/welcome.html
ADD Slide1.jpg $GALAXY_CONFIG_DIR/web/Slide1.jpg

# Mark folders as imported from the host.
VOLUME ["/export/", "/var/lib/docker"]

