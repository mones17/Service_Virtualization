from ast import Not
import datetime
import uuid
from fastapi import Request, Response, HTTPException, status
from Controllers.DataBaseController import *
from fastapi.responses import JSONResponse
import json
import uuid
from datetime import datetime, timedelta
import requests

async def Auth(request):
    r = requests.post('http://user_app:8003/sv/user/auth', headers = request.headers)
    return r.json(), r.status_code

async def GetUserInformation(request: Request):
    authJSON, authStatus = await Auth(request)
    if authStatus != 200:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"})
        return HTTPException, None
    else:
        username = authJSON.get('username')
        userID = GetUserID(username)
        if ValidateAdminRole(userID) == 1:
            return userID, 'admin'
        else:
            return userID, 'user'

async def ValidateAdminOrServiceAccess(request: Request, serviceID):
    authJSON, authStatus = await Auth(request)
    if authStatus != 200:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"})
        return HTTPException, None
    else:
        username = authJSON.get('username')
        userID = GetUserID(username)
        if ValidateAdminRole(userID) == 1:
            return userID, 'admin'
        elif GetUserAccess(userID, serviceID) != 0:
            return userID, 'user'
        else:
            return None, None

async def APIModesTransactions(request: Request, response: Response):                        
    query_params = request.query_params
    service = query_params.get("service")
    resource = query_params.get("resource")
    if resource and not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Missing service parameter")
    else:
        if not service and not resource:
            userID, role = await GetUserInformation(request)
            if userID and role:
                retrivedData = GetAllAPITransactions(userID, role)
                if retrivedData is None:
                    response.status_code = 500
                    return "Failed to retrive data from database"
                else:
                    response.status_code = 200
                    return retrivedData
            else:
                response.status_code = 401
                return "User unauthorized."
        elif service or (service and resource):
            serviceID = GetServiceIDByHost(service)
            if serviceID:
                userID, role = await ValidateAdminOrServiceAccess(request, serviceID)
                if userID and role:
                    retrivedData = GetAPITransactions(service, resource)
                    if retrivedData is None:
                        response.status_code = 500
                        return "Failed to retrive data from database"
                    else:
                        response.status_code = 200
                        return retrivedData
                else:
                    response.status_code = 401
                    return "User unauthorized."
            else:
                response.status_code = 404
                return "Provided service does not exist yet."
        else:
            response.status_code = 400
            return "Something went wrong."
        
async def FetchResponsesPercentage(request: Request, response: Response):
    query_params = request.query_params
    service = query_params.get("service")
    resource = query_params.get("resource")
    if resource and not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Missing service parameter")
    else:
        if not service and not resource:
            userID, role = await GetUserInformation(request)
            if userID and role:
                retrivedData = GetAllResponsesPercentage(userID, role)
                if retrivedData is None:
                    response.status_code = 500
                    return "Failed to retrive data from database"
                else:
                    response.status_code = 200
                    return retrivedData
            else:
                response.status_code = 401
                return "User unauthorized."
        elif service or (service and resource):
            serviceID = GetServiceIDByHost(service)
            if serviceID:
                userID, role = await ValidateAdminOrServiceAccess(request, serviceID)
                if userID and role:
                    retrivedData = GetResponsesPercentage(service, resource)
                    if retrivedData is None:
                        response.status_code = 500
                        return "Failed to retrive data from database"
                    else:
                        response.status_code = 200
                        return retrivedData
                else:
                    response.status_code = 401
                    return "User unauthorized."
            else:
                response.status_code = 404
                return "Provided service does not exist yet."
        else:
            response.status_code = 400
            return "Something went wrong."
        
async def TimeSaved(request: Request, response: Response):
    query_params = request.query_params
    service = query_params.get("service")
    resource = query_params.get("resource")
    if resource and not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Missing service parameter")
    else:
        if not service and not resource:
            userID, role = await GetUserInformation(request)
            if userID and role:
                retrivedData = GetAllTimeSaved(userID, role)
                if retrivedData is None:
                    response.status_code = 500
                    return "Failed to retrive data from database"
                else:
                    response.status_code = 200
                    return retrivedData
            else:
                response.status_code = 401
                return "User unauthorized."
        elif service or (service and resource):
            serviceID = GetServiceIDByHost(service)
            if serviceID:
                userID, role = await ValidateAdminOrServiceAccess(request, serviceID)
                if userID and role:
                    if resource:
                        if ResourceExists(serviceID, resource):
                            retrivedData = GetTimeSaved(service, resource)
                            if retrivedData is None:
                                response.status_code = 500
                                return "Failed to retrive data from database"
                            else:
                                response.status_code = 200
                                return retrivedData
                        else:
                            response.status_code = 404
                            return "Provided resource does not exist yet."
                    else:
                        retrivedData = GetTimeSaved(service, resource)
                        if retrivedData is None:
                            response.status_code = 500
                            return "Failed to retrive data from database"
                        else:
                            response.status_code = 200
                            return retrivedData
                else:
                    response.status_code = 401
                    return "User unauthorized."
            else:
                response.status_code = 404
                return "Provided service does not exist yet."
        else:
            response.status_code = 400
            return "Something went wrong."
        
async def FetchActivity(request: Request, response: Response):
    query_params = request.query_params
    service = query_params.get("service")
    resource = query_params.get("resource")
    if resource and not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Missing service parameter")
    else:
        if not service and not resource:
            userID, role = await GetUserInformation(request)
            if userID and role:
                retrivedData = GetAllActivity(userID, role)
                if retrivedData is None:
                    response.status_code = 500
                    return "Failed to retrive data from database"
                else:
                    response.status_code = 200
                    return retrivedData
            else:
                response.status_code = 401
                return "User unauthorized."
        elif service or (service and resource):
            serviceID = GetServiceID(service)
            if serviceID:
                userID, role = await ValidateAdminOrServiceAccess(request, serviceID)
                if userID and role:
                    host = GetHostByName(service)
                    retrivedData = GetActivity(host, resource)
                    if retrivedData is None:
                        response.status_code = 500
                        return "Failed to retrive data from database"
                    else:
                        response.status_code = 200
                        return retrivedData
                else:
                    response.status_code = 401
                    return "User unauthorized."
            else:
                response.status_code = 404
                return "Provided service does not exist yet."
        else:
            response.status_code = 400
            return "Something went wrong."
        
async def LastSevenDaysTransactions(request: Request, response: Response):
    query_params = request.query_params
    service = query_params.get("service")
    resource = query_params.get("resource")
    if resource and not service:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Missing service parameter")
    else:
        retrivedData = GetLastSevenDaysTransactionsInfo("aslkda", "lkalsknd")
        response.status_code = 200
        return retrivedData
        