from uuid import UUID
from fastapi import Request, Response, FastAPI
from Controllers.DashboardController import *

app = FastAPI()

@app.get("/sv/dashboard/newrelic/health")
async def HealthCheck():
    return {"status": "health"}

@app.get("/sv/dashboard/apiModeTransactions")
async def APIModesTransactionsRequest( request: Request, response: Response):
    return await APIModesTransactions( request, response )

@app.get("/sv/dashboard/responsesPercentage")
async def FetchResponsesPercentageRequest( request: Request, response: Response):
    return await FetchResponsesPercentage( request, response )

@app.get("/sv/dashboard/timeSaved")
async def TimeSavedRequest( request: Request, response: Response):
    return await TimeSaved( request, response )

@app.get("/sv/dashboard/activity")
async def FetchActivityRequest( request: Request, response: Response):
    return await FetchActivity( request, response )

@app.get("/sv/dashboard/lastSevenDaysTransactions")
async def FetchLastSevenDaysTransactions( request: Request, response: Response):
    return await LastSevenDaysTransactions( request, response )

@app.options("/{full_path:path}")
async def OptionsRequest( request: Request, response:Response):
    response.status_code=204