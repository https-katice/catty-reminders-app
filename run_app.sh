#!/bin/bash
set -e

cd /home/katrin/catty-reminders-app || exit 1

SHA=$1
echo "Deploying SHA: $SHA"

git fetch --all
git reset --hard "$SHA"

/home/katrin/catty-reminders-app/.venv/bin/python -m pip install -r requirements.txt

echo "DEPLOY_REF=$SHA" > /home/katrin/catty-reminders-app/.env

sudo systemctl restart catty-reminders

sleep 3
if systemctl is-active --quiet catty-reminders; then
    echo "SUCCESS: Deployed $SHA"
else
    echo "ERROR: catty-reminders service not active"
    exit 1
fi