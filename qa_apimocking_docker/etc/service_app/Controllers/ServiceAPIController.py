import json
from fastapi import Request, Response
import uuid
import requests
from Controllers.DataBaseController import *
from fastapi.responses import JSONResponse
from fastapi import HTTPException, status
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

current_day = datetime.now().strftime("%Y-%m-%d")
filename = f'/home/python/app/logs/servicevirtualization_{current_day}.log'

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S ',
                    filename=filename, filemode='a')

handler = TimedRotatingFileHandler(filename, when="midnight", interval=1, backupCount=30)
handler.setLevel(logging.INFO)
logging.getLogger().addHandler(handler)

logging.getLogger('cassandra').setLevel(logging.CRITICAL) 

async def Auth(request):
    r = requests.post('http://user_app:8003/sv/user/auth', headers = request.headers)
    return r.json(), r.status_code

async def AddignServiceToUser(request, response):
    body = await request.json()
    service = body.get('service')
    user = body.get('user')
    if service and user:
        authJSON, authStatus = await Auth(request)
        if authStatus != 200:
            HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		    detail="User unauthorized",
		    headers={"WWW-Authenticate": "Bearer"})
            return HTTPException
        else:
            admin = authJSON.get('username')
            adminID = GetUserID(admin)
            if ValidateAdminRole(adminID) == 1:
                serviceCount = ExistingService(service)
                if ValidateUserExist(user) > 0:
                    userID = GetUserID(user)
                    if serviceCount > 0:
                        serviceID = GetServiceID(service)
                        if VerifyExistingPermission(userID, serviceID) == 0:
                            AddServiceByUserID(userID, serviceID)
                            logging.info('User %s add permisions over %s service for user %s.', admin, service, user)
                            response.status_code=200
                            return "Service permission was added."
                        else:
                            logging.warning('User %s attempted to add permisions over %s service for user %s, but the permission already exists.', admin, service, user)
                            response.status_code=400
                            return "The provided user already has permissions for the provided service."
                    else:
                        response.status_code=400
                        return "The provided service doesn't exist."
                else:
                    response.status_code=400
                    return "User provided doesn't exist yet."
            else:
                logging.warning('User %s attempted to add permisions over %s service for user %s, but this could not be completed for missing admin permissions.', admin, service, user)
                response.status_code=401
                return "User doesn't have admin permissions."
    else:
        response.status_code=400
        return "Provide at least service and user."

async def DeleteServiceToUser(request, response):
    body = await request.json()
    service = body.get('service')
    user = body.get('user')
    if service and user:
        authJSON, authStatus = await Auth(request)
        if authStatus != 200:
            HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		    detail="User unauthorized",
		    headers={"WWW-Authenticate": "Bearer"})
            return HTTPException
        else:
            admin = authJSON.get('username')
            adminID = GetUserID(admin)
            if ValidateAdminRole(adminID) == 1:
                serviceCount = ExistingService(service)
                if ValidateUserExist(user) > 0:
                    userID = GetUserID(user)
                    if serviceCount > 0:
                        serviceID = GetServiceID(service)
                        if VerifyExistingPermission(userID, serviceID) == 1:
                            DeleteServiceByUserID(userID, serviceID)
                            logging.info('User %s deleted permisions over %s service for user %s.', admin, service, user)
                            response.status_code=200
                            return "Service permission was deleted."
                        else:
                            logging.warning('User %s attempted to delete permisions over %s service for user %s, but the permission doesn\'t exist.', admin, service, user)
                            response.status_code=400
                            return "Service permission doesn't exist."
                    else:
                        response.status_code=400
                        return "The provided service doesn't exist."
                else:
                    response.status_code=400
                    return "User provided doesn't exist yet."
            else:
                logging.warning('User %s attempted to delete permisions over %s service for user %s, but this could not be completed for missing admin permissions.', admin, service, user)
                response.status_code=401
                return "User doesn't have admin permissions."
    else:
        response.status_code=400
        return "Provide at least service and user."
    
