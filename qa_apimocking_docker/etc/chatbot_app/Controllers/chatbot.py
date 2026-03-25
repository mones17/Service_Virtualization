from Resources.bot_Responses import *

class ChatBotAdmin:

    def __init__(self):
        self.menu_level = 0
        self.submenu_level = 0
        self.is_final_step = False
        self.menu_responses = {
            '1': self.CQ_menuOp,
            '2': self.service_menuOp,
            '3': self.resources_menu,
            '4': self.response_Menu,
        }
        self.submenu_responses = {
            '1': self.commonQuestions_answers,
            '2': self.services_answers,
            '3': self.resources_answers,
            '4': self.response_answers,
        }
    def process_admin_input(self, user_name, user_input):
        response = ""
        principal_menus = {
            "1": "Common Questions",
            "2": "Service",
            "3": "Resource",
            "4": "Response"
        }
        if not user_input.isnumeric():
            user_input = user_input.lower()
        if self.menu_level == 0:
            response = f"ADMIN: Hello {user_name}, how can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"
            self.menu_level = 1
        elif self.menu_level == 1:
            if user_input == 'restart':
                response = f"ADMIN: Hello {user_name}, how can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"
                self.menu_level = 1
            elif user_input == 'back':
                response = f"ADMIN: Hello {user_name}, how can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"
                self.menu_level = 1
            elif user_input in self.menu_responses:
                response = f"{principal_menus[user_input]}\n" + self.menu_responses[user_input]()
                self.submenu_level = user_input
                self.menu_level = 2
            else:
                response = "Invalid option. Please select an option from 1 to 4."
        elif self.menu_level == 2:
            if user_input == 'start':
                self.is_final_step = False
                response = f"Welcome back to the principal menu. Is there anything else I can help you with?\n{self.principal_menuOp()}"
                self.menu_level = 1
            elif user_input == 'restart':
                self.is_final_step = False
                response = f"ADMIN: Hello {user_name}, how can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"
                self.menu_level = 1
            elif user_input == 'back':
                if self.is_final_step:
                    response = f"{principal_menus[self.submenu_level]}\n" + self.menu_responses[self.submenu_level]()
                    self.menu_level = 2
                    self.is_final_step = False
                else:
                    response = f"ADMIN: Hello {user_name}, how can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"
                    self.menu_level = 1
            else:
                response = self.get_submenu_response(self.submenu_level, user_input)
        return response

    def get_submenu_response(self, submenu_level, user_input):
        submenu_responses = {
            '1': self.commonQuestions_answers,
            '2': self.services_answers,
            '3': self.resources_answers,
            '4': self.response_answers,
        }
        if submenu_level in submenu_responses:
            return submenu_responses[submenu_level](user_input)
        else:
            return "Invalid ask, please try again"

    def principal_menuOp(self):
        return main_Menu

    def CQ_menuOp(self):
        return cq_Menu

    def service_menuOp(self):
        return admin_menus.service_Menu

    def resources_menu(self):
        return admin_menus.resources_Menu

    def response_Menu(self):
        return admin_menus.response_Menu

    def commonQuestions_answers(self, commonQuestion_selected):
        response = ""
        cq_options = {
            '1': common_questions['1'],
            '2': common_questions['2'],
            '3': common_questions['3']
        }
        response = cq_options.get(commonQuestion_selected, "Opción no válida")
        response += "\n\nTo return to the Main Menu, type 'start'."
        self.is_final_step = True
        return response

    def services_answers(self, serviceQuestion_selected):
        response = ""
        srv_options = {
            '1': admin_Responses.service['1'],
            '2': admin_Responses.service['2'],
            '3': admin_Responses.service['3'],
            '4': admin_Responses.service['4'],
            '5': admin_Responses.service['5'],
            '6': admin_Responses.service['6']
        }
        response = srv_options.get(serviceQuestion_selected, "Invalid option. Please select an option from 1 to 4.")
        response += "\n\nTo return to the main Menu, type 'start'."
        self.is_final_step = True
        return response

    def resources_answers(self, resourcesQuestion_selected):
        response = ""
        rsc_options = {
            '1': admin_Responses.resources['1'],
            '2': admin_Responses.resources['2'],
            '3': admin_Responses.resources['3'],
            '4': admin_Responses.resources['4'],
            '5': admin_Responses.resources['5'],
            '6': admin_Responses.resources['6']
        }
        response = rsc_options.get(resourcesQuestion_selected, "Invalid option. Please select an option from 1 to 6.")
        response += "\n\nTo return to the Main Menu, type 'start'."
        self.is_final_step = True
        return response

    def response_answers(self, responseQuestion_select):
        responseAnswer = ""
        rps_options = {
            '1': admin_Responses.responseText['1'],
            '2': admin_Responses.responseText['2'],
            '3': admin_Responses.responseText['3'],
            '4': admin_Responses.responseText['4'],
            '5': admin_Responses.responseText['5'],
            '6': admin_Responses.responseText['6'],
            '7': admin_Responses.responseText['7'],
            '8': admin_Responses.responseText['8']
        }
        responseAnswer = rps_options.get(responseQuestion_select, "Invalid option. Please select an option from 1 to 8.")
        responseAnswer += "\n\nTo return to the main Menu, type 'start'."
        self.is_final_step = True
        return responseAnswer
    

