# Multi-User Changes — fitbit-ha-addon Fork

## What changed

| File | Change |
|------|--------|
| `config.yaml` | Replaced flat single-user fields with a `users` list + shared InfluxDB block |
| `run.sh` | Loops over every entry in `users`, exports indexed env vars, spawns one Python process per user |
| `fitbit_fetch_wrapper.py` | New shim: reads indexed env vars → sets canonical names → calls original `fitbit_fetch.main()` |

## How it looks in the HA UI

The **Configuration** tab will show:

- Shared InfluxDB settings (host, port, token, etc.) — entered once
- A **`users` list** where you can click **+ Add** to add as many Fitbit accounts as you like

Each user entry has:
- `username` — friendly label (used as an InfluxDB tag so data stays separate)
- `refresh_token`
- `client_id`
- `client_secret`
- `devicename`
- `local_timezone`

## Migration from single-user setup

Old config field → New location:

```
refresh_token   →  users[0].refresh_token
client_id       →  users[0].client_id
client_secret   →  users[0].client_secret
devicename      →  users[0].devicename
local_timezone  →  users[0].local_timezone
```

The InfluxDB fields remain at the top level (unchanged names).

## Adding a second user

1. Open **Settings → Add-ons → Fitbit Fetch Data → Configuration**
2. Scroll to the **users** section
3. Click **+ Add user**
4. Fill in the new person's Fitbit credentials
5. Click **Save** and **Restart** the add-on

Each user's data is tagged with their `username` value in InfluxDB,
so Grafana / HA dashboards can filter per person.

## One Fitbit Developer App per user

Each user must have their own app registered at https://dev.fitbit.com
with **OAuth 2.0 Application Type = Personal** (required for intraday data).
They each generate their own refresh token via the Fitbit OAuth 2.0 Tutorial.
