#!/bin/bash

IP=$(ipconfig getifaddr en0) #mac0S 
echo "VITE_BASE_URL=http://$IP:8000" > frontend/.env
echo "Set VITE_BASE_URL to http://$IP:8000"
cd frontend
npm run dev
