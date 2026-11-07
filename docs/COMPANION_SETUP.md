# Field Scoreboard — Bitfocus Companion setup

No dedicated Companion plugin is required. Field Scoreboard provides a built-in HTTP Builder for **Generic HTTP Requests** in Bitfocus Companion.

## Configure LAN on the Scoreboard computer

1. Launch Field Scoreboard (`http://127.0.0.1:8790`). Open **Output & API → Output & network**.
2. Switch **Enable LAN access** ON, verify the server port, click **Save network settings**, and **exit/restart** the application to apply. Enabling LAN configures the server listener to `0.0.0.0:<port>`; this is a listening address **not** a Companion destination.
3. Check the dropdown of private IPv4 addresses (Ethernet, Wi-Fi, VPN). Use **Refresh** to detect network changes, and select an interface reachable from Companion. The address can be assigned by DHCP or configured statically. If necessary, allow inbound TCP on your trusted *Private* firewall profile. Never forward this HTTP port to the public internet.
4. In **Companion HTTP Builder**, click **Use selected LAN IP**. This fills the actual IP and port, such as `192.168.1.25:8790`. Then click **Load local API token** in the Builder to populate the authorization header. Alternatively, use **Copy API token** below the OBS Browser Source setup. These operations are host-only; the token is never placed in a URL.

## Add a button in Companion

1. **Connections → Add connection → Generic HTTP Requests**. Leave optional Base URL blank because Field Scoreboard generates full URLs.
2. On a button, add a **press action** using Generic HTTP Requests.
3. In Field Scoreboard's Builder select an action, e.g., **Start both clocks** or **Home score +1**.
4. Copy **Method** (`POST`, or `GET` for read-only status) and **URL/URI** into the matching Companion fields.
5. Click **Copy headers** and paste the JSON object into Companion's *Header* field (called *Header input (JSON)* in some versions):

   ```json
   {"Authorization":"Bearer YOUR_PER_INSTALLATION_TOKEN"}
   ```

   The button inserts the real token when loaded locally; the example above is only a placeholder.
6. If the Builder shows a body, choose Content Type `application/json` and paste the **Body (JSON)** exactly. Leave the body empty for Start/Pause/Stop/Reset.
7. Run **Test request** on Field Scoreboard to verify local API behavior (mutation requires confirmation), then press the Companion button to verify network control.

## Actions

The builder supports combined/individual clock Start, Pause, Stop, Reset, clock duration and signed adjustment, home/away scores and fouls, team names, numbered period, OT on/off, optional shot-clock hiding on/off, reset game and GET state. It uses the existing authenticated REST API; no extra software service is needed.

## Troubleshooting

- **ECONNREFUSED:** The Scoreboard has not been restarted after enabling LAN, the selected address is wrong, or the port is blocked. A listening wildcard `0.0.0.0` is never a remote destination.
- **401 Unauthorized:** The Bearer header is missing or the token is wrong. Do not share tokens or screenshots containing them.
- **No live button feedback:** GET state provides a snapshot. This test release does **not** implement a dedicated live Companion module. Use the web interface or OBS overlay for a continuously updating clock.
- **OBS Browser Source on another computer:** This is supported on a trusted private LAN. Enable LAN access, save, restart and use the **OBS on another computer (LAN)** link in the OBS setup section. A remote overlay is **read-only** and does not require a token. It will not work until Field Scoreboard is actively listening on the LAN (not merely saved).
- **Rotate a compromised token:** On the Field Scoreboard host, open Output & API → OBS Browser Source → **Regenerate token**. Confirm the warning. Existing Companion button headers and remote sessions must be updated; their old tokens immediately stop working. No restart is needed. Token rotation is denied to remote clients.
- **Clipboard blocked on tablet:** Browser clipboard APIs may be restricted on non-HTTPS LAN pages; a user-gesture copy fallback is provided. If the browser still rejects copying, select the displayed text manually.

See also [LAN/authentication and backups](USER_GUIDE.md#lan-and-authentication) and the [API boundary reference](ARCHITECTURE.md#http-and-authentication-boundaries). The reset-game action clears scores/fouls/OT and restores period 1; it leaves clocks and the selected period display format unchanged. Period commands remain numeric regardless of Number/Ordinal/Quarter display. For a custom HTTP action, `POST /api/game` with `{"field":"period_format","value":"quarter"}` selects the format (number/ordinal/quarter) without changing the number or OCR ownership; use the same authentication headers.

Companion's field names can vary by version; the [official Generic HTTP Requests guide](https://github.com/bitfocus/companion-module-generic-http/blob/master/companion/HELP.md) documents URL, JSON headers, body and content type.
