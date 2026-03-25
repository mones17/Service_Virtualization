from contextlib import nullcontext
import json
from logging.handlers import TimedRotatingFileHandler
from math import log
from multiprocessing import log_to_stderr
from venv import logger
from fastapi import Request, Response
import uuid
import requests
from Controllers.DataBaseController import *
from Controllers.DataBaseLogController import *
from fastapi import HTTPException, status
import re
import logging
from datetime import datetime, timezone
from Helpers.TypeValidation import *
import xmltodict

current_day = datetime.now().strftime("%Y-%m-%d")
filename = f'/home/python/app/logs/servicevirtualization_{current_day}.log'

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S ',
                    filename=filename, filemode='a')

handler = TimedRotatingFileHandler(filename, when="midnight", interval=1, backupCount=30)
handler.setLevel(logging.INFO)
logging.getLogger().addHandler(handler)

logging.getLogger('cassandra').setLevel(logging.CRITICAL) 

async def GetResponses(request: Request, response:Response):
    query_params = request.query_params
    service = query_params.get("service")
    resource = query_params.get("resource")
    if service and resource:
        if ValidateServiceExist(service) > 0:
            if ValidateResourceExist(resource) > 0:
                requestID = GetResquestID(service, resource)
                serviceID = GetServiceID(service)
                adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
                if adminRole == 1:
                    responses = GetResponsesUsingRequestID(requestID)
                    if responses is None:
                        log_message = 'Failed to retrieve data from database for user {}, for service {} and resource {}.'.format(username, service, resource)
                        logging.error('%s', log_message)
                        log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                        log_time = datetime.fromtimestamp(log_record.created)
                        InsertLogInDatabase(log_time, username, 'GRS, EDB', "Request", True, serviceID, requestID, '')
                        response.status_code = 500
                        return "Error getting responses, please check information sent."
                    else:
                        response.status_code = 200
                        return responses
                else:
                    response.status_code = 401
                    return "User unauthorized."
            else:
                response.status_code = 400
                return "The provided resource doesn't exist yet."
        else:
            response.status_code = 400
            return "The provided service doesn't exist yet."
    else:
        response.status_code = 400
        return "Please provide at least service and resource."

async def AcceptResponse(request: Request, response:Response):
    query_params = request.query_params
    responseID = query_params.get("responseID")
    role, username = await ValidateUserRole(request)
    if responseID:
        if ValidateResponseExistByID(uuid.UUID(responseID)) > 0:
            requestID = GetRequestIDByResponseID(uuid.UUID(responseID))
            serviceID = GetServiceIDByRequestID(uuid.UUID(requestID))
            adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
            service, resource = GetServiceResourceByID(uuid.UUID(serviceID), uuid.UUID(requestID))
            if adminRole == 1:
                currentStatus = GetResponseStatus(uuid.UUID(responseID))
                wasChangeMade = AcceptResponseUsingResponseID(uuid.UUID(responseID))
                if wasChangeMade:
                    if SaveResponseStatus(serviceID, requestID, 'accepted', currentStatus):
                        log_message = 'The user {} attempted to accept response {} for {}, {} and the action was completed successfully.'.format(username, service, resource, responseID)
                        logging.info('%s', log_message)
                        log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                        log_time = datetime.fromtimestamp(log_record.created)
                        InsertLogInDatabase(log_time, username, 'ACR', "Response", False, serviceID, requestID, responseID)
                        response.status_code = 200
                        message = "Response was accepted."
                else:
                    log_message = 'The user {} attempted to accept response {} for {}, {} but a system error occurred and the action could not be completed.'.format(username, service, resource, responseID)
                    logging.error('%s', log_message)
                    log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                    log_time = datetime.fromtimestamp(log_record.created)
                    InsertLogInDatabase(log_time, username, 'ACR, EDB', "Response", True, serviceID, requestID, responseID)
                    response.status_code = 500
                    message = "Error accepting the response."
            else:
                logging.warning('User %s unauthorized to accept responses for %.', username, service)
                response.status_code = 401
                message = "User unauthorized."
        else:
            logging.warning('User %s attempted to accept a non-existent response %s.', username, responseID)
            response.status_code = 400
            message = "The provided response ID doesn't exist yet."
    else:
        response.status_code = 400
        message = "Please provide complete information, at least response ID."
    return message

