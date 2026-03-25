import xml.etree.ElementTree as ET
import json

def xmlValidation(atributo):  
    try:  
        ET.fromstring(atributo)
        return True  
    except:
        return False
    
def ContentTypeValidation(headers):
    if headers is not None:
        try:
            json_headers = json.loads(headers)
            if 'Content-Type' in headers:
                content_type = json_headers.get('Content-Type')
                if not content_type:
                   if 'content-type' in headers:
                       content_type = json_headers.get('content-type')
                   else:
                       content_type = 'No Content-Type'
            elif 'content-type' in headers:
                content_type = json_headers.get('content-type')
            else:
                content_type = 'No Content-Type'
        except json.JSONDecodeError:
            content_type = 'json'
    else:
        content_type = 'json'
    return content_type