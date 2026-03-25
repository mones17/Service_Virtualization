#!/bin/bash
nginx -g "daemon off;" & uvicorn main:app --proxy-headers --host nginx_app --port 8001