async def DeleteAllServicesToUser(request, response):
    body = await request.json()
    service_name = body.get('service_name')
    user = body.get('user')
    if service_name and user:
        authJSON, authStatus = await Auth(request)
        if authStatus != 200:
            HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		    detail="User unauthorized",
		    headers={"WWW-Authenticate": "Bearer"})
            return HTTPException
        else:
            admin = authJSON.get('username')
            adminID = GetUserID(admin)
            if ValidateAdminRole(adminID) == 1:
                serviceCount = ExistingServiceName(service_name)
                if ValidateUserExist(user) > 0:
                    userID = GetUserID(user)
                    if serviceCount > 0:
                        if DeleteHostsByServiceName(userID, service_name):
                            logging.info('User %s deleted permisions over %s service for user %s.', admin, service_name, user)
                            response.status_code=200
                            return "Service permissions was deleted."
                        else:
                            logging.warning('User %s attempted to delete permisions over %s service for user %s.', admin, service_name, user)
                            response.status_code=400
                            return "Service permission doesn't exist."
                    else:
                        response.status_code=400
                        return "The provided service doesn't exist."
                else:
                    response.status_code=400
                    return "User provided doesn't exist yet."
            else:
                logging.warning('User %s attempted to delete permisions over %s service for user %s, but this could not be completed for missing admin permissions.', admin, service_name, user)
                response.status_code=401
                return "User doesn't have admin permissions."
    else:
        response.status_code=400
        return "Provide at least service and user."

async def GetUsersByService(request: Request, response: Response):
    query_params = request.query_params
    host = query_params.get('service')
    authJSON, authStatus = await Auth(request)
    if authStatus != 200:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		detail="User unauthorized",
	    headers={"WWW-Authenticate": "Bearer"})
        return HTTPException
    else:
        admin = authJSON.get('username')
        adminID = GetUserID(admin)
        if ValidateAdminRole(adminID) == 1:
            if host:
                if ExistingService(host) > 0:
                    serviceID = GetServiceID(host)
                    userResponses = GetAllUsersByServiceID(serviceID)
                    adminResponses = GetAdminInformation()
                    responses = userResponses + adminResponses
                    if responses is None:
                        logging.error('Failed to retrieve users for service %s from database, requested by user %s.', host, admin)
                        response.status_code = 400
                        return "Error getting services, please check provided information."
                    else:
                        response.status_code = 200
                        return responses
                else:
                    response.status_code = 400
                    return "Provided service doesn't exist yet."
            else:
                response.status_code = 400
                return "Please provide complete information."
        else:
            response.status_code = 401
            return "User unauthorized."

