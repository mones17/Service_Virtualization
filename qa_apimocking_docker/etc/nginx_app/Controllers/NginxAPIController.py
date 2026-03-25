from fastapi import Request, Response, FastAPI
from Controllers.ConfigNgnixController import *
from Controllers.DataBaseController import *

async def AddRoute( request, response):
    body = await request.json()
    server_name = body.get('host')
    route = body.get('route')
    if server_name and route:
        route_added = add_route_to_server_block(server_name, route)
        if route_added :
            body = "OK"
            response.status_code = 200
        else:
            body = "Something was wrong"
            response.status_code = 500
    else:
        body = "Please send all requiered information"
        response.status_code = 400
    return body

async def SetProxyTrafficAnalyzer( request, response):
    body = await request.json()
    service_host = body.get('host')
    print(service_host)
    if service_host:
        # Create function to get the status of the traffic analyzer proxy (ConfigNginxController)
        trafficAnalyzer_status = get_trafficAnalyzer_status(service_host)
        if trafficAnalyzer_status:
            # Create NGINX function to change the block for the one that enable the proxy access (Create NginxAPIDBController)
            if enable_proxy_access(service_host):
                body = "OK, proxy pass enabled"
                response.status_code = 200
            else:
                body = "Something was wrong"
                response.status_code = 500
        else:
            # Create NGINX function to change the block for the one that disable the proxy access (Create NginxAPIDBController)
            if disable_proxy_access(service_host):
                body = "OK, proxy pass disabled"
                response.status_code = 200
            else:
                body = "Something was wrong"
                response.status_code = 500
    else:
        body = "Please send all requiered information"
        response.status_code = 400
    return body

async def AddService(request, response):
    body = await request.json()
    service_name = body.get('host')
    actual_ip = body.get('actual_ip')
    port = body.get('port')
    if service_name and actual_ip and port:
        service_added = add_service(service_name, actual_ip, port)
        if service_added:
            message = "OK"
            response.status_code = 200
        else:
            message = "Something was wrong"
            response.status_code = 500
    else:
        message = "Please send all requiered information"
        response.status_code = 400
    return message

async def EditService(request, response):
    body = await request.json()
    service_host = body.get('host')
    new_host = body.get('new_host')
    ip = body.get('ip')
    new_ip = body.get('new_ip')
    port = body.get('port')
    new_port = body.get('new_port')
    if service_host and (new_host or new_ip or new_port):
        service_edited = edit_service(service_host, new_host, ip, new_ip, port, new_port)
        if service_edited:
            message = "Service was edited"
            response.status_code = 200
        else:
            message = "Something was wrong"
            response.status_code = 500
    else:
        message = "Please send all requiered information"
        response.status_code = 400
    return message

async def DeleteService(request, response):
    body = await request.json()
    service_name = body.get('service')
    if service_name:
        service_deleted = delete_service(service_name)
        if service_deleted:
            body = "Service was deleted"
            response.status_code = 200
        else:
            body = "Something was wrong"
            response.status_code = 500
    else:
        body = "Please send all requiered information"
        response.status_code = 400
    return body

async def DeleteRoute(request, response):
    body = await request.json()
    service = body.get('service')
    route = body.get('route')
    if service and route:
        route_deleted = delete_route(service, route)
        if route_deleted:
            body = "Route was deleted"
            response.status_code = 200
        else:
            body = "Something was wrong"
            response.status_code = 500
    else:
        body = "Please send all requiered information"
        response.status_code = 400
    return body;