#!/bin/bash

# Install system dependencies
sudo apt update
sudo apt install -y docker.io redis-server python3-pip python3-venv nginx

# Configure Docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

# Create project directory
mkdir -p ~/WebUI/user_data
chmod -R 777 ~/WebUI/user_data

# Python environment
python3 -m venv ~/WebUI/.venv
source ~/WebUI/.venv/bin/activate
pip install -r ~/WebUI/requirements.txt

# Nginx configuration
sudo bash -c 'cat > /etc/nginx/sites-available/webui <<EOF
server {
    listen 80;
    server_name _;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
    }
    
    location /user-files/ {
        alias /home/$USER/WebUI/user_data/;
    }
}
EOF'

sudo ln -s /etc/nginx/sites-available/webui /etc/nginx/sites-enabled
sudo systemctl restart nginx

# Systemd service
sudo bash -c 'cat > /etc/systemd/system/webui.service <<EOF
[Unit]
Description=WebUI Application
After=network.target

[Service]
User=$USER
WorkingDirectory=/home/$USER/WebUI
Environment="PATH=/home/$USER/WebUI/.venv/bin"
ExecStart=/home/$USER/WebUI/.venv/bin/daphne -b 0.0.0.0 -p 8080 WebUI.asgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF'

sudo systemctl daemon-reload
sudo systemctl enable webui
sudo systemctl start webui