from ast import Not
import token
import uuid
from fastapi import Request, Response, HTTPException, status
from Controllers.DataBaseController import *
from Helpers.Token import *
from Helpers.SMTP import *
from Helpers.Password import *
from fastapi.responses import JSONResponse
import json
import uuid
import logging
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
   
current_day = datetime.now().strftime("%Y-%m-%d")
filename = f'/home/python/app/logs/servicevirtualization_{current_day}.log'

handler = TimedRotatingFileHandler(filename, when="midnight", interval=1, backupCount=30)
handler.setLevel(logging.INFO)
logging.getLogger().addHandler(handler)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S ')
handler.setFormatter(formatter)
logging.getLogger().addHandler(handler)

logging.getLogger('cassandra').setLevel(logging.CRITICAL)

async def SendNewUserEmail(request: Request, response: Response):
    body = await request.json()
    email = body.get('email')
    role = body.get('isAdmin')
    baseUrl = body.get('baseUrl')
    authHeader = dict(request.headers)
    authToken = authHeader["authorization"].split()
    adminUsername = await GetTokenInformation(authToken)
    if ValidateAdminRole(adminUsername) == 1:
        if email:
            if ValidateExistingEmail(email):
                responses = {};
                if role is None:
                    role = False
                token = CreateEmailToken(data={"email": email, "isAdmin": role})
                tokenUrl = token.replace('.', '$')
                link = baseUrl + 'setup/' + tokenUrl
                SendEmail(email, link)
                logging.info('The user %s set a token for email: %s.', adminUsername, email)
                response.status_code=200
                responses = { "Token" : token }
                return responses
            else:
                response.status_code=400
                return "Email already exist."
        else:
            response.status_code=400
            return "Missing information, provide email to set token."
    else:
        response.status_code=401
        return "User unauthorized"
    
async def GetEmailTokenInformation(request: Request):
    authHeader = dict(request.headers)
    authToken = authHeader["authorization"].split()
    email, role = await DecodeEmailTokenInformation(authToken)
    if email:
        responses = {};
        responses = { "Email" : email, "IsAdmin" : role }
        return responses
    else:
        return "Token is not valid."

async def CreateUser(request: Request, response: Response):
    body = await request.json()
    username = body.get('username')
    password = body.get('password')
    authHeader = dict(request.headers)
    authToken = authHeader["authorization"].split()
    email, role = await DecodeEmailTokenInformation(authToken)
    if email:
        passwordComplexity, message = ValidatePassword(password)
        if ValidateExistingUserAndEmail(username, email):
            if passwordComplexity:
                encodedPassword = EncryptPassword(password)
                InsertUser(email, username, encodedPassword, role)
                logging.info('The user %s create user: %s successfully.',email , username)
                response.status_code=200
                return "User created successfully."
            else:
                response.status_code=400
                return message
        else:
            logging.warning('The user %s try to create user: %s which is an existing user.', email, username)
            response.status_code=400
            return "User already exist."
    else:
        logging.warning('User %s unauthorized, can not create new user cause is an user role only.', username)
        response.status_code=400
        return "User doesn't have admin permissions"

async def Login(request: Request, response: Response):
    body = await request.json()
    username = body.get('username')
    password = body.get('password')
    if username and password:
        userID, name, email, role, storedEncryptedPassword = ValidateExistingUser(username)
        if userID and name and email and role and storedEncryptedPassword:
            if VerifyPassword(password, storedEncryptedPassword):
                responses = {};
                UpdateAccessTime(userID)
                accessToken = CreateToken(data={"sub": name})
                logging.info('Login by user %s by %s, with email %s and %s permission, access token: %s by bearer type.', name, username, email, role, accessToken)
                response.status_code=200
                responses = {"Auth" : "Successful", "User" : name, "Email" : email, "Role" : role, "access_token" : accessToken, "token_type" : "bearer" }
                return responses
            else:
                logging.warning('Try to login with incorrect password by user %s, with %s.', name, username)
                response.status_code=401
                return "Incorrect username or password."
        else:
            logging.warning('Try to login with inexisting user: %s.', username)
            response.status_code=401
            return "User and password don't match or user doesn't exist yet."
    else:
        response.status_code=400
        return "Missing information, please provide email or username and password."
  
async def Auth(request: Request):
    # Get token from header and validate if token information is valid
    authHeader = request.headers.get("authorization")
    if authHeader:
        authToken = authHeader.split()
        username = await GetTokenInformation(authToken)
        userID, name, email, role, storedEncryptedPassword = ValidateExistingUser(username)
        if userID and name and email and role and storedEncryptedPassword:
            response = JSONResponse(content={"Login":"Successful","username": username}, status_code=200)
        else:
            response = JSONResponse(content={"message": "User and password don't match or user doesn't exist yet."}, status_code=401)
    else:
        response = JSONResponse(content={"message": "Token is not part of the headers."}, status_code=401)
    return response

