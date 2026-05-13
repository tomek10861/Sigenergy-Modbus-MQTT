#!/bin/sh
set -eu

POLL_INTERVAL_S="${POLL_INTERVAL_S:-15}"

while true; do
  echo "[$(date)] Start odczytu Sigenergy ${SIGENERGY_HOST:-host.docker.internal}:${SIGENERGY_PORT:-502}"
  python3 /app/SigenergyInverterData.py || echo "[$(date)] Odczyt zakończony błędem"
  echo "[$(date)] Czekam ${POLL_INTERVAL_S}s"
  sleep "${POLL_INTERVAL_S}"
done
