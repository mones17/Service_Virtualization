from fastapi import Request, Response, FastAPI
from Controllers.CassandraController import *

app = FastAPI()

@app.post("/sv/database/backup")
async def BackupRequest( request: Request, response:Response):
    return await CreateBackup(request, response)

@app.post("/sv/database/restore")
async def RestoreRequest( request: Request, response: Response):
    return await DoRestore(request, response)

@app.options("/{full_path:path}")
async def OptionsRequest( request: Request, response:Response):
    response.status_code=204