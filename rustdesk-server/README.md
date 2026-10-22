# RustDesk Server OSS

This Docker Compose setup runs RustDesk's ID/rendezvous service (`hbbs`) and relay service (`hbbr`) on a Linux host. The `data/` directory stores the server key pair and persists it across container restarts. Keep the private key (`data/id_ed25519`) secret and back it up securely.

## 1. Set the public address

Copy `.env.example` to `.env`. It is prefilled with `codehalter.does-it.net`; change it if your public DNS name changes. A dynamic DNS hostname is recommended for a home connection with a changing public IP.

## 2. Start the services

From this directory, run:

```sh
cp .env.example .env
# Edit .env, then:
sudo docker compose pull
sudo docker compose up -d
sudo docker compose logs -f
```

After startup, get the client verification key with:

```sh
sudo cat data/id_ed25519.pub
```

## 3. Configure network access

On the router, forward these ports to this Linux computer's reserved LAN IP:

| Port | Protocol | Purpose |
|---|---|---|
| 21115 | TCP | NAT test |
| 21116 | TCP and UDP | ID registration, heartbeat, and connection service |
| 21117 | TCP | Relay traffic |

Allow the same inbound ports through the Linux firewall, if enabled. Do not expose ports 21114, 21118, or 21119 for this setup; they are for Pro/web-client features that are not enabled here. If the ISP uses carrier-grade NAT, inbound port forwarding may not work; a public VPS or a VPN/tunnel with inbound connectivity will be needed.

## 4. Configure each RustDesk client

In the client's Network settings, choose **ID/Relay Server** and set:

- **ID Server:** your public DNS name or IP
- **Relay Server:** leave blank (clients can derive it), or use `<address>:21117`
- **Key:** contents of `data/id_ed25519.pub`

Check connectivity from a network outside the server's LAN. LAN testing alone does not confirm router forwarding works.

## Maintenance

Update with `sudo docker compose pull && sudo docker compose up -d`. Back up `data/` securely before updates. Anyone with `id_ed25519` can impersonate this server, so do not share that private key.