async def RejectResponse(request: Request, response:Response):
    query_params = request.query_params
    responseID = query_params.get("responseID")
    if responseID:
        role, username = await ValidateUserRole(request)
        if ValidateResponseExistByID(uuid.UUID(responseID)) > 0:
            requestID = GetRequestIDByResponseID(uuid.UUID(responseID))
            serviceID = GetServiceIDByRequestID(uuid.UUID(requestID))
            service, resource = GetServiceResourceByID(uuid.UUID(serviceID), uuid.UUID(requestID))
            adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
            if adminRole == 1:
                currentStatus = GetResponseStatus(uuid.UUID(responseID))
                wasChangeMade = RejectResponseUsingResponseID(uuid.UUID(responseID))
                if wasChangeMade:
                    if SaveResponseStatus(serviceID, requestID, 'rejected', currentStatus):
                        log_message = 'The user {} attempted to reject response {} for {}, {} and the action was completed successfully.'.format(username, service, resource, responseID)
                        logging.info('%s', log_message)
                        log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                        log_time = datetime.fromtimestamp(log_record.created)
                        InsertLogInDatabase(log_time, username, 'RJR', "Response", False, serviceID, requestID, responseID)
                        response.status_code = 200
                        message = "Response was rejected"
                else:
                    log_message = 'The user {} attempted to reject response {} for {}, {} but a system error occurred and the action could not be completed.'.format(username, service, resource, responseID)
                    logging.error('%s', log_message)
                    log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                    log_time = datetime.fromtimestamp(log_record.created)
                    InsertLogInDatabase(log_time, username, 'RJR, EDB', "Response", True, serviceID, requestID, responseID)
                    response.status_code = 500
                    message = "Error rejecting the response"
            else:
                logging.warning('User %s unauthorized to reject responses for %.', username, service)
                response.status_code = 401
                message = "User unauthorized."
        else:
            logging.warning('User %s attempted to reject a non-existent response %s.', username, responseID)
            response.status_code = 400
            message = "The provided response ID doesn't exist yet."
    else:
        response.status_code = 400
        message = "Please provide complete information, at least response ID."
    return message

async def AddRoute(request: Request, response:Response):
    body = await request.json()
    host = body.get('host')
    route = body.get('route')
    method = body.get('method')
    name = body.get('name') 
    if host and route and method and name:
        route = re.findall("[\w!@#$%^&*()_+-][\w!@#$%^&*()_+/-]+", route)
        route = str(route[0])
        body['route'] = route
        role, username = await ValidateUserRole(request)
        if ValidateServiceExist(host) > 0:
            serviceID = GetServiceID(host)
            serviceName = GetServiceNameByHost(host)
            adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
            if adminRole == 1:
                if ValidateRouteExist(serviceID, route) == 0:
                    if ValidateResourceNameExist(serviceID, name) == 0:
                        requestSaved = SaveNewRequest(serviceID, route, method, name)
                        if requestSaved:
                            nginx_appResponse = requests.post('http://nginx_app:8001/sv/routes/addRoute', json=body)
                            if nginx_appResponse.status_code == 200:
                                routeID = GetRouteID(serviceID, route)
                                log_message = 'User {} added a new route, {}, for service {}. The route was successfully added to the system.'.format(username, name, serviceName)
                                logging.info('%s', log_message)
                                log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                                log_time = datetime.fromtimestamp(log_record.created)
                                InsertLogInDatabase(log_time, username, 'ART', "Service", False, serviceID, '', '')
                                response.status_code = 200
                                message = "New route added"
                            else:
                                log_message = 'User {} attempted to add route {} for service {}, but the action failed on nginx.'.format(username, name, serviceName)
                                logging.error('%s', log_message)
                                log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                                log_time = datetime.fromtimestamp(log_record.created)
                                InsertLogInDatabase(log_time, username, 'ART, ENX', "Service", True, serviceID, '', '')
                                response.status_code = 500
                                message = "Error adding the request in the configuration file"
                        else:
                            log_message = 'User {} attempted to add route {} for service {}, but the action failed on database.'.format(username, name, serviceName)
                            logging.error('%s', log_message)
                            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                            log_time = datetime.fromtimestamp(log_record.created)
                            InsertLogInDatabase(log_time, username, 'ART, EDB', "Service", True, serviceID, '', '')
                            response.status_code = 500
                            message = "Error saving the request in the DB"
                    else:
                        response.status_code = 400
                        message = "Provided name already exist, try with another."
                else:
                    response.status_code = 400
                    message = "Provided route already exist for this service."
            else:
                logging.warning('User %s attempted to add route %s for service %s, but the action failed for missing admin permissions.', username, name, serviceName)
                response.status_code = 401
                message = "User unauthorized."
        else:
            response.status_code = 401
            message = "This services doesn't exist yet, user unauthorized to create new services."
    else:
        response.status_code = 400
        message = "Please provide complete information: host, route, actual ip and method."
    return message

