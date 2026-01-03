#!/bin/bash
set -e

cd /root/BotTele

echo ">>> Pulling latest code"
git pull origin main

if [ -f requirements.txt ]; then
    echo ">>> Installing Python dependencies"
    pip3 install -r requirements.txt
else
    echo ">>> requirements.txt not found, skipping pip install"
fi

echo ">>> Restarting bot"
systemctl restart BotTele
