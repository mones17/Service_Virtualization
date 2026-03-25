from fastapi import Request, Response, FastAPI
from Controllers.ConfigNgnixController import *
from Controllers.NginxAPIController import *

app = FastAPI()

@app.post("/sv/routes/addRoute")
async def AddRouteRequest( request: Request, response:Response):
    return await AddRoute(request, response)

@app.post("/sv/routes/addService")
async def AddServiceRequest( request: Request, response: Response):
    return await AddService(request, response)

@app.post("/sv/routes/editService")
async def EditServiceRequest( request: Request, response: Response):
    return await EditService(request, response)

@app.post("/sv/routes/deleteService")
async def DeleteServiceRequest( request: Request, response: Response):
    return await DeleteService(request, response)

@app.post("/sv/routes/deleteRoute")
async def DeleteRouteRequest( request: Request, response: Response):
    return await DeleteRoute(request, response)

@app.post("/sv/routes/setProxyTrafficAnalyzer")
async def SetProxyTrafficAnalyzerRequest( request: Request, response: Response):
    return await SetProxyTrafficAnalyzer(request, response)

@app.options("/{full_path:path}")
async def OptionsRequest( request: Request, response:Response):
    response.status_code=204