async def EditRoute(request: Request, response:Response):
    query_params = request.query_params
    host = query_params.get('service')
    resource = query_params.get('resource')
    body = await request.json()
    route = body.get('route')
    method = body.get('method')
    name = body.get('name')
    role, username = await ValidateUserRole(request)
    if host and resource:
        resource = re.findall("[\w!@#$%^&*()_+-][\w!@#$%^&*()_+/-]+", resource)
        resource = str(resource[0])
        if route or method or name:
            if ValidateServiceExist(host) > 0:
                serviceID = GetServiceID(host)
                serviceName = GetServiceNameByHost(host)
                adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
                if adminRole == 1:
                    resourceID, actualName, actualRoute, actualMethod = ValidateGetRouteInformation(serviceID, resource)
                    if resourceID and actualName and actualRoute and actualMethod:
                        if route:
                            route = re.findall("[\w!@#$%^&*()_+-][\w!@#$%^&*()_+/-]+", route)
                            route = str(route[0])
                            body['route'] = route
                        route = None if actualRoute == route else route if route else True
                        name = None if actualName == name else name if name else True
                        method = None if actualMethod == method else method if method else True
                        routeBand = ValidateRouteExist(serviceID, route) == 0 if route else True  
                        nameBand = ValidateRouteNameExist(serviceID, name) == 0 if name else True
                        methodBand = True if name or route else None if method is None else True
                        if routeBand and nameBand and methodBand:
                            UpdateRoute(resourceID, route, method, name)
                            messageRoute = "Route {} updated to {}. ".format(actualRoute, route) if route else ""
                            messageMethod = "Method {} updated to {}.".format(actualMethod, method) if method else ""
                            messageName = "Name {} updated to {}.".format(actualName, name) if name else ""
                            logMessage = messageRoute + messageMethod + messageName
                            log_message = 'User {} made some changes for {}, {}: {}'.format(username, serviceName, resource, logMessage)
                            logging.info('%s', log_message)
                            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                            log_time = datetime.fromtimestamp(log_record.created)
                            InsertLogInDatabase(log_time, username, 'ERT', "Request", False, serviceID, resourceID, '')
                            message = "Route updated successfully. "  
                            response.status_code = 200  
                        else:  
                            messageRoute = "The new route what you're gonna try to insert, currently exist. " if not routeBand else ""  
                            messageName = "The name that you're trying to insert currently exist, please select other." if not nameBand else ""  
                            message = messageRoute + messageName
                            if message == "":
                                message = "Trying to submit a form without changes."
                                response.status_code = 304
                            else:
                                response.status_code = 400
                            logging.warning('User %s attempted to made some changes for %s, %s but: %s', username, serviceName, resource, message)
                    else:
                        logging.warning('User %s attempted to made some changes for %s, but for non-existing resource.', username, serviceName)
                        response.stauts_code = 400
                        message = "Provided route doesn't exist yet."
                else:
                    logging.warning('User %s attempted to made some changes for %s, %s but the action failed for missing admin permissions.', username, serviceName, resource)
                    response.status_code = 401
                    message = "User unauthorized."
            else:
                logging.warning('User %s attempted to made some changes for non-existing service %s.', username, host)
                response.stauts_code = 400
                message = "Provided service doesn't exist yet."
        else:
            response.stauts_code = 400
            message = "Provide at least one filed to edit."
    else:
        response.status_code = 400
        message = "Provide the host and service to edit."
    return message

async def DeleteRoute(request: Request, response:Response):
    query_params = request.query_params
    host = query_params.get('service')
    resource = query_params.get('resource')
    role, username = await ValidateUserRole(request)
    if host and resource:
        if ValidateServiceExist(host) > 0:
            serviceID = GetServiceID(host)
            service = GetServiceNameByHost(host)
            if ValidateRouteExist(serviceID, resource) == 1:
                adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
                if adminRole == 1:
                    resourceID = GetResquestID(host, resource)
                    if DeleteAllResponsesAndResourceByID(resourceID):
                        body = {}
                        body['service'] = host
                        body['route'] = resource
                        nginx_appResponse = requests.post('http://nginx_app:8001/sv/routes/deleteRoute', json=body)
                        if nginx_appResponse.status_code == 200:
                            log_message = 'User {} initiated the deletion of the route {} for service {} and the action was completed successfully.'.format(username, resource, service)
                            logging.info('%s', log_message)
                            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                            log_time = datetime.fromtimestamp(log_record.created)
                            InsertLogInDatabase(log_time, username, 'DRT', "Request", False, serviceID, resourceID, '')
                            response.status_code = 200
                            message = "Route deleted successfully."
                        else:
                            log_message = 'User {} attempted to delete route {} for service {}, but the action failed on nginx.'.format(username, resource, service)
                            logging.error('%s', log_message)
                            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                            log_time = datetime.fromtimestamp(log_record.created)
                            InsertLogInDatabase(log_time, username, 'DRT, ENX', "Request", True, serviceID, resourceID, '')
                            response.status_code = 500
                            message = "Error deleting the route in the configuration file"
                    else:
                        log_message = 'User {} attempted to delete route {} for service {}, but the action failed on database.'.format(username, resource, service)
                        logging.error('%s', log_message)
                        log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                        log_time = datetime.fromtimestamp(log_record.created)
                        InsertLogInDatabase(log_time, username, 'DRT, EDB', "Request", True, serviceID, resourceID, '')
                        response.status_code = 500
                        message = "Route can't be deleted from DB."
                else:
                    logging.warning('User %s attempted to delete route %s for service %s but the action failed for missing admin permissions.', username, resource, service)
                    response.status_code = 401
                    message = "User unauthorized."
            else:
                logging.warning('User %s attempted to delete non-existing route %s for service %s.', username, resource, service)
                response.status_code = 400
                message = "Route provided doesn't exist yet."
        else:
            logging.warning('User %s attempted to delete route for non-existing service %s.', username, host)
            response.status_code = 400
            message = "Service provided doesn't exist yet."
    else:
        response.status_code = 400
        message = "Provide complete information, service and resource."
    return message