async def DeleteUserByID(request: Request, response: Response, userID):
    authHeader = dict(request.headers)
    authToken = authHeader["authorization"].split()
    adminUsername = await GetTokenInformation(authToken)
    if ValidateAdminRole(adminUsername) == 1:
        name, email, role, password = ValidateGetUserData(uuid.UUID(str(userID)))
        if name and email and role and password:
            DeleteUser(uuid.UUID(str(userID)))
            logging.info('User %s delete the user %s by ID: %s.', adminUsername, name, userID)
            response.status_code=200
            return "User deleted successfully."
        else:
            logging.warning('User %s try to delete inexsting user with ID: %s.', adminUsername, userID)
            response.status_code=400
            return "User doesn't exist yet."
    else:
        logging.warning('User %s try to delete user withouth permission.', adminUsername)
        response.status_code=400
        return "User unauthorized"

async def UpdateUserByID(request: Request, response: Response, userID):
    body = await request.json()
    email = body.get('email')
    username = body.get('username')
    password = body.get('password')
    role = body.get('role')
    authHeader = dict(request.headers)
    authToken = authHeader["authorization"].split()
    adminUsername = await GetTokenInformation(authToken)
    if ValidateAdminRole(adminUsername) == 1:
        if password or email or username or role:
            actualName, actualEmail, actualRole, storedEncryptedPassword = ValidateGetUserData(uuid.UUID(str(userID)))
            if actualName and actualEmail and actualRole and storedEncryptedPassword:
                username = None if actualName == username else username if username else None
                email = None if actualEmail == email else email if email else None
                role = None if actualRole == role else role if role else None
                passwordBand, messagePassword = ValidatePassword(password) if password else (True, "")
                usernameBand = ValidateExistingUsername(username) == True if username else True
                emailBand = ValidateExistingEmail(email) == True if email else True
                roleBand = True if username or email or password else None if role is None else True
                if usernameBand and emailBand and passwordBand and roleBand:
                    if password:
                        password = EncryptPassword(password)
                    UpdateUser(uuid.UUID(str(userID)), username, email, password, role)
                    usernameMessage = "Username {} updated to {}. ".format(actualName, username) if username else ""
                    emailMessage = "Email {} updated to {}. ".format(actualEmail, email) if email else ""
                    roleMessage = "Role {} updated to {}. ".format(actualRole, role) if role else ""
                    passwordMessage = "password updated." if password else ""
                    message = usernameMessage + emailMessage + roleMessage + passwordMessage
                    logging.info('The user %s made some changes for %s: %s.', adminUsername, actualName, message)
                    response.status_code=200
                    return "User updated successfully."
                else:
                    messageUsername = "The username that you're trying to insert already exist. " if not usernameBand else ""  
                    messageEmail = "The email that you're trying to insert already exist." if not emailBand else ""
                    message = messageUsername + messageEmail + messagePassword
                    if message == "":
                        response.status_code = 304
                        message = "Trying to submit a form without changes"
                    else:
                        response.status_code=400
                    logging.warning('The user %s try to update user %s, but get this error(s): %s.', adminUsername, actualName, message)
                    return message
            else:
                logging.warning('The user %s try to update an inexisting user by wrong ID: %s.', adminUsername, userID)
                response.status_code=400
                return "User doesn't exist yet."
        else:
            response.status_code=400
            return "Please provide data to update, you can't update with empty data."
    else:
        logging.warning('User %s try to update user without admin permissions.')
        response.status_code=400
        return "User doesn't have admin permissions"

async def ResetPassword(request, response):
    body = await request.json()
    password = body.get('password')
    if password:
        authHeader = dict(request.headers)
        authToken = authHeader["authorization"].split()
        username = await GetTokenInformation(authToken)
        userID = GetUserID(username)
        passwordComplexity, message = ValidatePassword(password)
        if passwordComplexity:
            encodedPassword = EncryptPassword(password)
            UpdateUserPassword(encodedPassword, userID)
            logging.info('User %s reset his password.', username)
            response.status_code=200
            return "User password was updated successfully."
        else:
            logging.warning('User %s try to reset his password but get this error(s): %s.', username, message)
            response. status_code=400
            return message
    else:
        logging.warning('User %s try to reset his password without new password.', username)
        response.status_code=400
        return "Provide new password, with missing informationthe password can't be updated."

async def GetUserInfo(request, response):
    authHeader = dict(request.headers)
    authToken = authHeader["authorization"].split()
    username = await GetTokenInformation(authToken)
    userID, name, email, role, storedEncryptedPassword = ValidateExistingUser(username)
    if userID and name and email and role and storedEncryptedPassword:
        logging.info('User information access: %s. User accessed their personal information in the system, this includes their username, email, and role.', username)
        responses = [];
        response.status_code=200
        responses.append({
            "User ID" : userID,
            "Name" : name,
            "Email" : email,
            "Role" : role
        })
        return responses
    else:
        logging.warning('An unknown user attempted to access personal information in the system, there is no record of this user.')
        response.status_code=400
        return "User doesn't exist or doesn't have information yet."
   
