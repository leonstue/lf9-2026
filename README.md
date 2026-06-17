# LF9-Projekt 2026 — Todo-Listen REST-Service

Ein REST-Service zur Verwaltung von To-do-Listen, entstanden im Kurs Lernfeld 9 im Jahr 2026.

Das Frontend ist mit SvelteKit gebaut, das Backend mit Python (Flask). Davor sitzt Traefik als Reverse-Proxy und kümmert sich um HTTPS über Let's Encrypt. Alles läuft in Containern über Docker Compose auf einem DigitalOcean-Droplet. Dazu kommt noch ein kleiner Monitoring-Stack mit Grafana, Prometheus, Loki und Alloy.

---

## Inhaltsverzeichnis

1. [Projektbeschreibung](#projektbeschreibung)
2. [Architektur](#architektur)
3. [Server-Einrichtung](#server-einrichtung)
4. [DNS-Einträge](#dns-einträge)
5. [Anpassung für eigene Domain](#anpassung-für-eigene-domain)
6. [Deployment](#deployment)
7. [Erreichbarkeit](#erreichbarkeit)
8. [Monitoring & Logging](#monitoring--logging)
9. [Firewall-Übersicht](#firewall-übersicht)
10. [License](#license)

---

## Projektbeschreibung

### Beschreibung

Mit dem Service kann man To-do-Listen anlegen, bearbeiten und verwalten — inklusive der Einträge darin.

### Ziel des Projekts

Wir wollten eine eigene REST-API bauen, das Ganze deployen und dabei mit Docker, einem Reverse-Proxy und einem echten Server arbeiten.

### Kontext

Das Projekt ist im Rahmen vom Lernfeld 9 in der Schule entstanden.

---

## Architektur

### Tech-Stack

| Schicht | Technologie |
| --- | --- |
| Frontend | SvelteKit + Vite |
| Backend | Python + Flask |
| Reverse-Proxy | Traefik v2.11 |
| Zertifikate | Let's Encrypt (HTTP-Challenge) |
| Container | Docker + Docker Compose v2 |
| Monitoring | Grafana, Prometheus, Loki, Alloy, node-exporter, blackbox-exporter |
| Hosting | DigitalOcean Droplet (Ubuntu) |
| Firewall | UFW |

### Verzeichnisstruktur

Grober Überblick, wo im Repo was liegt:

```
.
├── src/                    # Python-Backend (Flask)
│   └── list_server.py
├── frontend/
│   ├── Dockerfile          # Dockerfile fürs Frontend
│   └── frontend/           # eigentlicher SvelteKit-Code
│       ├── src/
│       ├── package.json
│       ├── vite.config.js
│       └── README.md       # von SvelteKit selbst angelegt, kann ignoriert werden
├── Dockerfile              # Dockerfile fürs Backend
├── docker-compose.yml      # gesamte Anwendung + Monitoring-Stack
├── openApi.yaml            # OpenAPI-Spezifikation der REST-API
├── acme.json               # wird vor dem ersten Start angelegt (Let's-Encrypt-Zertifikate)
└── .env                    # Grafana-Login, selbst anlegen
```

Die `README.md` in `frontend/frontend/` ist die Standard-README, die `npx sv create` beim Anlegen eines SvelteKit-Projekts mit reinpackt — die hat nichts mit diesem Projekt zu tun und kann ignoriert werden.

### Umgesetzte Punkte

- Statische öffentliche IP-Adresse für den Server
- DNS-Einträge bei name.com (inklusive Wildcard)
- Zwei lokale Benutzer
  - `willi` ohne Admin-Rechte
  - `fernzugriff` mit sudo
- SSH-Zugriff über `fernzugriff`
- UFW als Host-Firewall, nur SSH/HTTP/HTTPS offen
- Deployment über Docker Compose
- HTTPS über Traefik und Let's Encrypt
- Monitoring mit Grafana, Prometheus, Loki und Alloy
- Container starten nach einem Reboot von selbst wieder
- Komplette Einrichtung läuft über die Konsole

---

## Server-Einrichtung

Die folgenden Schritte richten einen frischen Linux-Server bei DigitalOcean ein. Statt `sahgame.de` kann man jede andere Domain (oder einfach die IP-Adresse) nehmen.

### Ausgangspunkt

Nach dem Anlegen des Droplets erstmal per SSH als root drauf:

```bash
ssh root@sahgame.de
```

### System vorbereiten

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install -y git
```

### Benutzer anlegen

Zwei lokale Benutzer anlegen:

```bash
sudo adduser willi
sudo adduser fernzugriff
```

Den `fernzugriff` noch in die sudo-Gruppe packen:

```bash
sudo usermod -aG sudo fernzugriff
```

### SSH-Zugriff einrichten

Passwort für `fernzugriff` setzen:

```bash
sudo passwd fernzugriff
```

Damit der Login per Passwort funktioniert, muss `PasswordAuthentication` an zwei Stellen auf `yes` stehen. Erst in der cloud-init-Konfiguration:

```bash
sudo nano /etc/ssh/sshd_config.d/50-cloud-init.conf
```

Eintrag:

```txt
PasswordAuthentication yes
```

Und in der Haupt-Konfiguration:

```bash
sudo nano /etc/ssh/sshd_config
```

Gleicher Eintrag:

```txt
PasswordAuthentication yes
```

SSH-Konfiguration einmal prüfen:

```bash
sudo sshd -t
```

Wenn keine Fehlermeldung kommt, SSH neu starten:

```bash
sudo systemctl restart ssh
```

Zur Kontrolle:

```bash
sudo sshd -T | grep -i passwordauthentication
```

Da sollte stehen:

```txt
passwordauthentication yes
```

Login von einem anderen Rechner testen:

```bash
ssh fernzugriff@sahgame.de
```

Und prüfen, ob sudo geht:

```bash
sudo whoami
```

Ausgabe:

```txt
root
```

### Firewall einrichten

`ufw` als Host-Firewall einrichten. SSH wird vor dem Aktivieren freigegeben, sonst sperrt man sich aus.

```bash
sudo apt install -y ufw
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

Status prüfen:

```bash
sudo ufw status numbered
```

Damit sind SSH, HTTP und HTTPS offen. Die ganze Port-Liste steht weiter unten im Abschnitt [Firewall-Übersicht](#firewall-übersicht).

### Docker installieren

Docker und Docker Compose v2 installieren:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
```

Im weiteren Verlauf wird immer `docker compose` (mit Leerzeichen) verwendet. Das alte `docker-compose` (mit Bindestrich) kann das `configs`-Feature aus der `docker-compose.yml` nicht.

Status prüfen:

```bash
sudo systemctl status docker
```

Damit Docker beim Booten automatisch startet:

```bash
sudo systemctl enable docker
```

Damit `fernzugriff` Docker ohne `sudo` benutzen kann, kommt der User noch in die Docker-Gruppe:

```bash
sudo usermod -aG docker fernzugriff
```

Danach einmal kurz ab- und wieder anmelden, sonst greift die Gruppe nicht:

```bash
exit
ssh fernzugriff@sahgame.de
```

---

## DNS-Einträge

Bei name.com wurden DNS-Einträge auf die öffentliche IP-Adresse des Droplets gesetzt.

Verwendete Hostnamen:

| Hostname | Wofür |
| --- | --- |
| `sahgame.de` | Frontend |
| `api.sahgame.de` | Backend (REST-API) |
| `traefik.sahgame.de` | Traefik-Dashboard |
| `grafana.sahgame.de` | Grafana |

Konkret gesetzt wurden zwei Einträge:

```txt
sahgame.de
*.sahgame.de
```

Der Wildcard-Eintrag deckt alle Subdomains ab.

---

## Anpassung für eigene Domain

Im Repo steht überall `sahgame.de` als Beispiel-Domain und `leon.stuempeley@gmx.de` als Kontakt-E-Mail für Let's Encrypt. Wenn man das Projekt auf eine eigene Domain umzieht, müssen folgende Stellen angepasst werden:

| Datei | Stelle | Was ändern |
| --- | --- | --- |
| `docker-compose.yml` | `--certificatesresolvers.le.acme.email=…` | Eigene E-Mail für Let's Encrypt |
| `docker-compose.yml` | `traefik.http.routers.*.rule=Host(…)` (4×) | Eigene Hostnamen für Frontend, API, Traefik, Grafana |
| `docker-compose.yml` | `configs.prometheus_config.content` → `targets:` unter Job `uptime` | URLs der Uptime-Checks |
| `frontend/frontend/vite.config.js` | `server.allowedHosts: [...]` | Eigene Hostnamen |
| `frontend/frontend/src/routes/+page.svelte` | `const API = "https://api.sahgame.de";` | URL der eigenen API |
| `frontend/frontend/src/routes/list/[list_id]/+page.svelte` | `const API = "https://api.sahgame.de";` | URL der eigenen API |
| `openApi.yaml` | `info.contact.email` | Eigene Kontakt-E-Mail |

Zum schnellen Checken, ob noch was übrig geblieben ist:

```bash
grep -rn "sahgame.de" --exclude-dir=node_modules --exclude-dir=.git .
grep -rn "leon.stuempeley" --exclude-dir=node_modules --exclude-dir=.git .
```

Nach dem Anpassen sollten beide Befehle nur noch Treffer in dieser README liefern.

---

## Deployment

### Repository klonen

```bash
git clone <REPOSITORY-URL>
cd <REPOSITORY-ORDNER>
```

Falls das Repo schon da ist, einfach aktualisieren:

```bash
git pull
```

### Konfiguration (`.env`)

Grafana-Login wird über Umgebungsvariablen gesetzt. Dafür eine `.env` im Projekt-Ordner anlegen:

```bash
nano .env
```

Inhalt:

```env
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=admin
```

Ohne `.env` (oder bei leeren Variablen) fällt Grafana auf seinen eingebauten Default `admin/admin` zurück. Wir lassen das so für den Schulkontext.

Die `.env` steht in der `.gitignore` und wird nicht eingecheckt.

### Anwendung starten

Vor dem allerersten Start die Datei für die Let's-Encrypt-Zertifikate anlegen:

```bash
touch acme.json
chmod 600 acme.json
```

Container bauen:

```bash
docker compose build
```

Und starten:

```bash
docker compose up -d
```

Die `docker-compose.yml` startet dabei folgende Dienste:

- Traefik als Reverse-Proxy für HTTPS
- das Backend (Todo-Listen-API)
- das Frontend
- den Monitoring-Stack (Grafana, Prometheus, node-exporter, blackbox-exporter, Loki, Alloy)

Status der Container:

```bash
docker compose ps
```

Logs anzeigen:

```bash
docker compose logs
```

Live-Logs:

```bash
docker compose logs -f
```

### Anwendung aktualisieren

```bash
git pull
docker compose build
docker compose up -d
```

Danach nochmal prüfen, ob alle Container laufen:

```bash
docker compose ps
```

### Neustart testen

In der `docker-compose.yml` ist für jeden Container die Restart-Policy gesetzt:

```yaml
restart: unless-stopped
```

Dadurch fahren die Container nach einem Server-Reboot wieder von selbst hoch, solange sie nicht vorher manuell gestoppt wurden.

Reboot auslösen:

```bash
sudo reboot
```

Nach dem Neustart wieder per SSH drauf:

```bash
ssh fernzugriff@sahgame.de
```

Und schauen, ob alles wieder läuft:

```bash
docker compose ps
```

---

## Erreichbarkeit

| Dienst | URL | Login |
| --- | --- | --- |
| Frontend (App) | `https://sahgame.de` | — |
| Backend (REST-API) | `https://api.sahgame.de` | — (CORS) |
| Traefik-Dashboard | `https://traefik.sahgame.de` | Basic Auth: `admin` / `abcd1234` |
| Grafana | `https://grafana.sahgame.de` | `admin` / `admin` |

---

## Monitoring & Logging

Auf dem Server läuft ein kleiner Monitoring-Stack für Servermetriken, Uptime-Checks und Logs.

### Was überwacht wird

- CPU, RAM und Disk vom Server (Host-Metriken)
- Uptime von Frontend und API (HTTPS-Check)
- Docker-Logs aller Container (stdout/stderr)

### Komponenten

| Komponente | Rolle |
| --- | --- |
| Grafana | Dashboard und Oberfläche |
| Prometheus | Speichert die Metriken (15 Tage Retention) |
| node-exporter | Liefert CPU/RAM/Disk-Werte vom Host |
| blackbox-exporter | Macht die HTTPS-Uptime-Checks |
| Loki | Speichert die Logs |
| Alloy | Holt die Docker-Logs ab und schickt sie an Loki |

Die ganzen Konfigurationen stehen inline in der `docker-compose.yml` unter dem Top-Level-Key `configs:`.

### Uptime-Ziele

Als Uptime-Ziele werden die Startseite (`https://sahgame.de`) und der Health-Endpoint des Backends (`https://api.sahgame.de/health`) abgefragt. Das Frontend hat keinen eigenen `/health`-Endpoint, die Startseite liefert ja schon `200 OK`.

### Nicht öffentlich erreichbar

Die folgenden Dienste sind nur im internen Docker-Netzwerk erreichbar und haben keine `ports:`-Freigabe auf dem Host:

- Prometheus
- Loki
- node-exporter
- blackbox-exporter
- Alloy

Nur Grafana ist nach außen sichtbar, und auch das nur über Traefik (HTTPS, Host `grafana.sahgame.de`).

### Daten in Grafana

In Grafana sind die Datasources Prometheus und Loki über das Provisioning schon eingerichtet. Damit gibt es:

- Servermetriken über Prometheus + node-exporter
- Uptime-Status über `probe_success` vom blackbox-exporter
- Container-Logs über Loki, gelabelt nach `container`, `compose_service` und `stream`

---

## Firewall-Übersicht

Auf dem Server ist `ufw` aktiv. Nur die Ports für SSH und Webzugriff sind offen.

### Öffentlich freigegeben

| Port | Protokoll | Zweck |
| --- | --- | --- |
| 22 | TCP | SSH-Zugriff |
| 80 | TCP | HTTP für Traefik und Let's-Encrypt-Challenge, Redirect auf HTTPS |
| 443 | TCP | HTTPS auf Frontend, API, Traefik-Dashboard und Grafana |

### Nicht öffentlich

Die internen Monitoring-Ports sind nicht in der Firewall offen und werden auch nicht aus dem Docker-Netzwerk per `ports:` veröffentlicht:

| Port | Dienst |
| --- | --- |
| 3000 | Grafana (läuft über Traefik) |
| 9090 | Prometheus |
| 3100 | Loki |
| 9100 | node-exporter |
| 9115 | blackbox-exporter |
| 12345 | Alloy |

---

## License

Dieses Projekt steht unter der Apache License 2.0 — siehe [LICENSE](LICENSE).

Copyright 2026 Leon Stümpeley.