async def AddService(request: Request, response:Response):
    body = await request.json()
    portfolio = body.get('portfolio')
    region = body.get('region')
    name = body.get('name')
    host = body.get('host')
    hostname = body.get('hostname')
    actual_ip = body.get('actual_ip')
    port = body.get('port')
    adminRole, username = await ValidateUserRole(request)
    if adminRole == 1:
        if portfolio and region and host and name and actual_ip and port:
            if ValidateServiceExist(host) == 0:
                serviceSaved = SaveNewService(host, name, actual_ip, port, portfolio, region, hostname)
                if serviceSaved:
                    nginx_appResponse = requests.post('http://nginx_app:8001/sv/routes/addService', json=body)
                    if nginx_appResponse:
                        serviceID = GetServiceID(host)
                        log_message = 'User {} added a new service {}. The service was successfully added to the system.'.format(username, name)
                        logging.info('%s', log_message)
                        log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})    
                        log_time = datetime.fromtimestamp(log_record.created)
                        InsertLogInDatabase(log_time, username, 'ASR', "Service", False, serviceID, '', '')
                        response.status_code = 200
                        message = "New service added"
                    else:
                        log_message = 'User {} attempted to add service {}, but the action failed on nginx.'.format(username, name)
                        logging.error('%s', log_message)
                        log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                        log_time = datetime.fromtimestamp(log_record.created)
                        InsertLogInDatabase(log_time, username, 'ASR, ENX', "Service", True, '00000000-0000-0000-0000-000000000000', '', '')
                        response.status_code = 500
                        message = "Error adding the service in the configuration file"
                else:
                    log_message = 'User {} attempted to add service {}, but the action failed on database.'.format(username, name)
                    logging.error('%s', log_message)
                    log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                    log_time = datetime.fromtimestamp(log_record.created)
                    InsertLogInDatabase(log_time, username, 'ASR, EDB', "Service", True, '00000000-0000-0000-0000-000000000000', '', '')
                    response.status_code = 500
                    message = "Error saving the service in the DB"
            else:
                response.status_code = 400
                message = "Provided service already exist."
        else:
            response.status_code = 400
            message = "Please provide complete information: host, name and actual ip."
    else:
        logging.warning('User %s attempted to add service %s, but the action failed for missing admin permissions.', username, name)
        response.status_code = 401
        message = "User unauthorized."
    return message

