from getpass import getuser
from http.client import responses
import time
from urllib import response
import uuid
from wsgiref import headers
from cassandra.cluster import Cluster
from datetime import datetime
from Helpers.TypeValidation import *
cluster = Cluster(contact_points=['cassandradb'])
session = cluster.connect('servicevirtualization')

def GetResquestID(service, resource):
    getServiceIDQuery = session.prepare('SELECT id FROM Service WHERE host = ? ALLOW FILTERING')
    getAllResourcesQuery = session.prepare('SELECT resource FROM Request WHERE service = ? ALLOW FILTERING')
    getRequestIDQuery = session.prepare('SELECT id FROM Request WHERE resource = ? ALLOW FILTERING')
    changeLastAccessQuery = session.prepare('UPDATE Request SET last_access = toTimestamp(now()) WHERE id = ?')
    getServiceIDResult = session.execute(getServiceIDQuery, [service]).one()
    serviceID = getServiceIDResult.id
    getAllResourcesResult = session.execute(getAllResourcesQuery, [str(serviceID)])
    savedResource = ''
    for currentResource in getAllResourcesResult:
        if currentResource.resource in resource:
            savedResource = currentResource.resource
    getRequestIDResult = session.execute(getRequestIDQuery, [savedResource]).one()
    session.execute_async(changeLastAccessQuery, [getRequestIDResult.id])
    return getRequestIDResult.id

def ValidateResourceExist(resource):
    getResourceQuery = session.prepare('SELECT COUNT(*) FROM request WHERE resource = ? Allow FILTERING')
    getResourceResult = session.execute(getResourceQuery, [resource])
    return getResourceResult[0].count

def ValidateResponseExistByID(responseID):
    getResponseQuery = session.prepare('SELECT COUNT(*) FROM response WHERE id = ? Allow FILTERING')
    getResponseResult = session.execute(getResponseQuery, [responseID])
    return getResponseResult[0].count

def ValidateRouteExist(serviceID, resource):
    getRouteQuery = session.prepare('SELECT COUNT(*) FROM request WHERE service = ? AND resource = ? Allow FILTERING')
    getRouteResult = session.execute(getRouteQuery, [str(serviceID), resource])
    return getRouteResult[0].count

def ValidateGetRouteInformation(serviceID, resource):
    getRouteQuery = session.prepare('SELECT COUNT(*) FROM request WHERE service = ? AND resource = ? Allow FILTERING')
    getRouteResult = session.execute(getRouteQuery, [str(serviceID), resource])
    if getRouteResult[0].count > 0:
        getInfromationQuery = session.prepare('SELECT * FROM request WHERE service = ? AND resource = ? Allow FILTERING')
        getInformationResult = session.execute(getInfromationQuery, [str(serviceID), resource]).one()
        return getInformationResult.id, getInformationResult.name, getInformationResult.resource, getInformationResult.method
    else:
        return None, None, None, None

def GetRouteID(serviceID, resource):
    getRouteQuery = session.prepare('SELECT id FROM request WHERE service = ? AND resource = ? Allow FILTERING')
    getRouteResult = session.execute(getRouteQuery, [str(serviceID), resource])
    return getRouteResult[0].id

