from fastapi import Request, Response, FastAPI
from Controllers.AdminAPIController import *

app = FastAPI()

@app.get("/sv/admin/newrelic/health")
async def HealthCheck():
    return {"status": "health"}

@app.get("/sv/admin/getResponses")
async def GetResponsesRequest( request: Request, response:Response):
    return await GetResponses(request, response)

@app.post("/sv/admin/acceptResponse")
async def AcceptResponseRequest( request: Request, response:Response):
    return await AcceptResponse(request, response)

@app.post("/sv/admin/rejectResponse")
async def RejectResponseRequest( request: Request, response:Response):
    return await RejectResponse(request, response)

@app.post("/sv/admin/addRoute")
async def AddRouteRequest( request: Request, response: Response):
    return await AddRoute(request, response)

@app.post("/sv/admin/addService")
async def AddServiceRequest( request: Request, response: Response):
    return await AddService(request, response)

@app.put("/sv/admin/editService")
async def EditServiceRequest( request: Request, response: Response):
    return await EditService(request, response)

@app.put("/sv/admin/editResource")
async def EditRouteRequest( request: Request, response: Response):
    return await EditRoute(request, response)

@app.delete("/sv/admin/deleteResource")
async def DeleteRouteRequest( request: Request, response: Response):
    return await DeleteRoute(request, response)

@app.delete("/sv/admin/deleteService")
async def DeleteServiceRequest( request: Request, response: Response):
    return await DeleteService(request, response)

@app.post("/sv/admin/changeAPIMode")
async def ChangeAPIModeRequest( request: Request, response:Response):
    return await ChangeAPIMode(request, response)

@app.post("/sv/admin/deleteResponse/{responseID}")
async def DeleteResponseRequest( request: Request, response:Response, responseID):
    return await DeleteResponseByID(request, response, responseID)

@app.get("/sv/admin/getRequests")
async def GetRequestRequest( request: Request, response: Response):
    return await GetRequests(request, response)

@app.post("/sv/admin/responses/addComment/{responseID}")
async def AddCommentRequest( request: Request, response: Response, responseID):
    return await AddComment(request, response, responseID)

@app.get("/sv/admin/products/getProductsList")
async def GetProductsListRequest( request: Request, response: Response):
    return await GetProductsList(request, response)

@app.post("/sv/admin/addResponse")
async def AddResponseRequest( request: Request, response: Response):
    return await AddResponse(request, response)

@app.put("/sv/admin/editPayload")
async def EditResponsePayloadRequest( request: Request, response: Response):
    return await EditResponsePayload(request, response)

@app.put("/sv/admin/setTrafficAnalyzer")
async def SetTrafficAnalyzerStatusRequest( request: Request, response: Response):
    return await SetTrafficAnalyzerStatus(request, response)

@app.options("/{full_path:path}")
async def OptionsRequest( request: Request, response:Response):
    response.status_code=204