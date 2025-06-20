#!/bin/bash

# Genera il file licence.txt a runtime
mkdir -p /root/.ScreamingFrogSEOSpider
echo "eula.accepted=15" > /root/.ScreamingFrogSEOSpider/spider.config
echo "name=${SF_LICENSE_NAME}" > /root/.ScreamingFrogSEOSpider/licence.txt
echo "license=${SF_LICENSE_KEY}" >> /root/.ScreamingFrogSEOSpider/licence.txt

export JAVA_TOOL_OPTIONS="-Xmx1024m"

# Avvia il server
exec uvicorn mcp.main:app --host 0.0.0.0 --port 8080
