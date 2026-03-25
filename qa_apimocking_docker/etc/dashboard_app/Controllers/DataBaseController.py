from curses import qiflush
from datetime import datetime, timedelta
from email import message
from urllib import request
from requests import get
from cassandra.cluster import Cluster
from jose import jwt, JWTError
import uuid
from cassandra.concurrent import execute_concurrent, execute_concurrent_with_args
import asyncio

cluster = Cluster(contact_points=['cassandradb'])
session = cluster.connect('servicevirtualization')

def ValidateAdminRole(userID):
    adminRoleQuery = session.prepare("SELECT role FROM user WHERE id = ? Allow FILTERING")
    adminRoleResult= session.execute(adminRoleQuery, [userID]).one()
    if "admin" in adminRoleResult:
        return 1
    else:
        return 0
    
def GetServiceID(name):
    getServiceIDQuery = session.prepare('SELECT COUNT(*) FROM service WHERE name = ? Allow FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [name]).one()
    if getServiceIDResult.count == 0:
        return False
    else:
        getServiceIDQuery = session.prepare('SELECT id FROM service WHERE name = ? Allow FILTERING')
        getServiceIDResult = session.execute(getServiceIDQuery, [name]).one()
        return getServiceIDResult.id
    
def GetServiceIDByHost(host):
    getServiceIDQuery = session.prepare('SELECT COUNT(*) FROM service WHERE host = ? Allow FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [host]).one()
    if getServiceIDResult.count == 0:
        return False
    else:
        getServiceIDQuery = session.prepare('SELECT id FROM service WHERE host = ? Allow FILTERING')
        getServiceIDResult = session.execute(getServiceIDQuery, [host]).one()
        return getServiceIDResult.id

def ValidateServiceExist(name):
    getServiceIDQuery = session.prepare('SELECT COUNT(*) FROM service WHERE name = ? Allow FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [name]).one()
    if getServiceIDResult.count == 0:
        return False
    else:
        return True
    
def GetUserAccess(userID, serviceID):
    getUserAccessQuery = session.prepare('SELECT COUNT(*) FROM userservice WHERE user = ? AND service = ? Allow FILTERING')
    getuserAccessResult = session.execute(getUserAccessQuery, [str(userID), str(serviceID)])
    return getuserAccessResult[0].count

def GetUserID(username):
    userIDQuery = session.prepare("SELECT id FROM user WHERE name = ? Allow FILTERING")
    userIDResult = session.execute(userIDQuery, [username]).one()
    return userIDResult.id

def GetHostByName(name):
    getHostQuery = session.prepare("SELECT host FROM service WHERE name = ? Allow FILTERING")
    getHostResult = session.execute(getHostQuery, [name]).one()
    return getHostResult.host

def GetAllTimeSaved(userID, role):
    if role == 'admin':
        getAllTimeSavedQuery = session.prepare('SELECT SUM(time_saved) AS total_time_saved FROM request')
        try:
            time_saved = 0
            time_saved_result = session.execute(getAllTimeSavedQuery)
            time_saved = time_saved_result[0].total_time_saved
            hours = time_saved // 3600
            time_saved = time_saved - (hours * 3600)
            minutes = time_saved // 60
            time_saved = time_saved - (minutes * 60)
            seconds = time_saved
            total_time = {
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds
            }
            return total_time
        except:
            return None
    elif role == 'user':
        getServiceDataQuery = session.prepare('SELECT service FROM userservice WHERE user = ? Allow FILTERING')
        try:
            time_saved = 0
            getServiceDataResult = session.execute(getServiceDataQuery) if role == 'admin' else session.execute(getServiceDataQuery, [str(userID)])
            for serviceID in getServiceDataResult:
                getResourcesQuery = session.prepare('SELECT id FROM request WHERE service = ? Allow FILTERING')
                getResourcesResult = session.execute(getResourcesQuery, [str(serviceID.id)]) if role == 'admin' else session.execute(getResourcesQuery, [str(serviceID.service)])
                for resourceID in getResourcesResult:
                    getTimeSavedQuery = session.prepare('SELECT time_saved FROM request WHERE id = ? Allow FILTERING')
                    getTimeSavedResult = session.execute(getTimeSavedQuery, [resourceID.id])
                    time_saved = time_saved + getTimeSavedResult[0].time_saved
            hours = time_saved // 3600
            time_saved = time_saved - (hours * 3600)
            minutes = time_saved // 60
            time_saved = time_saved - (minutes * 60)
            seconds = time_saved
            total_time = {
                "hours": hours,
                "minutes": minutes,
                "seconds": seconds
            }
            return total_time
        except:
            return None

def ResourceExists(serviceID, resourceName):
    getResourceIDQuery = session.prepare('SELECT COUNT(*) FROM request WHERE service = ? AND name = ? Allow FILTERING')
    getResourceIDResult = session.execute(getResourceIDQuery, [str(serviceID), resourceName])
    if getResourceIDResult[0].count == 0:
        return False
    else:
        return True

def GetTimeSaved(serviceHost, resource):
    if serviceHost and not resource:
        getServiceIDQuery = session.prepare('SELECT id FROM service WHERE host = ? Allow FILTERING')
        getServiceIDResult = session.execute(getServiceIDQuery, [serviceHost]).one()
        serviceID = getServiceIDResult.id
        getResourcesQuery = session.prepare('SELECT id FROM request WHERE service = ? Allow FILTERING')
        getResourcesResult = session.execute(getResourcesQuery, [str(serviceID)])
    elif serviceHost and resource:
        getServiceIDQuery = session.prepare('SELECT id FROM service WHERE host = ? Allow FILTERING')
        getServiceIDResult = session.execute(getServiceIDQuery, [serviceHost]).one()
        serviceID = getServiceIDResult.id
        getResourcesQuery = session.prepare('SELECT id FROM request WHERE service = ? AND name = ? Allow FILTERING')
        getResourcesResult = session.execute(getResourcesQuery, [str(serviceID), resource])
    try:
        time_saved = 0
        for resourceID in getResourcesResult:
            getTimeSavedQuery = session.prepare('SELECT time_saved FROM request WHERE id = ? Allow FILTERING')
            getTimeSavedResult = session.execute(getTimeSavedQuery, [resourceID.id])
            time_saved = time_saved + getTimeSavedResult[0].time_saved
        hours = time_saved // 3600
        time_saved = time_saved - (hours * 3600)
        minutes = time_saved // 60
        time_saved = time_saved - (minutes * 60)
        seconds = time_saved
        total_time = {
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds
        }
        return total_time
    except:
        return None
    
def GetAllAPITransactions(userID, role):
    responses = [];
    if role == 'admin':
        getTransparentCountQuery = session.prepare('SELECT SUM(transparent) FROM lastresourcestransactions WHERE transaction_date = ? Allow FILTERING')
        getRecordingCountQuery = session.prepare('SELECT SUM(recording) FROM lastresourcestransactions WHERE transaction_date = ? Allow FILTERING')
        getMockingCountQuery = session.prepare('SELECT SUM(mocking) FROM lastresourcestransactions WHERE transaction_date = ? Allow FILTERING')
        today = datetime.now()
        try:
            for i in range(6, -1, -1):
                currentDate = today - timedelta(days=i)
                day = currentDate.strftime("%Y-%m-%d")
                getTransparentCountsResult = session.execute(getTransparentCountQuery, [day])
                getRecordingCountsResult = session.execute(getRecordingCountQuery, [day])
                getMockingCountsResult = session.execute(getMockingCountQuery, [day])
                responses.append({
                    "name": day,
                    "transparent": getTransparentCountsResult.one()[0],
                    "recording": getRecordingCountsResult.one()[0],
                    "mocking": getMockingCountsResult.one()[0]
                    })
            return responses
        except:
            return None
    elif role == 'user':
        getServiceDataQuery = session.prepare('SELECT service FROM userservice WHERE user = ? Allow FILTERING')
        getTransparentCountQuery = session.prepare('SELECT SUM(transparent) FROM lastresourcestransactions WHERE service = ? AND transaction_date = ? Allow FILTERING')
        getRecordingCountQuery = session.prepare('SELECT SUM(recording) FROM lastresourcestransactions WHERE service = ? AND transaction_date = ? Allow FILTERING')
        getMockingCountQuery = session.prepare('SELECT SUM(mocking) FROM lastresourcestransactions WHERE service = ? AND transaction_date = ?Allow FILTERING')
        today = datetime.now()
        try:
            for i in range(6, -1, -1):
                transparentCount = 0
                recordingCount = 0
                mockingCount = 0
                currentDate = today - timedelta(days=i)
                day = currentDate.strftime("%Y-%m-%d")
                getServiceDataResult = session.execute(getServiceDataQuery, [str(userID)])
                for serviceID in getServiceDataResult:
                    getTransparentCountsResult = session.execute(getTransparentCountQuery, [serviceID.service, day])
                    transparentCount += getTransparentCountsResult.one()[0]
                    getRecordingCountsResult = session.execute(getRecordingCountQuery, [serviceID.service, day])
                    recordingCount += getRecordingCountsResult.one()[0]
                    getMockingCountsResult = session.execute(getMockingCountQuery, [serviceID.service, day])
                    mockingCount += getMockingCountsResult.one()[0]
                responses.append({
                    "name": day,
                    "transparent": transparentCount,
                    "recording": recordingCount,
                    "mocking": mockingCount
                })
            return responses
        except:
            return None
            
  
def GetAPITransactions(serviceHost, resource):
    responses = [];
    getServiceIDQuery = session.prepare('SELECT id FROM service WHERE host = ? Allow FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [serviceHost]).one()
    serviceID = getServiceIDResult.id
    if serviceHost and not resource:
        getTransparentCountQuery = session.prepare('SELECT SUM(transparent) FROM lastresourcestransactions WHERE service = ? AND transaction_date = ? Allow FILTERING')
        getRecordingCountQuery = session.prepare('SELECT SUM(recording) FROM lastresourcestransactions WHERE service = ? AND transaction_date = ? Allow FILTERING')
        getMockingCountQuery = session.prepare('SELECT SUM(mocking) FROM lastresourcestransactions WHERE service = ? AND transaction_date = ? Allow FILTERING')
    elif serviceHost and resource:
        getResourceIDQuery = session.prepare('SELECT id FROM request WHERE service = ? AND name = ? Allow FILTERING')
        getResourceIDResult = session.execute(getResourceIDQuery, [str(serviceID), resource]).one()
        resourceID = getResourceIDResult.id
        getTransparentCountQuery = session.prepare('SELECT SUM(transparent) FROM lastresourcestransactions WHERE service = ? AND resource = ? AND transaction_date = ? Allow FILTERING')
        getRecordingCountQuery = session.prepare('SELECT SUM(recording) FROM lastresourcestransactions WHERE service = ? AND resource = ? AND transaction_date = ? Allow FILTERING')
        getMockingCountQuery = session.prepare('SELECT SUM(mocking) FROM lastresourcestransactions WHERE service = ? AND resource = ? AND transaction_date = ? Allow FILTERING')
    today = datetime.now()
    try:
        for i in range(6, -1, -1):
            currentDate = today - timedelta(days=i)
            day = currentDate.strftime("%Y-%m-%d")
            getTransparentCountsResult = session.execute(getTransparentCountQuery, [str(serviceID), str(resourceID), day]) if serviceHost and resource else session.execute(getTransparentCountQuery, [str(serviceID), day])
            getRecordingCountsResult = session.execute(getRecordingCountQuery, [str(serviceID), str(resourceID), day]) if serviceHost and resource else session.execute(getRecordingCountQuery, [str(serviceID), day])
            getMockingCountsResult = session.execute(getMockingCountQuery, [str(serviceID), str(resourceID), day]) if serviceHost and resource else session.execute(getMockingCountQuery, [str(serviceID), day])
            responses.append({
                "name": day,
                "transparent": getTransparentCountsResult.one()[0],
                "recording": getRecordingCountsResult.one()[0],
                "mocking": getMockingCountsResult.one()[0]
                })
        return responses
    except:
        return None
    
def GetAllResponsesPercentage(userID, role):
    responses = [];
    if role == 'admin':
        getAcceptedCountQuery = session.prepare('SELECT SUM(accepted) FROM lastresponses Allow FILTERING')
        getRejectedCountQuery = session.prepare('SELECT SUM(rejected) FROM lastresponses Allow FILTERING')
        getNotValidatedCountQuery = session.prepare('SELECT SUM(not_validated) FROM lastresponses Allow FILTERING')
        try:
            getAcceptedCountResult = session.execute(getAcceptedCountQuery)
            getRejectedCountResult = session.execute(getRejectedCountQuery)
            getNotValidatedCountResult = session.execute(getNotValidatedCountQuery)
            responses.append({
                "name": 'Accepted',
                'value': getAcceptedCountResult.one()[0]
                })
            responses.append({
                "name": 'Rejected',
                'value': getRejectedCountResult.one()[0]
                })
            responses.append({
                "name": 'Not Validated',
                'value': getNotValidatedCountResult.one()[0]
                })
            return responses
        except:
            return None
    elif role == 'user':
        getServiceDataQuery = session.prepare('SELECT service FROM userservice WHERE user = ? Allow FILTERING')
        getAcceptedCountQuery = session.prepare('SELECT SUM(accepted) FROM lastresponses WHERE service = ? Allow FILTERING')
        getRejectedCountQuery = session.prepare('SELECT SUM(rejected) FROM lastresponses WHERE service = ? Allow FILTERING')
        getNotValidatedCountQuery = session.prepare('SELECT SUM(not_validated) FROM lastresponses WHERE service = ? Allow FILTERING')
        try:
            acceptedCount = 0
            rejectedCount = 0
            notValidatedCount = 0
            getServiceDataResult = session.execute(getServiceDataQuery, [str(userID)])
            for serviceID in getServiceDataResult:
                getAcceptedCountResult = session.execute(getAcceptedCountQuery, [serviceID.service])
                acceptedCount += getAcceptedCountResult.one()[0]
                getRejectedCountResult = session.execute(getRejectedCountQuery, [serviceID.service])
                rejectedCount += getRejectedCountResult.one()[0]
                getNotValidatedCountResult = session.execute(getNotValidatedCountQuery, [serviceID.service])
                notValidatedCount += getNotValidatedCountResult.one()[0]
            responses.append({
                "name": 'Accepted',
                'value': acceptedCount
                })
            responses.append({
                "name": 'Rejected',
                'value': rejectedCount
                })
            responses.append({
                "name": 'Not Validated',
                'value': notValidatedCount
                })
            return responses
        except:
            return None

def GetResponsesPercentage(host, resource):
    responses = [];
    getServiceIDQuery = session.prepare('SELECT id FROM service WHERE host = ? Allow FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [host]).one()
    serviceID = getServiceIDResult.id
    if host and not resource:
        getAcceptedCountQuery = session.prepare('SELECT SUM(accepted) FROM lastresponses WHERE service = ? Allow FILTERING')
        getRejectedCountQuery = session.prepare('SELECT SUM(rejected) FROM lastresponses WHERE service = ? Allow FILTERING')
        getNotValidatedCountQuery = session.prepare('SELECT SUM(not_validated) FROM lastresponses WHERE service = ? Allow FILTERING')
    elif host and resource:
        getResourceIDQuery = session.prepare('SELECT id FROM request WHERE service = ? AND name = ? Allow FILTERING')
        getResourceIDResult = session.execute(getResourceIDQuery, [str(serviceID), resource]).one()
        resourceID = getResourceIDResult.id
        getAcceptedCountQuery = session.prepare('SELECT SUM(accepted) FROM lastresponses WHERE service = ? AND resource = ? Allow FILTERING')
        getRejectedCountQuery = session.prepare('SELECT SUM(rejected) FROM lastresponses WHERE service = ? AND resource = ? Allow FILTERING')
        getNotValidatedCountQuery = session.prepare('SELECT SUM(not_validated) FROM lastresponses WHERE service = ? AND resource = ? Allow FILTERING')
    try:
        getAcceptedCountsResult = session.execute(getAcceptedCountQuery, [str(serviceID), str(resourceID)]) if host and resource else session.execute(getAcceptedCountQuery, [str(serviceID)])
        getRejectedCountsResult = session.execute(getRejectedCountQuery, [str(serviceID), str(resourceID)]) if host and resource else session.execute(getRejectedCountQuery, [str(serviceID)])
        getNotValidatedCountsResult = session.execute(getNotValidatedCountQuery, [str(serviceID), str(resourceID)]) if host and resource else session.execute(getNotValidatedCountQuery, [str(serviceID)])
        responses.append({
            "name": 'Accepted',
            'value': getAcceptedCountsResult.one()[0]
            })
        responses.append({
            "name": 'Rejected',
            'value': getRejectedCountsResult.one()[0]
            })
        responses.append({
            "name": 'Not Validated',
            'value': getNotValidatedCountsResult.one()[0]
            })
        return responses
    except:
        return None

def GetLastSevenDaysTransactionsInfo(service, resource):
    currentDate = datetime.now()
    sevenDaysAgo = currentDate - timedelta(days=7) 
    sevenDaysAgoDay = sevenDaysAgo.strftime("%Y-%m-%d")
    transactionsInformation = [];
    getLastTransactionsQuery = session.prepare('SELECT * FROM lastresourcestransactions WHERE transaction_date >= ? LIMIT 7 AlLOW FILTERING;')
    try:
        lastSevenDaysTransactionsInformationResult = session.execute(getLastTransactionsQuery, [sevenDaysAgoDay])
        for transactionInformation in lastSevenDaysTransactionsInformationResult:
                transactionsInformation.append({
                    "Transparent" : transactionInformation.transparent,
                    "Recording" : transactionInformation.recording,
                    "Mocking" : transactionInformation.mocking,
                    "date" : transactionInformation.transaction_date,
                })
        return transactionsInformation[:50]
    except:
        return None

def GetAllActivity(userID, role):
    responses = [];
    # Getting all Logs from the database
    getAllLogsQuery = session.prepare('SELECT * FROM logs')
    allLogsData = session.execute(getAllLogsQuery)
    logsToProcess = None
    # If user is admin there is no need to filter the logs
    if role == 'admin':
        logsToProcess = allLogsData
    # If user is not admin, we need to filter the logs to only show the logs that the user has access to
    elif role == 'user':
        # Getting the services that the user has access to
        getUserServicesAccessQuery = session.prepare('SELECT service FROM userservice WHERE user = ? ALLOW FILTERING')
        userServicesData = session.execute(getUserServicesAccessQuery, [str(userID)])
        print(userServicesData)
        # Filtering the logs to only show the logs that the user has access to accorsing to the services
        userServices = [data.service for data in userServicesData]
        filteredLogsUserAccess = [log for log in allLogsData if log.service_id in userServices] 
        logsToProcess = filteredLogsUserAccess
    # Processing the logs to return the information that we need
    return processLogs(logsToProcess)


def GetActivity(serviceHost, requestName):
    responses = [];
    logsData = None
    if(requestName):
        # Getting the request id to filter the logs
        queryToGetRequestId = session.prepare("SELECT id FROM request WHERE name = ? ALLOW FILTERING")
        requestID = session.execute(queryToGetRequestId, [str(requestName)]).one().id
        # If request is provides we only will get logs by that specific request, we don't need to filter by service because request exists only in one service
        queryToExecute = session.prepare("SELECT * FROM logs WHERE request_id = ? ALLOW FILTERING")
        logsData = session.execute(queryToExecute, [str(requestID)])
    else:
        # If request is not provided we will get all logs from the service, service must be allways provided when callind this method
        queryToGetServiceId = session.prepare("SELECT id FROM service WHERE host = ? ALLOW FILTERING")
        serviceID = session.execute(queryToGetServiceId, [str(serviceHost)]).one().id
        # Getting the logs from the service
        queryToExecute = session.prepare("SELECT * FROM logs WHERE service_id = ? ALLOW FILTERING")
        logsData = session.execute(queryToExecute, [str(serviceID)])
    # Processing the logs to return the information that we need
    return processLogs(logsData)
    
def getValidLogMesssage(messageID):
    message = None
    getMessageQuery = session.prepare('SELECT message FROM logmessages WHERE id = ? ALLOW FILTERING')
    if 'EDB' in messageID or 'ENX' in messageID:
        first_message = messageID.split(',')[0]
        second_message = messageID.split(' ')[1]
        firstMessageResult = session.execute(getMessageQuery, [first_message]).one()
        secondMessageResult = session.execute(getMessageQuery, [second_message]).one()
        message = firstMessageResult.message + ', ' + secondMessageResult.message
    else:
        getMessageResult = session.execute(getMessageQuery, [messageID]).one()
        message = getMessageResult.message
    return message

def getAffectedLogValue(levelAffected, serviceID, requestID, responseID):
    levelAffectedLowerCased = levelAffected.lower()
    # Will get the ID to use to get the affected value
    idToUse = None
    if levelAffectedLowerCased == 'service':
        idToUse = serviceID
    elif levelAffectedLowerCased == 'request':
        idToUse = requestID
    elif levelAffectedLowerCased == 'response':
        return responseID
    # Query string depending on the level affected
    getAffectedQueryString = F'SELECT name FROM {levelAffectedLowerCased} WHERE id = ?'
    getAffectedValueQuery = session.prepare(getAffectedQueryString)
    # Getting the affected value passing ID as uuid because in DB this is a UUID
    getServiceAffectedResult = session.execute(getAffectedValueQuery, [uuid.UUID(idToUse)]).one()
    if(getServiceAffectedResult):
        return getServiceAffectedResult.name
    else:
        return "Affected value not found"
    
def processLogs(logsData):
    try:
        responses = [];
        # Processing the logs to get the information that we need
        for log in logsData:
            # decode log message
            message = getValidLogMesssage(log.message)
            affectedLogValue = None
            if log.is_error == False:
                # Getting the affected value for example the service name, request name or response id
                affectedLogValue = getAffectedLogValue(log.level_affected, log.service_id, log.request_id, log.response_id)
            else:
                affectedLogValue = "Nothing was affected."
            # Appending the log information to the responses array
            responses.append({
                "User" : log.user,
                "Date" : log.date_created.strftime("%Y-%m-%d %H:%M:%S"),
                "Message" : message,
                "Affected" : affectedLogValue,
                "Is Error" : log.is_error
            })
            # Sorting the logs by date
            responses.sort(key=lambda x: x["Date"], reverse=True)
        # Returning only last 50 logs
        return responses[:50]
    except:
        return None