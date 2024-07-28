FROM elasticsearch:8.12.2

RUN ES_Version=8.12.2 && \
    /usr/share/elasticsearch/bin/elasticsearch-plugin install -b https://github.com/infinilabs/analysis-ik/releases/download/v${ES_Version}/elasticsearch-analysis-ik-${ES_Version}.zip