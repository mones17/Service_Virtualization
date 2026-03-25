from uuid import UUID
from fastapi import Request, Response, FastAPI
from Controllers.ServiceAPIController import *;

app = FastAPI()

@app.get("/sv/service/newrelic/health")
async def HealthCheck():
    return {"status": "health"}

@app.post("/sv/service/addService")
async def AddServiceRequest(request: Request, response: Response):
    return await AddignServiceToUser(request, response)

@app.get("/sv/service/userServices")
async def UserServicesRequets(request: Request, response: Response):
    return await GetUserServices(request, response)

@app.get("/sv/service/hostsByService")
async def GetHostsByServiceRequets(request: Request, response: Response):
    return await GetHostsByService(request, response)

@app.post("/sv/service/deleteService")
async def DeleteServiceRequest(request: Request, response: Response):
    return await DeleteServiceToUser(request, response)

@app.post("/sv/service/deleteAllServices")
async def DeleteAllServicesRequest(request: Request, response: Response):
    return await DeleteAllServicesToUser(request, response)

@app.get("/sv/service/getAllUsers")
async def GetAllUsersRequest(request: Request, response: Response):
    return await GetAllUsers(request, response)

@app.get("/sv/service/getUsersByService")
async def GetUsersServiceRequest(request: Request, response: Response):
    return await GetUsersByService(request, response)

@app.options("/{full_path:path}")
async def OptionsRequest( request: Request, response:Response):
    response.status_code=204