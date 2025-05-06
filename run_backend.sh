#!/bin/bash

#get local IP addr (MAC only)
IP=$(ipconfig getifaddr en0)
echo "LOCAL_IP=$IP" > backend/.env
echo "[backend] set local ip addr to $IP"
cd backend 
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
