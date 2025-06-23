# 🚀 Deployment Guide: AI Engine (FastAPI + GPT-4) on Apache (Ubuntu Server)

This guide walks through setting up and deploying the AI Engine correction API using FastAPI, Uvicorn, and Apache on an Ubuntu server **without a subdomain**, including persistent background service and Apache reverse proxy integration.

---

## ✅ Step 1: Upload or Clone the Project

Navigate to your deployment directory and clone the repo:

```bash
cd /var/www/html
sudo mkdir ai-engine-core
sudo chown -R $USER:$USER ai-engine-core
cd ai-engine-core

# Clone from GitHub
git clone git@github.com:SafarAI-ProjectHub/ai-engine-core.git .
```

---

## ✅ Step 2: Setup Python Environment

```bash
sudo apt update
sudo apt install python3.12-venv -y

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

---

## ✅ Step 3: Add Your OpenAI Key

Create a `.env` file in the root of the project:

```bash
echo "OPEN_AI_KEY=sk-xxxxxxx" > .env
```

---

## ✅ Step 4: Update `main.py` to use Uvicorn correctly

In `api/main.py`, update `FastAPI()` to:

```python
app = FastAPI(root_path="/ai")
```

Also, **remove or comment out** the line:

```python
uvicorn.run(...)
```

---

## ✅ Step 5: Create a systemd Service

Create a background service to run the app persistently:

```bash
cat <<EOF | sudo tee /etc/systemd/system/ai-engine.service > /dev/null
[Unit]
Description=AI Engine FastAPI Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/var/www/html/ai-engine-core
ExecStart=/var/www/html/ai-engine-core/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 9999
Restart=always

[Install]
WantedBy=multi-user.target
EOF
```

Then enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-engine
sudo systemctl start ai-engine
```

---

## ✅ Step 6: Configure Apache as Reverse Proxy

Enable proxy modules:

```bash
sudo a2enmod proxy
sudo a2enmod proxy_http
sudo systemctl restart apache2
```

Create a virtual host:

```bash
cat <<EOF | sudo tee /etc/apache2/sites-available/ai-engine.conf > /dev/null
<VirtualHost *:80>
    ServerName 54.237.228.206

    ProxyPreserveHost On
    ProxyPass /ai/ http://127.0.0.1:9999/
    ProxyPassReverse /ai/ http://127.0.0.1:9999/

    ErrorLog \${APACHE_LOG_DIR}/ai-engine-error.log
    CustomLog \${APACHE_LOG_DIR}/ai-engine-access.log combined
</VirtualHost>
EOF
```

Enable the site and reload Apache:

```bash
sudo a2ensite ai-engine.conf
sudo systemctl reload apache2
```

---

## ✅ Step 7: Verify API and Swagger UI

Open in your browser:

```
http://YOUR_SERVER_IP/ai/
```

You should see:

```json
{ "Hello": "World" }
```

Then visit:

```
http://YOUR_SERVER_IP/ai/docs
```

✅ Swagger UI should now load and allow testing of the `/correction` endpoint.

---

## 🔁 Management Commands

| Command | Description |
|--------|-------------|
| `sudo systemctl restart ai-engine` | Restart the FastAPI app |
| `sudo systemctl status ai-engine`  | View current status |
| `sudo journalctl -u ai-engine -f`  | View real-time logs |

---

## 🧩 Notes

- All routes are available under `/ai/` because of the `root_path="/ai"` setting.
- You can change this to `/` if you plan to reverse proxy to root.
- For production, consider adding HTTPS with Let's Encrypt + Certbot.

---