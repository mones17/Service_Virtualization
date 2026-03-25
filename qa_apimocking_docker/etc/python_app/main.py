from fastapi import Request, Response, FastAPI
from Controllers.GenericAPIController import *
import newrelic.agent

app = FastAPI()

@app.get("/sv/python/newrelic/health")
async def HealthCheck():
    return {"status": "health"}

@app.post("/{full_path:path}")
async def PostRequest( request: Request, response:Response):
    return await ProcessRequest(request, response)

@app.put("/{full_path:path}")
async def PutRequest( request: Request, response:Response):
    return await ProcessRequest(request, response)

@app.patch("/{full_path:path}")
async def PatchRequest( request: Request, response:Response):
    return await ProcessRequest(request, response)

@app.delete("/{full_path:path}")
async def DeleteRequest( request: Request, response:Response):
    return await ProcessRequest(request, response)

@app.get("/{full_path:path}")
async def GetRequest( request: Request, response:Response):
    return await ProcessRequest(request, response)

@app.options("/{full_path:path}")
async def OptionsRequest( request: Request, response:Response):
    return await ProcessRequest(request, response)