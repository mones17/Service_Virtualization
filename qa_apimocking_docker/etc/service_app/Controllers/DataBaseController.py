from getpass import getuser
from http.client import responses
from cassandra.cluster import Cluster
cluster = Cluster(contact_points=['cassandradb'])
session = cluster.connect('servicevirtualization')
import uuid

def GetUserID(username):
    userIDQuery = session.prepare("SELECT id FROM user WHERE name = ? Allow FILTERING")
    userIDResult = session.execute(userIDQuery, [username]).one()
    return userIDResult.id

def ValidateUserExist(username):
    userExistQuery = session.prepare('SELECT COUNT(*) FROM user WHERE name = ? Allow FILTERING')
    userExistResult = session.execute(userExistQuery, [username])
    return userExistResult[0].count

def ValidateUserExistByID(userID):
    userExistQuery = session.prepare('SELECT COUNT(*) FROM user WHERE id = ? Allow FILTERING')
    userExistResult = session.execute(userExistQuery, [userID])
    return userExistResult[0].count

def ValidateAdminRole(userID):
    adminRoleQuery = session.prepare("SELECT role FROM user WHERE id = ? Allow FILTERING")
    adminRoleResult= session.execute(adminRoleQuery, [userID]).one()
    if "admin" in adminRoleResult:
        return 1
    else:
        return 0

def GetServiceID(host):
    getServiceIDQuery = session.prepare('SELECT id FROM service WHERE host = ? Allow FILTERING')
    getServiceIDResult = session.execute(getServiceIDQuery, [host]).one()
    return getServiceIDResult.id

def ExistingService(host):
    getServiceCountQuery = session.prepare('SELECT COUNT(*) FROM service WHERE host = ? Allow FILTERING')
    getServiceCountResult = session.execute(getServiceCountQuery, [host])
    return getServiceCountResult[0].count

def ExistingServiceName(service_name):
    getServiceCountQuery = session.prepare('SELECT COUNT(*) FROM service WHERE name = ? Allow FILTERING')
    getServiceCountResult = session.execute(getServiceCountQuery, [service_name])
    return getServiceCountResult[0].count

def AddServiceByUserID(userID, serviceID):
    addServiceQuery = session.prepare('INSERT INTO userservice (id, user, date_created, last_update, '
                                      'last_access, service) VALUES (uuid(), ?, toTimestamp(now()), toTimestamp(now()), '
                                      'toTimestamp(now()), ?)')
    session.execute(addServiceQuery, [str(userID), str(serviceID)])

def DeleteServiceByUserID(userID, serviceID):
    getServiceQuery = session.prepare('SELECT id FROM userservice WHERE user = ? AND service = ? Allow FILTERING')
    getServiceResult = session.execute(getServiceQuery, [str(userID), str(serviceID)]).one()
    deleteServiceQuery = session.prepare('DELETE FROM userservice WHERE id = ?')
    session.execute(deleteServiceQuery, [getServiceResult.id])
    
def DeleteHostsByServiceName(userID, service_name):
    delCount = 0
    getHostsIDQuery = session.prepare('SELECT id FROM service WHERE name = ? Allow FILTERING')
    getHostsIDResult = session.execute(getHostsIDQuery, [service_name])
    for hostID in getHostsIDResult:
        getServiceQuery = session.prepare('SELECT COUNT(*), id FROM userservice WHERE user = ? AND service = ? Allow FILTERING')
        getServiceResult = session.execute(getServiceQuery, [str(userID), str(hostID.id)]).one()
        if getServiceResult.count > 0:
            deleteServiceQuery = session.prepare('DELETE FROM userservice WHERE id = ?')
            session.execute(deleteServiceQuery, [getServiceResult.id])
            delCount += 1
    if delCount > 0:
        return True

def VerifyExistingPermission(userID, serviceID):
    verifyPermissionQuery = session.prepare('SELECT COUNT(*) FROM userservice WHERE user = ? AND service = ? Allow FILTERING')
    verifyPermissionResult = session.execute(verifyPermissionQuery, [str(userID), str(serviceID)])
    return verifyPermissionResult[0].count