async def EditService(request: Request, response: Response):
    query_params = request.query_params
    service = query_params.get('service')
    body = await request.json()
    host = body.get('host')
    name = body.get('name')
    actual_ip = body.get('actual_ip')
    port = body.get('port')
    adminRole, username = await ValidateUserRole(request)
    if adminRole == 1:
        if service:
            if host or name or actual_ip or port:
                serviceID, actualName, actualHost, actualActualIP, actualPort = ValidateGetServiceInfromation(service)
                if serviceID and actualName and actualHost and actualActualIP and actualPort:
                    serviceName = GetServiceNameByHost(service)
                    host = None if actualHost == host else host if host else True
                    name = None if actualName == name else name if name else True
                    actual_ip = None if actualActualIP == actual_ip else actual_ip if actual_ip else True
                    port = None if actualPort == port else port if port else True
                    hostBand = ValidateServiceExist(host) == 0 if host else True
                    nameBand = True if actual_ip or port or host else None if name is None else True
                    actual_ipBand = True if name or port or host else None if actual_ip is None else True
                    portBand = True if name or actual_ip or host else None if port is None else True
                    edit_body = {
                        "host": service,
                        "new_host": host,
                        "ip": actualActualIP,
                        "new_ip": actual_ip,
                        "port": actualPort,
                        "new_port": port
                    }
                    if hostBand and nameBand and actual_ipBand and portBand:
                        edit_service = requests.post('http://nginx_app:8001/sv/routes/editService', json=edit_body)
                        if edit_service:
                            UpdateService(serviceID, host, name, actual_ip, port)
                            messageHost = "Host {} updated to {}. ".format(actualHost, host) if host else ""
                            messageName = "Name {} updated to {}. ".format(actualName, name) if name else ""
                            messageActualIP = "IP {} updated to {}. ".format(actualActualIP, actual_ip) if actual_ip else ""
                            messagePort = "Port {} updated to {}. ".format(actualPort, port) if port else ""
                            logMessage = messageHost + messageName + messageActualIP + messagePort
                            log_message = 'User {} made some changes for {}: {}'.format(username, serviceName, logMessage)
                            logging.info('%s', log_message)
                            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                            log_time = datetime.fromtimestamp(log_record.created)
                            InsertLogInDatabase(log_time, username, 'ESR', "Service" , False, serviceID, '', '')
                            message = "Service updated successfully. "
                            response.status_code = 200  
                        else:
                            message = "Error editing the service in the configuration file."
                            response.status_code = 500
                    else:
                        message = "The new host what you're gonna try to insert, currently exist." if not hostBand else ""
                        if message == "":
                            message = "Trying to submit a form without changes."
                            response.status_code = 304
                        else:
                            response.status_code = 400 
                        logging.warning('User %s attempted to made some changes for %s, but: %s', username, serviceName, message)
                else:
                    logging.warning('User %s attempted to made some changes for non-existing service %s.', username, service)
                    response.status_code = 400
                    message = "Provided service doesn't exist yet."
            else:
                response.status_code = 400
                message = "Provide at least one field to edit."
        else:
            response.status_code = 400
            message = "Please provide complete information, at least the service to edit."
    else:
        logging.warning('User %s attempted to made some changes for %s, but the action failed for missing admin permissions.', username, service)
        response.status_code = 401
        message = "User unauthorized."
    return message

async def DeleteService(request: Request, response: Response):
    query_params = request.query_params
    host = query_params.get("service")
    adminRole, username = await ValidateUserRole(request)
    if adminRole == 1:
        if host:
            if ValidateServiceExist(host) > 0:
                serviceID = GetServiceID(host)
                serviceName = GetServiceNameByHost(host)
                if DeleteServiceDB(serviceID):
                    body = {}
                    body["service"] = host
                    nginx_appResponse = requests.post('http://nginx_app:8001/sv/routes/deleteService', json=body)
                    if nginx_appResponse.status_code == 200:
                        log_message = 'User {} initiated the deletion of the service {} and the action was completed successfully.'.format(username, serviceName)
                        logging.info('%s', log_message)
                        log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                        log_time = datetime.fromtimestamp(log_record.created)
                        InsertLogInDatabase(log_time, username, 'DSR', "Service", False, serviceID, '', '')
                        response.status_code = 200
                        message = "Service deleted successfully."
                    else:
                        log_message = 'User {} attempted to delete service {}, but the action failed on nginx.'.format(username, serviceName)
                        logging.error('%s', log_message)
                        log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                        log_time = datetime.fromtimestamp(log_record.created)
                        InsertLogInDatabase(log_time, username, 'DSR, ENX', "Service", True, serviceID, '', '')
                        response.status_code = 500
                        message = "Error deleting the service in the configuration file"
                else:
                    log_message = 'User {} attempted to delete service {}, but the action failed on database.'.format(username, serviceName)
                    logging.error('%s', log_message)
                    log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                    log_time = datetime.fromtimestamp(log_record.created)
                    InsertLogInDatabase(log_time, username, 'DSR, EDB', "Service", True, serviceID, '', '')
                    response.status_code = 500
                    message = "Error deleting service in DB."
            else:
                logging.warning('User %s attempted to delete non-existing service %s.', username, host)
                response.status_code = 400
                message = "Provided service host doesn't exist yet."
        else:
            response.status_code = 400
            message = "Provide complete informacion, at least service host."
    else:
        logging.warning('User %s attempted to delete service %s but the action failed for missing admin permissions.', username, host)
        response.status_code = 401
        message = "User unauthorized."
    return message

