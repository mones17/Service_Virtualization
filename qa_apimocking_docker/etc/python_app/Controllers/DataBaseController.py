from datetime import datetime
from email import header
import time
from urllib import request
from cassandra.cluster import Cluster
import json
from Helpers.CalculateSimilirity import calculate_similarity
import xmltodict

cluster = Cluster(contact_points=['cassandradb'])
session = cluster.connect('servicevirtualization')

def GetRequestID(service, resource):
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

def GetServiceID(service):
    getServiceIDQuery = session.prepare('SELECT id FROM Service WHERE host = ? ALLOW FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [service]).one()
    return getServiceIDResult.id

def CreateIfRequestDoesNotExist(service, resource, method):
    getServiceIDQuery = session.prepare('SELECT id FROM Service WHERE host = ? ALLOW FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [service]).one()
    getRequestIDQuery = session.prepare('SELECT COUNT (*) FROM Request WHERE service = ? AND resource = ? ALLOW FILTERING')
    getRequestIDResult = session.execute(getRequestIDQuery, [str(getServiceIDResult.id), resource])
    if getRequestIDResult[0].count == 0:
        insertRequestQuery = session.prepare('INSERT INTO Request(id, service, resource, name, date_created, last_update, last_access, time_saved, api_mode, is_recorded, method) '
                                             'VALUES (uuid(), ?, ?, ?, toTimestamp(now()), toTimestamp(now()), toTimestamp(now()), 0, 0, True, ?)')
        session.execute(insertRequestQuery, [str(getServiceIDResult.id), resource, resource, method])

def IsTrafficAnalyzerMode(service):
    getTrafficModeQuery = session.prepare('SELECT is_trafficanalyzer FROM service WHERE host = ? ALLOW FILTERING')
    getTrafficModeResult = session.execute(getTrafficModeQuery, [service]).one()
    return getTrafficModeResult.is_trafficanalyzer

async def SaveResponse(requestID, response, request_payload, time_taken):
    try:
        headers_dict = dict(response.headers)
        headers = json.dumps(headers_dict)
        payload = response.content.decode('utf-8')
        statusCode = response.status_code
    except Exception as e:
        print('Error Saving Response:', str(e))
        return None
    request_payload_json = None
    if(request_payload is not None):
        try:
            request_payload_json = json.dumps(request_payload)
        except Exception as e:
            print('Error Converting Request Payload to JSON:', str(e))
            request_payload_json = None
    insertResponseQuery = session.prepare('INSERT INTO Response(id, request_id, status_code, headers, payload, request_payload, date_created,' 
                                              'last_update, last_access, time_taken) VALUES (uuid(), ?, ?, ?, ?, ?, toTimestamp(now()), toTimestamp(now()),' 
                                              'toTimestamp(now()), ?)')
    try:
        session.execute(insertResponseQuery, [str(requestID), str(statusCode), headers, payload, request_payload_json, int(time_taken)])
    except Exception as e:
        print('Error Saving Response:', str(e))

async def GetResponse(requestID, request_payload):
    start_time = time.time()
    getResponseQuery = session.prepare('SELECT id, status_code, payload, request_payload, time_taken, last_access, headers FROM Response WHERE request_id=? AND is_valid=true ALLOW FILTERING')
    changeLastAccessQuery = session.prepare('UPDATE Response SET last_access = toTimestamp(now()) WHERE id = ?')
    getResponseResult = session.execute(getResponseQuery, [str(requestID)])
    if len(getResponseResult.current_rows) == 0:
        return None, None, None
    max_similarity = -1
    most_similar_json = None
    for response in getResponseResult:
        if (response.request_payload is not None):
            print(f"target_json type: {type(request_payload)}, actual_json type: {type(response.request_payload)}")
            similarity = calculate_similarity(request_payload, json.loads(response.request_payload))
            print(f"target_json type: {type(request_payload)}, actual_json type: {type(response.request_payload)}")
        else:
            similarity = 0
        if similarity == max_similarity:
            # If the similarity is equal, compare the dates (last_update) and update most_similar_json if the date is older
            if response.last_access < most_similar_json.last_access:
                most_similar_json = response
        elif similarity > max_similarity:
            max_similarity = similarity
            most_similar_json = response
    if 'application/xml' in most_similar_json.headers:
        body = json.loads(most_similar_json.payload)
        body = xmltodict.unparse(body, pretty=True)
    elif 'application/json' in most_similar_json.headers:
        body = json.loads(most_similar_json.payload)
    else:
        body = most_similar_json.payload
    headers = most_similar_json.headers
    json_headers = json.loads(headers)
    try:
        content_type = json_headers['Content-Type']
    except:
        content_type = json_headers['content-type']
    status_code = int(most_similar_json.status_code)
    request_time_taken = most_similar_json.time_taken
    finish_time = time.time()
    time_taken = finish_time - start_time
    UpdateSavedTime(requestID, request_time_taken - time_taken)
    session.execute_async(changeLastAccessQuery, [most_similar_json.id])
    return body, status_code, content_type

def UpdateSavedTime(requestID, time_taken):
    getActualTimeSavedQuery = session.prepare('SELECT time_saved from Request WHERE id = ?')
    updateTimeSavedQuery = session.prepare('UPDATE Request SET time_saved = ? WHERE id = ?')
    getActualTimeSavedResult = session.execute(getActualTimeSavedQuery, [requestID]).one()
    new_time_saved = time_taken + getActualTimeSavedResult.time_saved
    session.execute(updateTimeSavedQuery, [int(new_time_saved), requestID])
    
def GetAPIModeUsingRequestID(requestID):
    getAPIModeQuery = session.prepare('SELECT api_mode FROM Request WHERE id = ? ALLOW FILTERING')
    changeLastAccessQuery = session.prepare('UPDATE Request SET last_access = toTimestamp(now()) WHERE id = ?')
    getAPIModeResult = session.execute(getAPIModeQuery, [requestID]).one()
    session.execute_async(changeLastAccessQuery, [requestID])
    return getAPIModeResult.api_mode

def InsertLogInDatabase(dateCreated, user, message, levelAffected, isError, serviceId, requestId, responseId):
    logValuesQuery = session.prepare("INSERT INTO logs (id, date_created, user, message, level_affected, is_error, service_id, request_id, response_id) VALUES (uuid(), ?, ?, ?, ?, ?, ?, ?, ?)")
    logValuesResult = session.execute(logValuesQuery, [dateCreated, user, message, levelAffected, isError, str(serviceId), str(requestId), str(responseId)])
    
def SaveLastResourceTransaction(service, resource, transactionType):
    # Getting current date and formatting to 'YYYY-MM-DD'
    currentDate = datetime.now()  
    day = currentDate.strftime("%Y-%m-%d")
    # Check if there is a register for today
    isRegisterForTodayQuery = session.prepare("SELECT COUNT(*), transparent, recording, mocking FROM lastresourcestransactions WHERE service = ? AND resource = ? AND transaction_date = ? ALLOW FILTERING")
    isRegisterForToday = session.execute(isRegisterForTodayQuery, [str(service), str(resource), day])
    if isRegisterForToday[0].count > 0:
        # If there is a register for today then we get the actual number of transactions in each API Mode
        actualTransparentValue = int(isRegisterForToday[0].transparent)
        actualRecordingValue = int(isRegisterForToday[0].recording)
        actualMockingValue = int(isRegisterForToday[0].mocking)
        # We need the ID for the record for today so then we can update the number of transactions.
        getLastResourceIdQuery =  session.prepare("SELECT id FROM lastresourcestransactions WHERE service = ? AND resource = ? AND transaction_date = ? ALLOW FILTERING")
        lastResourceId = session.execute(getLastResourceIdQuery, [str(service), str(resource), day]).one().id
        # Preparing query to update the values in te specific record for today.
        updateLastResourceQuery = session.prepare('UPDATE lastresourcestransactions SET transparent = ?, recording = ?, mocking = ? WHERE id = ?')
        # Updating the value of the number of transactions depending on the transation API mode.
        if transactionType == 'transparent':
            actualTransparentValue = actualTransparentValue + 1
        elif transactionType == 'recording':
            actualRecordingValue = actualRecordingValue + 1
        elif transactionType == 'mocking':
            actualMockingValue = actualMockingValue + 1
        try:
            # Update values.
            session.execute(updateLastResourceQuery, [actualTransparentValue, actualRecordingValue, actualMockingValue ,lastResourceId])
        except:
            return False
    else:
        # Id there is no record for today then we insert a new one.
        createLastResourceQuery = session.prepare('INSERT INTO lastresourcestransactions (id, service, resource, transparent, recording, mocking, transaction_date) VALUES (uuid(), ?, ?, ?, ?, ?, ?)')
        try: 
            if transactionType == 'transparent':
                session.execute(createLastResourceQuery, [str(service), str(resource), 1, 0, 0, day])
            elif transactionType == 'recording':
                session.execute(createLastResourceQuery, [str(service), str(resource), 0, 1, 0, day])
            elif transactionType == 'mocking':
                session.execute(createLastResourceQuery, [str(service), str(resource), 0, 0, 1, day])
        except:
            return False
    return True

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