from cassandra.cluster import Cluster
from jose import jwt, JWTError
import uuid
from datetime import datetime

cluster = Cluster(contact_points=['cassandradb'])
session = cluster.connect('servicevirtualization')
  
# This method is used for validate is the email is already registered
def ValidateExistingUser(username):
    exitingUserQuery = session.prepare("SELECT COUNT(*) FROM user WHERE name = ? Allow FILTERING")
    existingUserResult = session.execute(exitingUserQuery, [username])
    existingEmailQuery = session.prepare('SELECT COUNT(*) FROM user WHERE email = ? Allow FILTERING')
    existingEmailResult = session.execute(existingEmailQuery, [username])
    if existingUserResult[0].count > 0:
        getUserInformationQuery = session.prepare("SELECT id, name, email, role, password FROM user WHERE name = ? Allow FILTERING")
        getUserInformationResult = session.execute(getUserInformationQuery, [username]).one()
        return getUserInformationResult.id, getUserInformationResult.name, getUserInformationResult.email, getUserInformationResult.role, getUserInformationResult.password
    elif existingEmailResult[0].count > 0:
        getUserInformationQuery = session.prepare("SELECT id, name, email, role, password FROM user WHERE email = ? Allow FILTERING")
        getUserInformationResult = session.execute(getUserInformationQuery, [username]).one()
        return getUserInformationResult.id, getUserInformationResult.name, getUserInformationResult.email, getUserInformationResult.role, getUserInformationResult.password
    else:
        return None, None, None, None, None

def ValidateGetUserData(userID):
    exitingUserQuery = session.prepare("SELECT COUNT(*) FROM user WHERE id = ? Allow FILTERING")
    existingUserResult = session.execute(exitingUserQuery, [userID])
    if existingUserResult[0].count > 0:
        getUserInformationQuery = session.prepare("SELECT name, email, role, password FROM user WHERE id = ? Allow FILTERING")
        getUserInformationResult = session.execute(getUserInformationQuery, [userID]).one()
        return getUserInformationResult.name, getUserInformationResult.email, getUserInformationResult.role, getUserInformationResult.password
    else:
        return None, None, None, None

def ValidateExistingUserAndEmail(user, email):
    exitingUserQuery = session.prepare("SELECT COUNT(*) FROM user WHERE name = ? Allow FILTERING")
    existingUserResult = session.execute(exitingUserQuery, [user])
    existingEmailQuery = session.prepare('SELECT COUNT(*) FROM user WHERE email = ? Allow FILTERING')
    existingEmailResult = session.execute(existingEmailQuery, [email])
    if existingUserResult[0].count == 0 and existingEmailResult[0].count == 0:
        return True
    return False

def ValidateExistingUsername(username):
    exitingUserQuery = session.prepare("SELECT COUNT(*) FROM user WHERE name = ? Allow FILTERING")
    existingUserResult = session.execute(exitingUserQuery, [username])
    if existingUserResult[0].count == 0:
        return True
    return False

def ValidateExistingEmail(email):
    existingEmailQuery = session.prepare('SELECT COUNT(*) FROM user WHERE email = ? Allow FILTERING')
    existingEmailResult = session.execute(existingEmailQuery, [email])
    if existingEmailResult[0].count == 0:
        return True
    return False


def ValidateAdminRole(username):
    userdID = GetUserID(username)
    adminRoleQuery = session.prepare("SELECT role FROM user WHERE id = ? Allow FILTERING")
    adminRoleResult= session.execute(adminRoleQuery, [userdID]).one()
    if "admin" in adminRoleResult:
        return 1
    else:
        return 0

def GetUserEmail(user):
    exitingUserQuery = session.prepare("SELECT email FROM user WHERE name = ? Allow FILTERING")
    existingUserResult = session.execute(exitingUserQuery, [user])
    return existingUserResult[0].email

def GetUserByEmail(email):
    exitingUserQuery = session.prepare("SELECT name FROM user WHERE email = ? Allow FILTERING")
    existingUserResult = session.execute(exitingUserQuery, [email])
    return existingUserResult[0].name

