import os
import shutil
import datetime
import subprocess
from fastapi import Request, Response, FastAPI

CASSANDRA_DATA_DIR = "/var/lib/cassandra/data/servicevirtualization"
BACKUP_DIR = "/var/lib/backups"

async def CreateBackup( request, response):
    command = "./create-backup.sh"
    message = ''
    try:
        output = subprocess.check_output(command, shell=True, text=True, stderr=subprocess.STDOUT)
        print("OUTPUT OF SCRIPT EXECUTION: ", output)
        response.status_code = 200
        message = 'Snapshot created successfully'
    except subprocess.CalledProcessError as e:
        print(e.output)
        response.status_code = 500
        message = 'Error creating snapshot'
    except Exception as e:
        print(str(e))
        response.status_code = 500
        message = 'Error creating snapshot'
    return message

async def DoRestore( request, response):
    body = await request.json()
    message = ''
    if 'reference_date' in body:
        body_date = body['reference_date']
        reference_date = datetime.datetime.strptime(body_date, "%d/%m/%Y")
        data_cleaned = clear_cassandra_data()
        if data_cleaned:
            do_restore = restore_nearest_backup(CASSANDRA_DATA_DIR, reference_date)
            if do_restore:
                response.status_code = 200
                message = 'Data restored successfully'
            else:
                response.status_code = 500
                message = 'Error creating restore'
        else:
            response.status_code = 500
            message = 'Error clearing data'
        return message
    else:
        response.status_code = 400
        message = 'Please provide reference_date'
    return message

def find_nearest_backup(backup_dir, reference_date):
    backups = os.listdir(backup_dir)
    nearest_backup = None
    min_difference = None
    for backup in backups:
        try:
            backup_date = datetime.datetime.strptime(backup, 'snapshot_%d-%m-%Y')
            difference = abs(backup_date - reference_date)
            if nearest_backup is None or difference < min_difference:
                nearest_backup = backup
                min_difference = difference
        except ValueError:
            continue
    return nearest_backup

def clear_cassandra_data():  
    for root, dirs, files in os.walk(CASSANDRA_DATA_DIR):  
        for dir in dirs:  
            # Obtiene la ruta completa del directorio de la tabla.  
            dir_path = os.path.join(root, dir)  
            # Verifica que no sea el directorio 'snapshots' ni sus subdirectorios que comienzan con 'snapshot_'.  
            if dir != 'snapshots' and not dir.startswith('snapshot_'):  
                try:  
                    # Elimina solo los archivos dentro del directorio de la tabla.  
                    for file in os.listdir(dir_path):  
                        file_path = os.path.join(dir_path, file)  
                        if os.path.isfile(file_path):  
                            os.remove(file_path)  
                    # Elimina los subdirectorios, excepto los de snapshots.  
                    for subdir in os.listdir(dir_path):  
                        subdir_path = os.path.join(dir_path, subdir)  
                        if os.path.isdir(subdir_path) and subdir != 'snapshots' and not subdir.startswith('snapshot_'):  
                            shutil.rmtree(subdir_path)  
                except Exception as e:  
                    print(f"Error al limpiar {dir_path}: {e}")  
                    return False  
  
    return True

def restore_nearest_backup(cassandra_data_dir, reference_date):
    # Get the list of keyspaces or tables in the backup.
    for keyspace_or_table_name in os.listdir(cassandra_data_dir):
        print("ITERATION")
        print("KEYSPACE OR TABLE NAME: ", keyspace_or_table_name)
        backup_dir = os.path.join(cassandra_data_dir, keyspace_or_table_name, 'snapshots')
        print("BACKUP DIR: ", backup_dir)
        # find and return the nearest backup to the reference date like 'snapshot_dd-mm-YYYY'
        nearest_backup = find_nearest_backup(backup_dir, reference_date)
        print("NEAREST BACKUP: ", nearest_backup)
        if nearest_backup is not None:              
            # Get the full path of the keyspace or table directory, per table.
            keyspace_or_table_dir = os.path.join(backup_dir, nearest_backup)
            # Get the destination directory path for the keyspace or table.
            destination_dir = os.path.join(cassandra_data_dir, keyspace_or_table_name)
            try:
                # Extraer el nombre de la tabla
                table_name = keyspace_or_table_name.split('-')[0]
                compact_command = f"nodetool compact servicevirtualization {table_name}"
                subprocess.run(compact_command, shell=True, check=True)
                shutil.copytree(keyspace_or_table_dir, destination_dir, dirs_exist_ok=True)
                print("TABLE NAME: ", table_name)
                import_command = f"nodetool import servicevirtualization {table_name} {keyspace_or_table_dir}"
                subprocess.run(import_command, shell=True, check=True)
                print(f"Restaurado {table_name} desde {keyspace_or_table_dir}")
            except Exception as e:
                print(f"Error al restaurar {keyspace_or_table_name}: {e}")  
                continue
    try:
        cleanup_command = f"nodetool cleanup servicevirtualization"
        subprocess.run(cleanup_command, shell=True, check=True)
    except Exception as e:
        print("Error al limpiar:", e)
    return True