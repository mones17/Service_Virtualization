from uuid import UUID
from fastapi import Request, Response, FastAPI
from Controllers.UserAPIController import *;

app = FastAPI()

@app.get("/sv/user/newrelic/health")
async def HealthCheck():
    return {"status": "health"}

@app.post("/sv/user/createUser")
async def CreateUserRequest( request: Request, response: Response):
    return await CreateUser(request, response)

@app.post("/sv/user/login")
async def LoginRequest( request: Request, response: Response):
    return await Login(request, response)

@app.get("/sv/user/getUserInformation")
async def GetUserInformationRequest( request: Request, response: Response):
    return await GetUserInfo(request, response)

@app.post("/sv/user/auth")
async def LoginRequest( request: Request):
    return await Auth(request)

@app.delete("/sv/user/deleteUser/{userID}")
async def DeleteUserByIDRequest( request: Request, response: Response, userID):
    return await DeleteUserByID(request, response, userID)

@app.put("/sv/user/updateUser/{userID}")
async def UpdateUserByIDRequest( request: Request, response: Response, userID):
    return await UpdateUserByID(request, response, userID)

@app.put("/sv/user/resetPassword")
async def ResetPasswordRequest( request: Request, response: Response):
    return await ResetPassword(request, response)

@app.post("/sv/user/sendNewUserEmail")
async def SendNewUserEmailRequest( request: Request, response: Response):
    return await SendNewUserEmail(request, response)

@app.get("/sv/user/getEmailTokenInformation")
async def GetEmailTokenInformationRequest( request: Request):
    return await GetEmailTokenInformation(request)

@app.options("/{full_path:path}")
async def OptionsRequest( request: Request, response:Response):
    response.status_code=204