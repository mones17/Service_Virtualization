#!/bin/bash
uvicorn main:app --proxy-headers --host cassandradb --port 8010 &
cassandra -f