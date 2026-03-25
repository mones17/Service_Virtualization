from fastapi import FastAPI, Request, HTTPException, Response
from Controllers.chatbot import ChatBotAdmin, ChatBotClient

app = FastAPI()
chatbotClient = ChatBotClient()
chatbotAdmin = ChatBotAdmin()

@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    raise HTTPException(status_code=400, detail=str(exc))

@app.post('/sv/chat/client')
async def client_chat(request: Request):
    data = await request.json()
    user_name = data.get('user_name', 'Guess')
    user_input = data.get('user_input', '')
    response = chatbotClient.process_client_input(user_name, user_input)
    return {'response': response}

@app.post('/sv/chat/admin')
async def admin_chat(request: Request):
    data = await request.json()
    user_name = data.get('user_name', 'Admin')
    user_input = data.get('user_input', '')
    response = chatbotAdmin.process_admin_input(user_name, user_input)
    return {'response': response}

@app.options("/{full_path:path}")
async def OptionsRequest( request: Request, response: Response):
    response.status_code=204