async def ChangeAPIMode(request: Request, response:Response):
    body = await request.json()
    service = body.get("service")
    resource = body.get("resource")
    new_apiMode = body.get("api_mode")
    if service and resource:
        if ValidateServiceExist(service) > 0:
            if ValidateResourceExist(resource) > 0:
                serviceID = GetServiceID(service)
                adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
                if adminRole == 1:
                    if new_apiMode>=0 and new_apiMode<3:
                        requestID = GetResquestID(service, resource)
                        wasAPIModeChanged = ChangeAPIModeUsingRequestID(requestID, new_apiMode)
                        message_id = "CAMT" if new_apiMode== 0 else "CAMR" if new_apiMode== 1 else "CAMM" if new_apiMode == 2 else None
                        mode = "Transparent" if new_apiMode == 0 else "Recording" if new_apiMode == 1 else "Mocking" if new_apiMode == 2 else None
                        if wasAPIModeChanged:
                            log_message = 'User {} has changed the API mode to {}, for {}, {}'.format(username, mode, service, resource)
                            logging.info('%s', log_message)
                            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                            log_time = datetime.fromtimestamp(log_record.created)
                            InsertLogInDatabase(log_time, username, message_id, 'Request', False, serviceID, requestID, '')
                            response.status_code = 200
                            message = "API Mode was changed"
                        else:
                            log_message = 'User {} attempted to change API mode to {}, for {}, {} but something went wrong in the database.'.format(username, mode, service, resource)
                            logging.error('%s', log_message)
                            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                            log_time = datetime.fromtimestamp(log_record.created)
                            InsertLogInDatabase(log_time, username, ('{}, EDB'.format(message_id)), 'Request', True, serviceID, requestID, '' )
                            response.status_code = 500
                            message = "Error changing API Mode"
                    else:
                        response.status_code = 400
                        message = "API Mode should be 0->Transparent, 1->Recording or 2->Mocking."
                else:
                    logging.warning('User %s attempted to change API mode to %s, for %s but this could not be completed for missing permissions over %s.', username, new_apiMode, resource, service)
                    response.status_code = 401
                    message = "User unauthorized."
            else:
                response.status_code = 400
                message = "Provided resource doesn't exist yet."
        else:
            response.status_code = 400
            message = "Provided service doesn't exist yet."
    else:
        response.status_code = 400
        message = "Please provide complete information: service and resource."
    return message

async def DeleteResponseByID(request: Request, response:Response, responseID):
    if ValidateResponseExistByID(uuid.UUID(responseID)) > 0:
        serviceID = GetServiceIDFromResponseID(responseID)
        requestID = GetRequestIDByResponseID(uuid.UUID(responseID))
        adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
        if adminRole == 1:
            if DeleteByResponseID(uuid.UUID(responseID)):
                log_message = 'User {} attempted to delete response {}, for service {}, and the action was complted successfully.'.format(username, responseID, serviceID)
                logging.info('%s', log_message)
                log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                log_time = datetime.fromtimestamp(log_record.created)
                InsertLogInDatabase(log_time, username, 'DRS', "Response", False, serviceID, requestID, '')
                response.status_code = 200
                return "Response deleted successfully."
            else:
                log_message = 'User {} attempted to delete response {}, for service {}, and the action failed on the database.'.format(username, responseID, serviceID)
                logging.warning('%s', log_message)
                log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                log_time = datetime.fromtimestamp(log_record.created)
                InsertLogInDatabase(log_time, username, 'DRS, EDB', "Response", True, serviceID, requestID, '')
                response.status_code = 500
                return "Delete response failed on the database."
        else:
            logging.warning('User %s attempted to delete responses, but this could not be completed for missing admin permissions.', username)
            response.status_code = 400
            return "User unauthorized."
    else:
        response.status_code = 400
        return "Provided response ID doesn't exist yet."

async def DeleteResponses(request: Request, response:Response):
    responsesDeleted = DeleteUncheckedResponses()
    response.status_code = 200
    if responsesDeleted > 0:
        if responsesDeleted == 1:
            word = " Response was deleted"
        else:
            word = " Responses were deleted"
        message = str(responsesDeleted) + word
        logging.info('%s, by SSV admin.', message)
    else:
        logging.warning('There was not any response to delete, by SSV admin.')
    return message


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
            return (1, username)
        elif GetUserAccess(userID, serviceID) != 0:
            return (1, username)
        else:
            return (0, username)

async def ValidateUserRole(request: Request):
    authJSON, authStatus = await Auth(request)
    if authStatus != 200:
        HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"})
        return HTTPException
    else:
        username = authJSON.get('username')
        userID = GetUserID(username)
        if ValidateAdminRole(userID) == 1:
            return 1, username
        else:
            return 0, username

async def Auth(request):
    r = requests.post('http://user_app:8003/sv/user/auth', headers = request.headers)
    return r.json(), r.status_code

async def GetRequests(request: Request, response: Response):
    query_params = request.query_params
    service = query_params.get("service")
    if service:
        if ValidateServiceExist(service) > 0:
            serviceID = GetServiceID(service)
            adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
            if adminRole == 1:
                responses = GetRequestsByServiceID(serviceID)
                if responses is None:
                    response.status_code = 500
                    log_message = 'Failed to retrieve data from database for user {} and service {}.'.format(username, service)
                    logging.error('%s', log_message)
                    log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                    log_time = datetime.fromtimestamp(log_record.created)
                    InsertLogInDatabase(log_time, username, 'GRT, EDB', "Service", True, serviceID, '', '')
                    return "Error getting responses, please check information sent"
                else:
                    response.status_code = 200
                    return responses
            else:
                response.status_code = 401
                return "User unauthorized."
        else:
            response.status_code = 400
            return "Service doesn't exist yet."
    else:
        response.status_code = 400
        return "Service host doesn't provided."

