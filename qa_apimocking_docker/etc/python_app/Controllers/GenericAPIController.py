import time
import xmltodict
import xml.etree.ElementTree as ET
from datetime import *
from fastapi import Request, Response
from Controllers.DataBaseController import *
from Helpers.MakeAPICall import *
from fastapi.responses import JSONResponse
import uuid
from urllib.parse import unquote

async def ProcessRequest (request: Request, globalResponse:Response):
    if(request.method == 'OPTIONS'):
        globalResponse.status_code = 204
    else:
        # Get Request ID
        service = request.headers.get('host')
        content_type = request.headers.get('Content-Type', '')
        # Default payload is an empty dictionary
        request_payload = {}
        # Read the body as bytes
        body_bytes = await request.body()
        query_params = request.query_params
        if query_params:  
            for key, value in query_params.items():  
                decoded_value = unquote(value)  
                if 'id' in key.lower():  
                    print("INTO ID, CONTAINS ID")
                    try:  
                        print("TRYING TO CONVERT TO UUID")
                        clean_value = decoded_value.strip('"') 
                        request_payload[key] = uuid.UUID(clean_value) 
                        query_params=uuid.UUID(clean_value)
                    except ValueError:  
                        print("CANNOT BE CONVERTED TO UUID")
                        request_payload[key] = decoded_value  
                else:  
                    request_payload[key] = decoded_value
        if(request.method == 'GET'):
            pass
        elif 'application/x-www-form-urlencoded' in content_type:
            # Handle application/x-www-form-urlencoded
            form_data = await request.form()
            # Convert the Form object to a dictionary and then to a JSON string
            request_payload = dict(form_data)
        elif 'application/xml' in content_type or 'application/soap+xml' in content_type or 'text/xml' in content_type:
            # Handle application/xml
            xml_data = body_bytes.decode('utf-8')
            # Convert XML data to a dictionary
            xml_dict = xmltodict.parse(xml_data)
            # Convert the dictionary to a JSON string
            request_payload = json.loads(json.dumps(xml_dict))
        else:
            try:
                # Convert the JSON body to a dictionary
                request_payload = json.loads(body_bytes.decode('utf-8'))
            except json.JSONDecodeError:
                # Handle invalid JSON
                globalResponse.status_code = 400
                return {"error": "Unsupported Content-Type: {} in request body.".format(content_type)}
        url = str(request.url)
        resource = url.split(service, 1)[1]
        # Verify if traffic analyzer mode is enabled
        trafficAnalyzer = IsTrafficAnalyzerMode(service)
        if trafficAnalyzer:
            apiMode = 1
        else:
            requestID = GetRequestID(service, resource)
            apiMode = GetAPIModeUsingRequestID(requestID)
        if apiMode == 0:
            # Transparent Mode
            # Make Call to the real API
            callResponse = await MakeCall(request, globalResponse, body_bytes)
            if callResponse.headers is not None:  
                headers = {key: value for key, value in callResponse.headers.items()}
                response_content_type = callResponse.headers['Content-Type']
            serviceID = GetServiceID(service)
            resourceID = GetRequestID(service, resource)
            if SaveLastResourceTransaction(serviceID, resourceID, 'transparent') :
                InsertLogInDatabase(datetime.now(), 'system', 'UAMT', "Request", False, '', '', '')
                if 'application/soap+xml' in content_type or 'text/xml' in content_type:
                    return Response(content=callResponse.content.decode('utf-8'), media_type = response_content_type)
                else:
                    return parse_response_content(callResponse)
            else:
                return "Transaction couldn't be saved in DB"
        elif apiMode == 1:
            # Recording Mode
            start_time = time.time()
            # Make Call to the real API
            callResponse = await MakeCall(request, globalResponse, body_bytes)
            finish_time = time.time()
            time_taken = finish_time - start_time
            if callResponse.headers is not None:  
                headers = {key: value for key, value in callResponse.headers.items()}
                response_content_type = callResponse.headers['Content-Type']
                statusCode = callResponse.status_code
            else:
                response_content_type = 'NoneType'
                statusCode = 200
            # Validate if the response content type is valid
            if any(content_type in response_content_type for content_type in ['application/xml', 'application/soap+xml', 'application/json', 'application/text', 'text/xml']) and trafficAnalyzer:
                # If the request does not exist, create it and return true to get the new requestID
                CreateIfRequestDoesNotExist(service, resource, request.method)
                requestID = GetRequestID(service, resource)
                # Save response in the DB
                await SaveResponse(requestID, callResponse, request_payload, time_taken)
                # Return the response
                serviceID = GetServiceID(service)
                resourceID = GetRequestID(service, resource)
                if SaveLastResourceTransaction(serviceID, resourceID, 'recording') and SaveResponseStatus(serviceID, resourceID, 'not_validated', None):
                    InsertLogInDatabase(datetime.now(), 'system', 'UAMR', "Request", False, serviceID, resourceID, '')
                    return Response(content=callResponse.content.decode('utf-8'), media_type = response_content_type, headers=headers)
                else:
                    return "Transaction couldn't be saved in DB"
            elif any(content_type in response_content_type for content_type in ['application/xml', 'application/soap+xml', 'application/json', 'application/text', 'text/xml', 'text/html']) and not trafficAnalyzer:
                # Save response in the DB
                await SaveResponse(requestID, callResponse, request_payload, time_taken)
                # Return the response
                serviceID = GetServiceID(service)
                resourceID = GetRequestID(service, resource)
                if SaveLastResourceTransaction(serviceID, resourceID, 'recording') and SaveResponseStatus(serviceID, resourceID, 'not_validated', None):
                    InsertLogInDatabase(datetime.now(), 'system', 'UAMR', "Request", False, serviceID, resourceID, '')
                    if 'application/soap+xml' in content_type or 'text/xml' in content_type or 'text/html' in content_type:
                        return Response(content=callResponse.content.decode('utf-8'), media_type = response_content_type, headers=headers)
                    else:
                        return parse_response_content(callResponse)
                else:
                    return "Transaction couldn't be saved in DB"
            else:
                try:
                    headers.pop('content-length')
                    headers.pop('content-encoding')
                except:
                    pass
                if 'text/' in response_content_type:
                    return Response(content=callResponse.content.decode('utf-8'), media_type = response_content_type, headers=headers)
                else:
                    return Response(content=callResponse.content, media_type = response_content_type, headers=headers)
        elif apiMode == 2:
            # Mocking Mode
            # Make query trying to get a saved and validated response
            body, status_code, content_type = await GetResponse(requestID, request_payload)
            if body == None:
                # No response was saved in the DB
                start_time = time.time()
                # Make Call to the real API
                callResponse = await MakeCall(request, globalResponse, body_bytes)
                if callResponse.headers is not None:  
                    headers = {key: value for key, value in callResponse.headers.items()}
                    response_content_type = callResponse.headers['Content-Type']
                finish_time = time.time()
                time_taken = finish_time - start_time
                # Save response in the DB
                await SaveResponse(requestID, callResponse, request_payload, time_taken)
                serviceID = GetServiceID(service)
                resourceID = GetRequestID(service, resource)
                if SaveLastResourceTransaction(serviceID, resourceID, 'mocking') and SaveResponseStatus(serviceID, resourceID, 'not_validated', None):
                    InsertLogInDatabase(datetime.now(), 'system', 'UAMR', "Request", False, serviceID, requestID, '')
                    if 'application/soap+xml' in content_type or 'text/xml' in content_type or 'text/html' in content_type:
                        return Response(content=callResponse.content.decode('utf-8'), media_type = response_content_type, headers=headers)
                    else:
                        return parse_response_content(callResponse)
                else:
                    return "Transaction couldn't be saved in DB"
            else:
                globalResponse.status_code = status_code
                headers = {"Content-Type": content_type}
                serviceID = GetServiceID(service)
                resourceID = GetRequestID(service, resource)
                if SaveLastResourceTransaction(serviceID, resourceID, 'mocking') :
                    InsertLogInDatabase(datetime.now(), 'system', 'UAMM', "Request", False, serviceID, requestID, '')
                    if 'application/soap+xml' in content_type or 'text/xml' in content_type or 'text/html' in content_type:
                        return Response(content=body, media_type = content_type, headers=headers)
                    else:
                        return JSONResponse(content=body, headers=headers)
                else:
                    return "Transaction couldn't be saved in DB"

def parse_response_content(response):
    try:
        # Get the Content-Type of the response
        content_type = response.headers.get('Content-Type', '')
        # Check if the Content-Type is text
        if 'text/plain' in content_type or 'text/html' in content_type:
            # Decode the content to a Unicode string
            return response.content.decode('utf-8')
        elif 'application/json' in content_type:
            # Parse the JSON content
            return json.loads(response.content.decode('utf-8'))
        elif 'application/xml' in content_type or 'application/soap+xml' in content_type or 'text/xml' in content_type:
            # Parse the XML content
            return ET.fromstring(response.content.decode('utf-8'))
        else:
            # Handle other content types as needed
            return response.content
    except Exception as e:
        print(f"Error processing response content: {str(e)}")
        return None