def ValidateExistingUserByID(userID):
     existingUserIDQuery = session.prepare("SELECT COUNT(*) FROM user WHERE id = ? Allow FILTERING")
     existingUserIDResult = session.execute(existingUserIDQuery, [userID])
     print(existingUserIDResult[0].count)
     return existingUserIDResult[0].count

def InsertUser(email, name, encocedPassword, role):
	insertUserQuery = session.prepare("""
		INSERT INTO User (id, email, name, password, role, date_created, last_access, last_update)
		VALUES (uuid(), ?, ?, ?, ?, toTimestamp(now()), toTimestamp(now()), toTimestamp(now()))
	""")
	session.execute(insertUserQuery, [email, name, encocedPassword, role])

def ValidateUserInformation(email, username):
    matchingUserQuery = session.prepare("SLEECT * FROM user WHERE email = ? AND WHERE username = ? Allow FILTERING")
    matchingUserResult = session.execute(matchingUserQuery, [email, username])
    return matchingUserResult.one().id

def GetPasswordID(username):
	passwordIdQuery = session.prepare("SELECT password, id FROM user WHERE name = ? ALLOW FILTERING")
	passwordIdResult = session.execute(passwordIdQuery, [username])
	return passwordIdResult[0].password, passwordIdResult[0].id

def GetUserID(username):
    userIDQuery = session.prepare("SELECT id FROM user WHERE name = ? Allow FILTERING")
    userIDResult = session.execute(userIDQuery, [username]).one()
    return userIDResult.id

def UpdateAccessTime(passwordID):
    updateStatement = session.prepare("UPDATE user SET last_access = toTimestamp(now()) WHERE id = ?")
    session.execute(updateStatement, [passwordID])

def UpdateUser(userID, username, email, password, role):
    if username:
        updateNameQuery = session.prepare("UPDATE user SET name = ? WHERE id = ?")
        session.execute(updateNameQuery, [username, userID])
    if email:
        updateEmailQuery = session.prepare("UPDATE user SET email = ? WHERE id = ?")
        session.execute(updateEmailQuery, [email, userID])
    if password:
        updatePasswordQuery = session.prepare("UPDATE user SET password = ? WHERE id = ?")
        session.execute(updatePasswordQuery, [password, userID])
    if role:
        updateRoleQuery = session.prepare("UPDATE user SET role = ? WHERE id = ?")
        session.execute(updateRoleQuery, [role, userID])

def DeleteUser(userID):
    deleteUserByIDQuery = session.prepare('DELETE FROM user WHERE id = ?')
    session.execute(deleteUserByIDQuery, [userID])
    getUserIDQuery = session.prepare('Select id FROM userservice WHERE user = ? Allow FILTERING')
    deleteUserPermissionQuery = session.prepare('DELETE FROM userservice WHERE id = ?')
    getUserIDResult = session.execute(getUserIDQuery, [str(userID)])
    for user in getUserIDResult:
        session.execute(deleteUserPermissionQuery, [uuid.UUID(str(user.id))])

def UserInfo(role, userID):
    responses = [];
    if role == "admin":
        getUserQuery = session.prepare('SELECT * FROM user Allow FILTERING')
        getUserResult = session.execute(getUserQuery)
        for user in getUserResult:
            responses.append({
                "User ID" : str(user.id),
                "Name" : user.name,
                "Email" : user.email,
                "Role" : user.role
             })
    elif role == "user":
        getUserQuery = session.prepare('SELECT * FROM user where id = ? Allow FILTERING')
        getUserResult = session.execute(getUserQuery, [userID]).one()
        responses.append({
            "User ID" : str(getUserResult.id),
            "Name" : getUserResult.name,
            "Email" : getUserResult.email,
            "Role" : getUserResult.role
        })
    else:
        return None
    return responses

def UpdateUserPassword(password, userID):
    updatePasswordQuery = session.prepare("UPDATE user SET password = ? WHERE id = ?")
    session.execute(updatePasswordQuery, [password, userID])