async def GetUserServices(request: Request, response: Response):
    query_params = request.query_params
    user = query_params.get('user')
    userID = query_params.get('id')
    authJSON, authStatus = await Auth(request)
    if authStatus != 200:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		detail="User unauthorized",
	    headers={"WWW-Authenticate": "Bearer"})
        return HTTPException
    else:
        admin = authJSON.get('username')
        adminID = GetUserID(admin)
        if ValidateAdminRole(adminID) == 1:
            if userID:
                if ValidateUserExistByID(uuid.UUID(str(userID))) > 0:
                    if ValidateAdminRole(uuid.UUID(str(userID))) == 1:
                        responses = GetAllServices()
                        if responses is None:
                            logging.error('Failed to retrieve services for user %s from database, requested by user %s.', userID, admin)
                            response.status_code = 500
                            return "Error getting services, please check provided information."
                        else:
                            logging.info('User %s requested all services permissions for user %s.', admin, userID)
                            response.status_code = 200
                            return responses
                    else:
                        responses = UserServices(userID)
                        if responses is None:
                            logging.error('Failed to retrieve services for user %s from database, requested by user %s.', userID, admin)
                            response.status_code = 500
                            return "Error getting services, please check provided information."
                        else:
                            logging.info('User %s requested all services permissions for user %s.', admin, userID)
                            response.status_code = 200
                            return responses
                else:
                    response = JSONResponse(content={"message": "Provided user doesn't exist."}, status_code=400)
                    return response
            elif user:
                if ValidateUserExist(user) > 0:
                    userID = GetUserID(user)
                    if ValidateAdminRole(uuid.UUID(str(userID))) == 1:
                        responses = GetAllServices()
                        if responses is None:
                            logging.error('Failed to retrieve services for user %s from database, requested by user %s.', user, admin)
                            response.status_code = 400
                            return "Error getting services, please check provided information."
                        else:
                            logging.info('User %s requested all services permissions for user %s.', admin, user)
                            response.status_code = 200
                            return responses
                    else:
                        responses = UserServices(userID)
                        if responses is None:
                            logging.error('Failed to retrieve services for user %s from database, requested by user %s.', user, admin)
                            response.status_code = 400
                            return "Error getting services, please check provided information."
                        else:
                            logging.info('User %s requested all services permissions for user %s.', admin, user)
                            response.status_code = 200
                            return responses
                else:
                    response = JSONResponse(content={"message": "Provided user doesn't exist."}, status_code=400)
                    return response
            else:
                responses = GetAllServices()
                if responses is None:
                    logging.error('Failed to retrieve his services for user %s from database.', admin)
                    response.status_code = 400
                    return "Error getting services, please check provided information."
                else:
                    logging.info('User %s requested his services permissions.', admin)
                    response.status_code = 200
                    return responses
        else:
            if user or userID:
                response.status_code = 400
                return "User doesn't have admin permissions, so please do not request the access for other users."
            else:
                responses = UserServices(adminID)
                if responses is None:
                    logging.error('Failed to retrieve his services for user %s from database.', admin)
                    response.status_code = 500
                    return "Error getting services, please check provided information."
                else:
                    logging.info('User %s requested his services permissions.', admin)
                    response.status_code = 200
                    return responses
                
async def GetHostsByService(request: Request, response: Response):
    query_params = request.query_params
    user = query_params.get('user')
    service_name = query_params.get('service_name')
    authJSON, authStatus = await Auth(request)
    if authStatus != 200:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		detail="User unauthorized",
	    headers={"WWW-Authenticate": "Bearer"})
        return HTTPException
    else:
        admin = authJSON.get('username')
        adminID = GetUserID(admin)
        if ValidateAdminRole(adminID) == 1:
            userID = GetUserID(user)
            if userID:
                if ValidateUserExistByID(uuid.UUID(str(userID))) > 0:
                    responses = UserServices(userID)
                    if responses is None:
                        logging.error('Failed to retrieve services for user %s from database, requested by user %s.', userID, admin)
                        response.status_code = 500
                        return "Error getting services, please check provided information."
                    else:
                        for entry in responses:
                            if entry["Name"] == service_name:  
                                return {"Hosts": entry["Hosts"]}
                        response.status_code = 400
                        return "Service doesn't exist for the provided user."
                else:
                    response = JSONResponse(content={"message": "Provided user doesn't exist."}, status_code=400)
                    return response
            else:
                response.status_code = 400
                return "Please provide user ID."
        else:
            if user or userID:
                response.status_code = 400
                return "User doesn't have admin permissions, so please do not request the access for other users."
            else:
                responses = UserServices(adminID)
                if responses is None:
                    logging.error('Failed to retrieve his services for user %s from database.', admin)
                    response.status_code = 500
                    return "Error getting services, please check provided information."
                else:
                    logging.info('User %s requested his services permissions.', admin)
                    response.status_code = 200
                    return responses

async def GetAllUsers(request: Request, response: Response):
    authJSON, authStatus = await Auth(request)
    if authStatus != 200:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		detail="User unauthorized",
		headers={"WWW-Authenticate": "Bearer"})
        return HTTPException
    else:
        admin = authJSON.get('username')
        adminID = GetUserID(admin)
        if ValidateAdminRole(adminID) == 1:
            responses = AllUsers()
            if responses is None:
                logging.error('Failed to retrieve all users from database, requested by user %s.', admin)
                response.status_code = 400
                return "Error getting services, please check provided information."
            else:
                response.status_code = 200
                return responses
        else:
            response.status_code = 401
            return "User unauthorized."