def GetServiceID(host):
    getServiceIDQuery = session.prepare('SELECT id FROM service WHERE host = ? Allow FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [host]).one()
    return getServiceIDResult.id

def ValidateResourceNameExist(serviceID, name):
    getNameCountQuery = session.prepare('SELECT COUNT (*) FROM request WHERE service = ? AND name = ? Allow FILTERING')
    getNameCountResult = session.execute(getNameCountQuery, [str(serviceID), name])
    return getNameCountResult[0].count

def GetResponsesUsingRequestID(requestID):
    responses = [];
    getResponsesUsingRequestIDQuery = session.prepare('SELECT id, status_code, payload, is_valid, date_created, comment, headers ' 
                                                      'FROM Response WHERE request_id = ? ALLOW FILTERING');
    changeLastAccessQuery = session.prepare('UPDATE Response SET last_access = toTimestamp(now()) WHERE id = ?');
    getResponsesUsingRequestIDResult = session.execute(getResponsesUsingRequestIDQuery, [str(requestID)])
    for currentResponse in getResponsesUsingRequestIDResult:
        responses.append({
            "id": currentResponse.id,
            "date_created": currentResponse.date_created,
            "status_code": currentResponse.status_code,
            "payload": currentResponse.payload,
            "comment": currentResponse.comment,
            "is_valid": currentResponse.is_valid,
            "content_type": ContentTypeValidation(currentResponse.headers)
        })
        try:
            session.execute(changeLastAccessQuery, [currentResponse.id])
        except :
            pass
    return responses

def AcceptResponseUsingResponseID(responseID):
    changeIsValidUsingResponseIDQuery = session.prepare('UPDATE Response SET is_valid = true ,' 
                                                        'last_update = toTimestamp(now()) WHERE id = ?')
    try:
        session.execute(changeIsValidUsingResponseIDQuery, [responseID])
    except :
        return False
    return True

def GetResponseStatus(responseID):
    getResponseStatusQuery = session.prepare('SELECT is_valid FROM response WHERE id = ? Allow FILTERING')
    getResponseStatusResult = session.execute(getResponseStatusQuery, [responseID]).one()
    if getResponseStatusResult.is_valid == True:
        return 'accepted'
    elif getResponseStatusResult.is_valid == False:
        return 'rejected'
    else:
        return 'not_validated'

def RejectResponseUsingResponseID(responseID):
    changeIsValidUsingResponseIDQuery = session.prepare('UPDATE Response SET is_valid = false ,' 
                                                        'last_update = toTimestamp(now()) WHERE id = ?')
    try:
        session.execute(changeIsValidUsingResponseIDQuery, [responseID])
    except :
        return False
    return True

def SaveNewRequest(serviceID, route, method, name):
    createNewRequestQuery = session.prepare('INSERT INTO Request (id, service, resource, method, api_mode, name,'
                                            'date_created, last_update, last_access, time_saved)'
                                            'VALUES(uuid(), ?, ?, ?, ?, ?, toTimestamp(now()), toTimestamp(now()), toTimestamp(now()), 0)')
    try:
        session.execute(createNewRequestQuery, [str(serviceID), route, method, 0, name])
    except :
        return False
    return True

def SaveNewService(host, name, actual_ip, port, portfolio, region, hostname):
    createNewServiceQuery = session.prepare('INSERT INTO Service' 
                                                '(id, host, name, actual_ip, port, portfolio, region, host_name, date_created, last_update, last_access)' 
                                                'VALUES (uuid(), ?, ?, ?, ?, ?, ?, ?, toTimestamp(now()), toTimestamp(now()), toTimestamp(now()))')
    try:
        session.execute(createNewServiceQuery, [host, name, actual_ip, port, portfolio, region, hostname])
    except:
        return False
    return True

def ValidateRouteNameExist(serviceID, name):
    routeNameQuery = session.prepare('SELECT COUNT (*) FROM request WHERE service = ? AND name = ? Allow FILTERING')
    routeNameResult = session.execute(routeNameQuery, [str(serviceID), name])
    return routeNameResult[0].count

def UpdateService(serviceID, host, name, actual_ip, port):
    if host:
        editHostQuery = session.prepare('UPDATE service SET host = ? WHERE id = ?')
        session.execute(editHostQuery, [host, serviceID])
    if name:
        editNameQuery = session.prepare('UPDATE service SET name = ? WHERE id = ?')
        session.execute(editNameQuery, [name, serviceID])
    if actual_ip:
        editIPQuery = session.prepare('UPDATE service SET actual_ip = ? WHERE id = ?')
        session.execute(editIPQuery, [actual_ip, serviceID])
    if port:
        editPortQuery = session.prepare('UPDATE service SET port = ? WHERE id = ?')
        session.execute(editPortQuery, [port, serviceID])

def UpdateRoute(resourceID, route, method, name):
    if route:
        editRouteQuery = session.prepare('UPDATE request SET resource = ? WHERE id = ?')
        session.execute(editRouteQuery, [route, resourceID])
    if method:
        editMethodQuery = session.prepare('UPDATE request SET method = ? WHERE id = ?')
        session.execute(editMethodQuery, [method, resourceID])
    if name:
        editNameQuery = session.prepare('UPDATE request SET name = ? WHERE id = ?')
        session.execute(editNameQuery, [name, resourceID])

def DeleteAllResponsesAndResourceByID(resourceID):
    getAllResponsesQuery = session.prepare('SELECT id FROM response WHERE request_id = ? Allow FILTERING')
    getAllResponsesResult = session.execute(getAllResponsesQuery, [str(resourceID)])
    deleteResponseQuery = session.prepare('DELETE FROM response WHERE id = ?')
    for currentResponse in getAllResponsesResult:
        try:
            session.execute(deleteResponseQuery, [currentResponse.id])
        except:
            return False
    deleteResourceQuery = session.prepare('DELETE FROM request WHERE id = ?')
    try:
        session.execute(deleteResourceQuery, [resourceID])
    except:
        return False
    return True

def DeleteServiceDB(serviceID):
    getAllResourcesQuery = session.prepare('SELECT id FROM request WHERE service = ? Allow FILTERING')
    getAllResourcesResult = session.execute(getAllResourcesQuery, [str(serviceID)])
    for currentResource in getAllResourcesResult:
        try:
            DeleteAllResponsesAndResourceByID(currentResource.id)
        except:
            return False
    deleteServiceQuery = session.prepare('DELETE FROM service WHERE id = ?')
    try:
        session.execute(deleteServiceQuery, [serviceID])
    except:
        return False
    getServiceQuery = session.prepare('Select id FROM userservice WHERE service = ? Allow FILTERING')
    deleteUserPermissionQuery = session.prepare('DELETE FROM userservice WHERE id = ?')
    getServiceResult = session.execute(getServiceQuery, [str(serviceID)])
    for service in getServiceResult:
        try:
            session.execute(deleteUserPermissionQuery, [uuid.UUID(str(service.id))])
        except:
            return False
    return True

def ChangeAPIModeUsingRequestID(requestID, apiMode):
    changeAPIModeUsingResponseIDQuery = session.prepare('UPDATE Request SET api_mode = ? ,' 
                                                        'last_update = toTimestamp(now()) WHERE id = ?')
    try:
        session.execute(changeAPIModeUsingResponseIDQuery, [apiMode, requestID])
    except :
        return False
    return True

def DeleteUncheckedResponses():
    responsesDeleted = 0;
    getAllUncheckedResponsesQuery = session.prepare('SELECT id FROM ServiceVirtualization.Response '
                                                    'WHERE is_valid = false ALLOW FILTERING')
    deleteResponseUsingIDQuery = session.prepare('DELETE FROM Response WHERE id = ?')
    getAllUncheckedResponsesResult = session.execute(getAllUncheckedResponsesQuery)
    for currentResponse in getAllUncheckedResponsesResult:
        try:
            session.execute(deleteResponseUsingIDQuery, [currentResponse.id])
            responsesDeleted = responsesDeleted + 1
        except :
            pass
    return responsesDeleted

def DeleteByResponseID(responseID):
    deleteResponseQuery = session.prepare('DELETE FROM response WHERE id = ?')
    try:
        session.execute(deleteResponseQuery, [responseID])
    except :
        return False
    return True

def GetServiceID(host):
    getServiceIDQuery = session.prepare('SELECT id FROM service WHERE host = ? Allow FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [host]).one()
    return getServiceIDResult.id

def GetServiceResourceByID(serviceID, resourceID):
    getServiceQuery = session.prepare('SELECT name FROM service WHERE id = ? Allow FILTERING')
    getServiceResult = session.execute(getServiceQuery, [serviceID]).one()
    getResourceQuery = session.prepare('SELECT name FROM request WHERE id = ? Allow FILTERING')
    getResourceResult = session.execute(getResourceQuery, [resourceID]).one()
    return getServiceResult.name, getResourceResult.name

def GetServiceNameByHost(host):
    getServiceQuery = session.prepare('SELECT name FROM service WHERE host = ? Allow FILTERING')
    getServiceResult = session.execute(getServiceQuery, [host]).one()
    return getServiceResult.name

def GetServiceIDFromResponseID(responseID):
    requestID = GetRequestIDByResponseID(uuid.UUID(responseID))
    return GetServiceIDByRequestID(uuid.UUID(requestID))

def GetRequestIDByResponseID(responseID):
    getRequestIDQuery = session.prepare('SELECT request_id FROM response WHERE id = ? Allow FILTERING')
    getRequestIDResult = session.execute(getRequestIDQuery, [responseID]).one()
    return getRequestIDResult.request_id

def GetServiceIDByRequestID(requestID):
    getServiceIDQuery = session.prepare('SELECT service FROM request WHERE id = ? Allow FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [requestID]).one()
    return getServiceIDResult.service

def ValidateServiceExist(host):
    getServiceCountQuery = session.prepare('SELECT COUNT(*) FROM service WHERE host = ? Allow FILTERING')
    getServiceCountResult = session.execute(getServiceCountQuery, [host])
    return getServiceCountResult[0].count

def ValidateGetServiceInfromation(host):
    getServiceCountQuery = session.prepare('SELECT COUNT(*) FROM service WHERE host = ? Allow FILTERING')
    getServiceCountResult = session.execute(getServiceCountQuery, [host])
    if getServiceCountResult[0].count > 0:
        getServiceInfromationQuery = session.prepare('SELECT * FROM service WHERE host = ? Allow FILTERING')
        getServiceInfromationResult = session.execute(getServiceInfromationQuery, [host]).one()
        return getServiceInfromationResult.id, getServiceInfromationResult.name, getServiceInfromationResult.host, getServiceInfromationResult.actual_ip, getServiceInfromationResult.port
    else:
        return None, None, None, None, None

def GetUserAccess(userID, serviceID):
    getUserAccessQuery = session.prepare('SELECT COUNT(*) FROM userservice WHERE user = ? AND service = ? Allow FILTERING')
    getuserAccessResult = session.execute(getUserAccessQuery, [str(userID), str(serviceID)])
    return getuserAccessResult[0].count

def GetRequestsByServiceID(serviceID):
    responses = [];
    getRequestsQuery = session.prepare('SELECT * FROM request WHERE service = ? Allow FILTERING')
    changeLastAccessQuery = session.prepare('UPDATE request SET last_access = toTimestamp(now()) WHERE id = ?');
    getRequestsResult = session.execute(getRequestsQuery, [str(serviceID)])
    for currentRequest in getRequestsResult:
        responses.append({
            "id": currentRequest.id,
            "name": currentRequest.name,
            "service": currentRequest.service,
            "resource": currentRequest.resource,
            "method": currentRequest.method,
            "API mode": currentRequest.api_mode,
            "Date Created": currentRequest.date_created,
            "Last Update": currentRequest.last_update,
            "Last Access": currentRequest.last_access,
            "Is Recorded": currentRequest.is_recorded
            })
        try:
            session.execute(changeLastAccessQuery, [currentRequest.id])
        except:
            pass
    return responses

def GetUserID(username):
    userIDQuery = session.prepare("SELECT id FROM user WHERE name = ? Allow FILTERING")
    userIDResult = session.execute(userIDQuery, [username]).one()
    return userIDResult.id

def ValidateAdminRole(userID):
    adminRoleQuery = session.prepare("SELECT role FROM user WHERE id = ? Allow FILTERING")
    adminRoleResult= session.execute(adminRoleQuery, [userID]).one()
    if "admin" in adminRoleResult:
        return 1
    else:
        return 0

def ValidateResponseExist(responseID):
    getRespoonseCountQuery = session.prepare('SELECT COUNT(*) FROM response WHERE id = ?')
    getResponseCountResult = session.execute(getRespoonseCountQuery, [uuid.UUID(responseID)])
    return getResponseCountResult[0].count

def AddCommentUsingResponseID(comment, responseID):
    changeIsValidUsingResponseIDQuery = session.prepare('UPDATE Response SET comment = ? ,' 
                                                        'last_update = toTimestamp(now()) WHERE id = ?')
    try:
        session.execute(changeIsValidUsingResponseIDQuery, [comment, uuid.UUID(responseID)])
    except :
        return False
    return True

def GetProducts():
    products = [];
    getProductsQuery = session.prepare('SELECT * FROM products')
    getProductsResult = session.execute(getProductsQuery)
    for product in getProductsResult:
        products.append({
                "id": product.id,
                "name": product.name
            })
    return products

def SaveNewResponse(requestID, payload, request_payload, comment, status_code, time_taken, headers):
    createNewResponseQuery = session.prepare('INSERT INTO Response (id, request_id, payload, request_payload, status_code, is_valid, date_created, last_update, last_access, comment, time_taken, headers)' 
                                            'VALUES(uuid(), ?, ?, ?, ?, true, toTimestamp(now()), toTimestamp(now()), toTimestamp(now()), ?, ?, ?)')
    if not time_taken:
        time_taken = 1
    try:
         session.execute(createNewResponseQuery, [str(requestID), payload, request_payload, status_code, comment, time_taken, headers])
    except :
         return False
    return True

def ChangeTrafficAnalyzerStatus(serviceID, status):
    changeTrafficAnalyzerStatusQuery = session.prepare('UPDATE service SET is_trafficAnalyzer = ? WHERE id = ?')
    try:
        session.execute(changeTrafficAnalyzerStatusQuery, [status, serviceID])
    except :
        return False
    return True

def UpdateResposePayload(responseID, new_payload):
    updateResponseQuery = session.prepare('UPDATE response SET payload = ? WHERE id = ?')
    try:
        session.execute(updateResponseQuery, [new_payload, responseID])
    except:
        return False
    return True

def GetHeadersByResponseID(responseID):
    getHeadersQuery = session.prepare('SELECT headers FROM response WHERE id = ?')
    getHeadersResult = session.execute(getHeadersQuery, [responseID]).one()
    return getHeadersResult.headers

def SaveResponseStatus(service, resource, responseType, previousType):
    # Getting current date and formatting to 'YYYY-MM-DD'
    currentDate = datetime.now()  
    day = currentDate.strftime("%Y-%m-%d")
    # Check if there is a register for today
    isRegisterForTodayQuery = session.prepare("SELECT COUNT(*), accepted, rejected, not_validated FROM lastresponses WHERE service = ? AND resource = ? ALLOW FILTERING")
    isRegisterForToday = session.execute(isRegisterForTodayQuery, [str(service), str(resource)])
    if isRegisterForToday[0].count > 0:
        # If there is a register for today then we get the actual number of responses in each status
        actualAcceptedValue = int(isRegisterForToday[0].accepted)
        actualRejectedValue = int(isRegisterForToday[0].rejected)
        actualNotValidatedValue = int(isRegisterForToday[0].not_validated)
        getLastResponseIdQuery =  session.prepare("SELECT id FROM lastresponses WHERE service = ? AND resource = ? ALLOW FILTERING")
        lastResponseId = session.execute(getLastResponseIdQuery, [str(service), str(resource)]).one().id
        # Preparing query to update the values in te specific record for today.
        updateLastResponseQuery = session.prepare('UPDATE lastresponses SET accepted = ?, rejected = ?, not_validated = ? WHERE id = ?')
        # Updating the value of the number of transactions depending on the transation API mode.
        if previousType is not None:
            if previousType == 'accepted':
                actualAcceptedValue = actualAcceptedValue - 1
            elif previousType == 'rejected':
                actualRejectedValue = actualRejectedValue - 1
            elif previousType == 'not_validated':
                actualNotValidatedValue = actualNotValidatedValue - 1
        if responseType == 'accepted':
            actualAcceptedValue = actualAcceptedValue + 1
        elif responseType == 'rejected':
            actualRejectedValue = actualRejectedValue + 1
        elif responseType == 'not_validated':
            actualNotValidatedValue = actualNotValidatedValue + 1
        try:
            # Update values.
            session.execute(updateLastResponseQuery, [actualAcceptedValue, actualRejectedValue, actualNotValidatedValue ,lastResponseId])
        except:
            return False
    else:
        # Id there is no record for today then we insert a new one.
        createLastResponseQuery = session.prepare('INSERT INTO lastresponses (id, service, resource, accepted, rejected, not_validated, transaction_date) VALUES (uuid(), ?, ?, ?, ?, ?, ?)')
        try: 
            if responseType == 'accepted':
                session.execute(createLastResponseQuery, [str(service), str(resource), 1, 0, 0, day])
            elif responseType == 'rejected':
                session.execute(createLastResponseQuery, [str(service), str(resource), 0, 1, 0, day])
            elif responseType == 'not_validated':
                session.execute(createLastResponseQuery, [str(service), str(resource), 0, 0, 1, day])
        except:
            return False
    return True

def GetServiceIDByHost(host):
    getServiceIDQuery = session.prepare('SELECT COUNT(*) FROM service WHERE host = ? Allow FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [host]).one()
    if getServiceIDResult.count == 0:
        return False
    else:
        getServiceIDQuery = session.prepare('SELECT id FROM service WHERE host = ? Allow FILTERING')
        getServiceIDResult = session.execute(getServiceIDQuery, [host]).one()
        return getServiceIDResult.id