async def AddComment(request, response, responseID):
    body = await request.json()
    comment = body.get('comment')
    if comment and responseID:
        responseExists = ValidateResponseExist(responseID)
        if responseExists == 1:
            requestID = GetRequestIDByResponseID(uuid.UUID(responseID))
            serviceID = GetServiceIDByRequestID(uuid.UUID(requestID))
            service, resource = GetServiceResourceByID(uuid.UUID(serviceID), uuid.UUID(requestID))
            adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
            if adminRole == 1:
                if AddCommentUsingResponseID(comment, responseID):
                    log_message = 'User {} added/updated a comment: {} for {}, {}.'.format(username, comment, service, resource)
                    logging.info('%s', log_message)
                    log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                    log_time = datetime.fromtimestamp(log_record.created)
                    InsertLogInDatabase(log_time, username, 'ACM', "Response", False, serviceID, requestID, responseID)
                    response.status_code = 200
                    message = "Comment added."
                else:
                    log_message = 'User {} attempted to add/update a comment: {} for {}, {}, but could not be completed for database error.'.format(username, comment, service, resource)
                    logging.error('%s', log_message)
                    log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                    log_time = datetime.fromtimestamp(log_record.created)
                    InsertLogInDatabase(log_time, username, 'ACM, EDB', "Response", True, serviceID, requestID, responseID)
                    response.status_code = 500
                    message = "Error adding the comment."
            else:
                response.status_code = 401
                message = "User unauthorized."
        else:
            response.status_code = 400
            message = "The response ID is not valid"
    else:
        response.status_code = 400
        message = "Please provide complete information: comment and responseID."
    return message

async def GetProductsList(request, response):
    authJSON, authStatus = await Auth(request)
    if authStatus == 200:
        username = authJSON.get('username')
        products = GetProducts()
        if len(products) > 0:
            response.status_code = 200
            return products
        else:
            log_message = 'User {} attempted to get the products list, but there are not products in the database.'.format(username)
            logging.error('%s', log_message)
            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
            log_time = datetime.fromtimestamp(log_record.created)
            InsertLogInDatabase(log_time, username, 'GPL, EDB', "Service", True, '00000000-0000-0000-0000-000000000000', '', '')
            response.status_code = 500
            message = "Error getting products, try again."
    else:
        response.status_code = 401
        message = "User unauthorized."
    return message

async def AddResponse(request, response):
    body = await request.json()
    query_params = request.query_params
    payload = body.get("payload")
    request_payload = body.get("request_payload")
    comment = body.get("comment")
    status_code = body.get("status_code")
    service = query_params.get("service")
    resource = query_params.get("resource")
    time_taken = body.get("time")
    headers = body.get("headers")
    if service and resource:
        if payload and request_payload and status_code and headers:
            if ValidateServiceExist(service) > 0:
                if ValidateResourceExist(resource) > 0:
                    serviceID = GetServiceID(service)
                    adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
                    if adminRole == 1:
                        requestID = GetResquestID(service, resource)
                        headers = json.dumps(headers)
                        if xmlValidation(request_payload):
                            request_payload = str(request_payload)
                        else:
                            try:
                                request_payload = json.loads(request_payload)
                                request_payload = json.dumps(request_payload)
                            except:
                                request_payload = str(request_payload)
                        content_type = ContentTypeValidation(headers)
                        if 'json' in content_type:
                            payload = json.dumps(payload)
                        elif 'xml' in content_type or 'text' in content_type:
                            payload = str(payload)
                        if not time_taken:
                            time_taken = 0
                        wasResponseSaved = SaveNewResponse(str(requestID), payload, request_payload, comment, status_code, time_taken, headers)
                        if wasResponseSaved:
                            if SaveResponseStatus(serviceID, requestID, 'accepted', None):
                                log_message = 'User {} added a new response for {}, {}.'.format(username, service, resource)
                                logging.info('%s', log_message)
                                log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                                log_time = datetime.fromtimestamp(log_record.created)
                                InsertLogInDatabase(log_time, username, 'ARS', "Request", False, serviceID, requestID, '')
                                response.status_code = 200
                                message = "Response added."
                        else:
                            log_message = 'User {} attempted to add a new response for {}, {} but the action failed on database.'.format(username, service, resource)
                            logging.error('%s', log_message)
                            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                            log_time = datetime.fromtimestamp(log_record.created)
                            InsertLogInDatabase(log_time, username, 'ARS, EDB', "Request", True, serviceID, requestID, '')
                            response.status_code = 500
                            message = "Error saving the response."
                    else:
                        response.status_code = 401
                        message = "User unauthorized."
                else:
                    response.status_code = 400
                    message = "Provided resource doesn't exist yet."
            else:
                response.status_code = 400
                message = "Provided service doesn't exist yet."
        else:
            response.status_code = 400
            message = "Please provide complete information: payload, request_payload and status_code."
    else:
        response.status_code = 400
        message = "Please provide complete information: service and resource."
    return message

