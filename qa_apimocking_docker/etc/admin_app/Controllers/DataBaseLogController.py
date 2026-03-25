from getpass import getuser
from http.client import responses
import uuid
from cassandra.cluster import Cluster
cluster = Cluster(contact_points=['cassandradb'])
session = cluster.connect('servicevirtualization')

def InsertLogInDatabase(dateCreated, user, message, levelAffected, isError, serviceId, requestId, responseId):
    logValuesQuery = session.prepare("INSERT INTO logs (id, date_created, user, message, level_affected, is_error, service_id, request_id, response_id) VALUES (uuid(), ?, ?, ?, ?, ?, ?, ?, ?)")
    logValuesResult = session.execute(logValuesQuery, [dateCreated, user, message, levelAffected, isError, str(serviceId), str(requestId), str(responseId)])