def UserServices(userID):
    responses = [];
    getUserServicesQuery = session.prepare('SELECT * FROM userservice WHERE user = ? Allow FILTERING')
    getUserServicesResult = session.execute(getUserServicesQuery, [str(userID)])
    # Dict to store the services
    service_dict = {}
    for service in getUserServicesResult:
        getServiceDataQuery = session.prepare('SELECT * FROM service WHERE id = ? Allow FILTERING')
        getServiceDataResult = session.execute(getServiceDataQuery, [uuid.UUID(str(service[4]))]).one()
        key = (getServiceDataResult.region, getServiceDataResult.portfolio, getServiceDataResult.name)  # Unique key per service name
        if key not in service_dict:
            # If not exists the key, create a new one
            service_dict[key] = {
                "Region": getServiceDataResult.region,
                "Portfolio": getServiceDataResult.portfolio,
                "Name": getServiceDataResult.name,
                "Hosts": []
            }
        # Add the host to the list
        service_dict[key]["Hosts"].append({
            "Host-Name": getServiceDataResult.host_name,
            "Host": getServiceDataResult.host,
            "IP": getServiceDataResult.actual_ip,
            "Port": getServiceDataResult.port,
            "Traffic-Analyzer": getServiceDataResult.is_trafficanalyzer
        })
    # Convert the dict into list of responses
    for key, value in service_dict.items():
        responses.append(value)
    return responses

def GetAllServices():  
    responses = []  
    getServiceDataQuery = session.prepare('SELECT * FROM service Allow FILTERING')  
    getServiceDataResult = session.execute(getServiceDataQuery)  
    # Dict to store the services
    service_dict = {}
    for service in getServiceDataResult:  
        key = (service.region, service.portfolio, service.name)  # Unique key per service name 
        if key not in service_dict:  
            # If not exists the key, create a new one
            service_dict[key] = {  
                "Region": service.region,  
                "Portfolio": service.portfolio,  
                "Name": service.name,  
                "Hosts": []  
            }  
        # Add the host to the list  
        service_dict[key]["Hosts"].append({  
            "Host-Name": service.host_name,
            "Host": service.host,  
            "IP": service.actual_ip,  
            "Port": service.port,  
            "Traffic-Analyzer": service.is_trafficanalyzer  
        })  
    # Convert the dict into list of responses
    for key, value in service_dict.items():  
        responses.append(value)  
    return responses  

def AllUsers():
    responses = [];
    getUsersDataQuery = session.prepare('SELECT * FROM user Allow FILTERING')
    getUsersDataResult = session.execute(getUsersDataQuery)
    for user in getUsersDataResult:
        responses.append({
            "ID": user.id,
            "Username": user.name,
            "Email": user.email,
            "Role": user.role
            })
    return responses

def GetAllUsersByServiceID(serviceID):
    responses = [];
    getUsersIDByServiceQuery = session.prepare('SELECT * FROM userservice WHERE service = ? Allow FILTERING')
    getUserInformationQuery = session.prepare('SELECT * FROM user WHERE id = ? Allow FILTERING')
    getUsersIDByServiceResult = session.execute(getUsersIDByServiceQuery, [str(serviceID)])
    for userID in getUsersIDByServiceResult:
        getUserInformationResult = session.execute(getUserInformationQuery, [uuid.UUID(str(userID[5]))]).one()
        responses.append({
            "ID" : getUserInformationResult.id,
            "Username" : getUserInformationResult.name,
            "Email" : getUserInformationResult.email,
            "Role" : getUserInformationResult.role
            })
    return responses

def GetAdminInformation():
    responses = [];
    getAdminIDQuery = session.prepare('SELECT * FROM user WHERE role = ? Allow FILTERING')
    getAdminIDResult = session.execute(getAdminIDQuery, ["admin"])
    for admin in getAdminIDResult:
        responses.append({
            "ID" : admin.id,
            "Username" : admin.name,
            "Email" : admin.email,
            "Role" : admin.role
            })
    return responses