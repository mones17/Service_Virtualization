#!/bin/bash  

# Destination directory for snapshots  
SNAPSHOT_DIR="/var/lib/cassandra/data/servicevirtualization" 

# Get the current date in the desired format (e.g., 10-09-2023)  
SNAPSHOT_NAME=$(date +'%d-%m-%Y')  

# Name of the snapshot directory to create  
SNAPSHOT_DIR_NAME="snapshot_$SNAPSHOT_NAME"  

# Get each table and check if the snapshot exists
for keyspace_or_table_name in "$SNAPSHOT_DIR"/*; do
    if [ -d "$keyspace_or_table_name/snapshots/$SNAPSHOT_DIR_NAME" ]; then
        echo "Snapshot: $keyspace_or_table_name/snapshots/$SNAPSHOT_DIR_NAME already exists. Removing it..."
        # Delete existing snapshot  
        rm -rf "$keyspace_or_table_name/snapshots/$SNAPSHOT_DIR_NAME"
        if [ $? -ne 0 ]; then  
            echo "Error removing the existing snapshot."  
            exit 1  
        fi  
    fi  
done

# Create a new snapshot with the specific name  
nodetool snapshot -t "$SNAPSHOT_DIR_NAME" servicevirtualization  

# Check if the snapshot was created successfully  
if [ $? -eq 0 ]; then  
    echo "Snapshot created successfully: $SNAPSHOT_DIR_NAME"  
else  
    echo "Error creating the snapshot."  
    exit 1  
fi