class ChatBotClient:
    def __init__(self):
        self.menu_level = 0
        self.submenu_level = 0
        self.is_final_step = False
        self.menu_responses = {
            '1': self.CQ_menuOp,
            '2': self.service_menuOp,
            '3': self.resources_menu,
            '4': self.response_Menu,
        }
        self.submenu_responses = {
            '1': self.commonQuestions_answers,
            '2': self.services_answers,
            '3': self.resources_answers,
            '4': self.response_answers,
        }
    def process_client_input(self, user_name, user_input):
        response = ""
        principal_menus = {
            "1": "Common Questions",
            "2": "Service",
            "3": "Resource",
            "4": "Response"
        }
        if not user_input.isnumeric():
            user_input = user_input.lower()
        if self.menu_level == 0:
            response = f"CLIENT: Hello {user_name}, how can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"
            self.menu_level = 1
        elif self.menu_level == 1:
            if user_input == 'restart':
                response = f"CLIENT: Hello {user_name}, how can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"
                self.menu_level = 1
            elif user_input == 'back':
                response = f"CLIENT: Hello {user_name}, how can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"
                self.menu_level = 1
            elif user_input in self.menu_responses:
                response = f"{principal_menus[user_input]}\n" + self.menu_responses[user_input]()
                self.submenu_level = user_input
                self.menu_level = 2
            else:
                response = "Invalid option. Please select an option from 1 to 4."
        elif self.menu_level == 2:
            if user_input == 'start':
                response = f"Welcome back to the principal menu.\n{self.principal_menuOp()}"
                self.menu_level = 1
            elif user_input == 'restart':
                self.is_final_step = False
                response = f"CLIENT: Hello {user_name}, how can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"
                self.menu_level = 1
            elif user_input == 'back':
                if self.is_final_step:
                    response = f"{principal_menus[self.submenu_level]}\n" + self.menu_responses[self.submenu_level]()
                    self.menu_level = 2
                    self.is_final_step = False
                else:
                    response = f"CLIENT: Hello {user_name}, how can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"
                    self.menu_level = 1
            else:
                response = self.get_submenu_response(self.submenu_level, user_input)
        return response

    def get_submenu_response(self, submenu_level, user_input):
        submenu_responses = {
            '1': self.commonQuestions_answers,
            '2': self.services_answers,
            '3': self.resources_answers,
            '4': self.response_answers,
        }
        if submenu_level in submenu_responses:
            return submenu_responses[submenu_level](user_input)
        else:
            return "Invalid request, please try again and select the topic that works best for you."

    def principal_menuOp(self):
        return main_Menu
    def CQ_menuOp(self):
        return cq_Menu
    def service_menuOp(self):
        return client_menus.service_Menu
    def resources_menu(self):
        return client_menus.resources_Menu
    def response_Menu(self):
        return client_menus.response_Menu

    def commonQuestions_answers(self, commonQuestion_selected):
        response = ""
        cq_options = {
            '1': common_questions['1'],
            '2': common_questions['2'],
            '3': common_questions['3']
        }
        response = cq_options.get(commonQuestion_selected, "Opción no válida")
        response += "\n\nTo return to the Main Menu, type 'start'."
        self.is_final_step = True
        return response

    def services_answers(self, serviceQuestion_selected):
        response = ""
        srv_options = {
            '1': client_Responses.service['1'],
            '2': client_Responses.service['2'],
            '3': client_Responses.service['3'],
        }
        response = srv_options.get(serviceQuestion_selected, "Opción no válida")
        response += "\n\nTo return to the main Menu, type 'start'."
        self.is_final_step = True
        return response

    def resources_answers(self, resourcesQuestion_selected):
        response = ""
        rsc_options = {
        '1': client_Responses.resources['1'],
        '2': client_Responses.resources['2'],
        '3': client_Responses.resources['3'],
        '4': client_Responses.resources['4'],
        '5': client_Responses.resources['5'],
        '6': client_Responses.resources['6']
        }
        response = rsc_options.get(resourcesQuestion_selected, "Opción no válida")
        response += "\n\nTo return to the Main Menu, type 'start'."
        self.is_final_step = True
        return response

    def response_answers(self, responseQuestion_select):
        responseAnswer = ""
        rps_options = {
            '1': client_Responses.responseText['1'],
            '2': client_Responses.responseText['2'],
            '3': client_Responses.responseText['3'],
            '4': client_Responses.responseText['4'],
            '5': client_Responses.responseText['5'],
            '6': client_Responses.responseText['6'],
            '7': client_Responses.responseText['7'],
            '8': client_Responses.responseText['8']
        }
        responseAnswer = rps_options.get(responseQuestion_select, "Opción no válida")
        responseAnswer += "\n\nPara volver al Menú Principal, escribe 'start'."
        self.is_final_step = True
        return responseAnswer