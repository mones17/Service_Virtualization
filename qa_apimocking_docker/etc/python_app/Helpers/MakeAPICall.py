import httpx
from fastapi import Request, Response

client = httpx.AsyncClient()
async def MakeCall(request:Request, globalResponse:Response, body_bytes):
    # Get URL
    service = request.headers.get('host')
    url = str(request.url)
    resource = url.split(service, 1)[1]
    url = f"https://{service}{resource}"
    # Get Method
    method = request.method
    # Get all headers
    headers = {}
    for header in request.headers:
        transformed_header = '-'.join([word.capitalize() for word in header.split('-')])
        headers.update({transformed_header:request.headers.get(header)})
    try:
        headers.pop('Content-Length')
    except :
        pass
    try:
        while True:
            method_kargs = {'url': url, 'headers':headers, 'timeout':50, 'data':body_bytes}
            callableMethod = None
            if method == "POST":
                callableMethod = client.post
            elif method == "PUT":
                callableMethod = client.put
            elif method == "PATCH":
                callableMethod = client.patch
            elif method == "DELETE":
                callableMethod = client.delete
            elif method == "GET":
                callableMethod = client.get
                method_kargs.pop('data')
            if callableMethod is not None:
                try:
                    moved = False
                    response = await callableMethod(**method_kargs)
                    contet_type = response.headers['Content-Type']
                    if 'text/html' in contet_type:
                        response_content = response.content.decode('utf-8')
                        if 'Object moved' in response_content:
                            moved = True
                    if (moved == True or response.status_code == 302) and 'Location' in response.headers:
                        url = response.headers['Location']
                        if url.startswith('/'):
                            url = f"https://{service}{url}"
                    else:
                        break
                except Exception as e:
                    continue
        #We have a response here
        if response is None:
            globalResponse.status_code=500
            return {"error": "No response gotten from the API"}
        if not(response.content):
            globalResponse.status_code=response.status_code
            return {"error": "Response has an empty body"}
        globalResponse.status_code=response.status_code
        return response
    except httpx.RequestError as e:
        print("Error en la solicitud:", str(e))
    except httpx.HTTPStatusError as e:
        print("Error de estado HTTP:", e)
        print("Codigo de estado:", e.response.status_code)
    except Exception as e:
        print("Error desconocido:", e)