async def SetTrafficAnalyzerStatus(request, response):
    body = await request.json()
    host = body.get('host')
    status = body.get('status')
    if host:
        if ValidateServiceExist(host) > 0:
            serviceID = GetServiceID(host)
            adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
            if adminRole == 1:
                if status == True or status == False:
                    wasStatusChanged = ChangeTrafficAnalyzerStatus(serviceID, status)
                    if wasStatusChanged:
                        nginx_TrafficAnalyzer = requests.post('http://nginx_app:8001/sv/routes/setProxyTrafficAnalyzer', json=body)
                        if nginx_TrafficAnalyzer:
                            log_message = 'User {} changed the Traffic Analyzer status to {} for {}.'.format(username, status, host)
                            logging.info('%s', log_message)
                            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                            log_time = datetime.fromtimestamp(log_record.created)
                            InsertLogInDatabase(log_time, username, 'STA', "Service", False, serviceID, '', '')
                            response.status_code = 200
                            message = "Traffic Analyzer status was changed."
                        else:
                            log_message = 'User {} attempted to change the Traffic Analyzer status to {} for {} but the action failed on nginx.'.format(username, status, host)
                            logging.error('%s', log_message)
                            log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                            log_time = datetime.fromtimestamp(log_record.created)
                            InsertLogInDatabase(log_time, username, 'STA, ENX', "Service", True, serviceID, '', '')
                            response.status_code = 500
                            message = "Error changing the Traffic Analyzer status in the configuration file."
                    else:
                        log_message = 'User {} attempted to change the Traffic Analyzer status to {} for {} but the action failed on database.'.format(username, status, host)
                        logging.error('%s', log_message)
                        log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                        log_time = datetime.fromtimestamp(log_record.created)
                        InsertLogInDatabase(log_time, username, 'STA, EDB', "Service", True, serviceID, '', '')
                        response.status_code = 500
                        message = "Error changing the Traffic Analyzer status in the DB."
                else:
                    response.status_code = 400
                    message = "Status should be true or false."
            else:
                response.status_code = 401
                message = "User unauthorized."
        else:
            response.status_code = 400
            message = "Service doesn't exist yet."
    else:
        response.stattus_code = 400
        message = "Please provide complete information: host and status."
    return message

async def EditResponsePayload(request, response):
    body = await request.json()
    query_params = request.query_params
    responseID = query_params.get('responseID') 
    new_payload = body.get('new_payload')
    if responseID and new_payload:
        responseExists = ValidateResponseExist(responseID)
        if responseExists == 1:
            requestID = GetRequestIDByResponseID(uuid.UUID(responseID))
            serviceID = GetServiceIDByRequestID(uuid.UUID(requestID))
            service, resource = GetServiceResourceByID(uuid.UUID(serviceID), uuid.UUID(requestID))
            adminRole, username = await ValidateAdminOrServiceAccess(request, serviceID)
            if adminRole == 1:
                headers = GetHeadersByResponseID(uuid.UUID(responseID))
                content_type = ContentTypeValidation(headers)
                if 'json' in content_type:
                    new_payload = json.dumps(new_payload)
                elif 'xml' in content_type or 'text' in content_type:
                    new_payload = str(new_payload)
                updateStatus = UpdateResposePayload(uuid.UUID(responseID), new_payload)
                if updateStatus:
                    log_message = 'User {} update the payload for the response {} for {}.'.format(username, responseID, service)
                    logging.info('%s', log_message)
                    log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                    log_time = datetime.fromtimestamp(log_record.created)
                    InsertLogInDatabase(log_time, username, 'ERS', "Response", False, serviceID, requestID, responseID)
                    response.status_code = 200
                    message = "Response updated successfully."
                else:
                    log_message = 'User {} attempted to update the payload for the response {} for {}, but action failed on database.'.format(username, responseID, service)
                    logging.error('%s', log_message)
                    log_record = logging.makeLogRecord({'msg' : log_message, 'args' : None})
                    log_time = datetime.fromtimestamp(log_record.created)
                    InsertLogInDatabase(log_time, username, 'ERS, EDB', "Response", True, serviceID, requestID, responseID)
                    response.status_code = 500
                    message = "Error updating the paylod in the database."
            else:
                response.status_code = 401
                message = "User unauthorized."
        else:
            response.status_code = 400
            message = "Provided response does not exist yet."
    else:
        response.status_code = 400
        message = "Please provide complete information: host, route and new payload."
    return message