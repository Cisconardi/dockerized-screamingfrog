#!/bin/bash

set -e

PERSISTED="/persisted_machineid/machineid"
DEST="/root/.ScreamingFrogSEOSpider/machineid/machineid"

mkdir -p "$(dirname "$DEST")"

# Se non esiste, lo creo e lo persisto
if [ ! -f "$PERSISTED" ]; then
  echo ">> Nessun machineid trovato, ne creo uno"
  uuidgen > "$PERSISTED"
  chmod 600 "$PERSISTED"
fi

# Copio nel path richiesto da SF
cp "$PERSISTED" "$DEST"

echo ">> Machine ID pronto: $(cat "$DEST")"

export _JAVA_OPTIONS="-Xmx1024m"
umask 000

mkdir -p /root/.ScreamingFrogSEOSpider /output /crawls
chmod -R 777 /root/.ScreamingFrogSEOSpider /output /crawls

# Scrivi licenza valida in due righe
echo "${SF_LICENSE_NAME}" > /root/.ScreamingFrogSEOSpider/licence.txt
echo "${SF_LICENSE_KEY}" >> /root/.ScreamingFrogSEOSpider/licence.txt

# Accetta EULA
echo "eula.accepted=15" > /root/.ScreamingFrogSEOSpider/spider.config

# Avvia FastAPI MCP
exec uvicorn mcp.main:app --host 0.0.0.0 --port 8080
