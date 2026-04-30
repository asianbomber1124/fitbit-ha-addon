#!/usr/bin/with-contenv bashio
# =============================================================================
# Fitbit Fetch Data – Multi-User run.sh
# Reads shared InfluxDB config once, then spawns one fetcher process per user.
# Each user can optionally override the InfluxDB database/bucket.
# =============================================================================

set -e

bashio::log.info "Starting Fitbit Fetch Data (multi-user mode)..."

# ── Shared InfluxDB options ──────────────────────────────────────────────────
INFLUXDB_HOST=$(bashio::config 'influxdb_host')
INFLUXDB_PORT=$(bashio::config 'influxdb_port')
INFLUXDB_VERSION=$(bashio::config 'influxdb_version')
INFLUXDB_USERNAME=$(bashio::config 'influxdb_username')
INFLUXDB_PASSWORD=$(bashio::config 'influxdb_password')
INFLUXDB_DATABASE=$(bashio::config 'influxdb_database')
INFLUXDB_ORG=$(bashio::config 'influxdb_org')
INFLUXDB_TOKEN=$(bashio::config 'influxdb_token')
INFLUXDB_SSL=$(bashio::config 'influxdb_ssl')
AUTO_BACKFILL=$(bashio::config 'auto_backfill')
BACKFILL_DAYS=$(bashio::config 'backfill_days')

export INFLUXDB_HOST INFLUXDB_PORT INFLUXDB_VERSION
export INFLUXDB_USERNAME INFLUXDB_PASSWORD INFLUXDB_DATABASE
export INFLUXDB_ORG INFLUXDB_TOKEN INFLUXDB_SSL
export AUTO_BACKFILL BACKFILL_DAYS

# ── Count users ──────────────────────────────────────────────────────────────
USER_COUNT=$(bashio::config 'users | length')
bashio::log.info "Found ${USER_COUNT} user(s) configured."

if [ "${USER_COUNT}" -eq 0 ]; then
    bashio::log.fatal "No users configured! Add at least one user in the add-on options."
    exit 1
fi

# ── Launch one fetcher process per user ─────────────────────────────────────
PIDS=()

for i in $(seq 0 $((USER_COUNT - 1))); do
    USERNAME=$(bashio::config "users[${i}].username")
    REFRESH_TOKEN=$(bashio::config "users[${i}].refresh_token")
    CLIENT_ID=$(bashio::config "users[${i}].client_id")
    CLIENT_SECRET=$(bashio::config "users[${i}].client_secret")
    DEVICENAME=$(bashio::config "users[${i}].devicename")
    LOCAL_TIMEZONE=$(bashio::config "users[${i}].local_timezone")

    # Per-user database — fall back to shared setting if empty
    USER_DB=$(bashio::config "users[${i}].influxdb_database")
    if [ -z "${USER_DB}" ] || [ "${USER_DB}" = "null" ]; then
        USER_DB="${INFLUXDB_DATABASE}"
    fi

    bashio::log.info "Launching fetcher for user: ${USERNAME} (device: ${DEVICENAME}, database: ${USER_DB})"

    export "FITBIT_USERNAME_${i}=${USERNAME}"
    export "FITBIT_REFRESH_TOKEN_${i}=${REFRESH_TOKEN}"
    export "FITBIT_CLIENT_ID_${i}=${CLIENT_ID}"
    export "FITBIT_CLIENT_SECRET_${i}=${CLIENT_SECRET}"
    export "FITBIT_DEVICENAME_${i}=${DEVICENAME}"
    export "FITBIT_LOCAL_TIMEZONE_${i}=${LOCAL_TIMEZONE}"
    export "FITBIT_INFLUXDB_DATABASE_${i}=${USER_DB}"

    python3 /app/fitbit_fetch_wrapper.py --user-index "${i}" &
    PIDS+=($!)
done

# ── Wait for all background processes ────────────────────────────────────────
bashio::log.info "All user fetchers started. Waiting..."
for pid in "${PIDS[@]}"; do
    wait "${pid}" || bashio::log.warning "A fetcher process (PID ${pid}) exited with an error."
done

bashio::log.info "All fetchers finished."
