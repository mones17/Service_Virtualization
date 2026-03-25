class client_menus:
    service_Menu = "1. What is a service?\n2. Why don't I see any services?\n3. How can I add services?"
    resources_Menu = "1. What is a resource?\n2. Why don't I see any resources?\n3. How can I add resources?\n4. What are API modes?\n5. How can I edit a resource?\n6. How can I delete a resource?"
    response_Menu = "1. What is a response?\n2. Why don't I see any responses?\n3. How can I add responses?\n4. What does 'comment' mean?\n5. How can I add a comment?\n6. How can I edit a comment?\n7. What does 'Accepted' mean?\n8. How can I change the value of 'Accepted'?"
class admin_menus:
    service_Menu = "1. What is a service?\n2. Why don't I see any services?\n3. How can I add services?\n4. How can I edit a service? \n5. How can I delete a service?\n6. How can I add users to a service?"
    resources_Menu = "1. What is a resource?\n2. Why don't I see any resources?\n3. How can I add resources?\n4. What are API modes?\n5. How can I edit a resource?\n6. How can I delete a resource?"
    response_Menu = "1. What is a response?\n2. Why don't I see any responses?\n3. How can I add responses?\n4. What does 'comment' mean?\n5. How can I add a comment?\n6. How can I edit a comment?\n7. What does 'Accepted' mean?\n8. How can I change the value of 'Accepted'?"
class client_Responses:
    service = {
        '1': """A service is an application that has been virtualized, which means it operates independently in a virtual environment. Within this service, you can find two key elements: the name by which it is identified and the host.\n
    The name is the designation given to this application, which distinguishes it from others within the system. On the other hand, the host is an essential part of the URL that allows us to access this product in a specific manner.""",
        '2': """Unfortunately, you cannot view any services at the moment, as you have not been granted the necessary permission. If you wish to gain access to any of our services, we invite you to contact an administrator of Solera Service Virtualizer (SSV), who will be happy to provide you with the necessary assistance to do so.""",
        '3': """If you wish to gain access to any of our services, we invite you to contact an administrator of Solera Service Virtualizer (SSV), who will be happy to provide you with the necessary assistance to do so.""",
    }

    resources = {
        '1': """A "resource" is one of the numerous access points (endpoints) available within the service. \nThe essence of these resources lies in the name by which they are identified and the path through which access to a specific endpoint can be achieved.""",
        '2': """At the moment, it is not possible to view any 'resource' because none has been registered for this service. To add one, please click on the 'Add Resource' button and complete the required information in the form, including the name by which it will be identified, the path to access that specific endpoint, and the corresponding method.""",
        '3': """To add one, please click on the 'Add Resource' button and complete the required information in the form, including the name by which it will be identified, the path to access that specific endpoint, and the corresponding method.""",
        '4': """The 'API modes' are the different ways in which SSV (Solera Service Virtualizer) can interact with each of the registered 'resources.' Here are the three modes:
    \n1.Transparent Mode: In this mode, all traffic arriving at the specific endpoint is directed to the expected host, and the response comes directly from that host. In other words, the interaction occurs directly with the original host without any additional interventions.
    \n2.Recording Mode: In this mode, all traffic arriving at the specific endpoint is sent to the expected host, but additionally, the response is stored in a database before being delivered. This allows for the recording and retention of a history of the received responses.
    \n3.Mocking Mode: In this mode, all traffic is intercepted, and the response comes from the responses previously stored in the database. In this case, the expected host no longer interacts, and the responses are obtained from the simulations saved in the database, facilitating the simulation of specific scenarios without affecting the original host.
    \nThese modes provide flexibility in how interactions with registered resources are managed, allowing for the adaptation of service behavior to specific needs and use cases.""",
        '5': """To edit a 'resource,' follow these steps:\n
    1.Click on the button to view the responses ({}) within the row of the 'resource' you want to edit.\n
    2.Once inside the response view, look for the three dots (...) at the top of the screen.\n
    3.Click on the three dots and select the 'Edit Resource' option.\n
    4.Fill out the required information in the editing form.\n
    5.Finally, click 'Submit' to save the changes.\n
    These steps will allow you to effectively modify the information and configuration of a 'resource.'""",
        '6': """To Delete a 'resource,' follow these steps:\n
    1.Click on the button to view the responses ({}) within the row of the 'resource' you want to edit.\n
    2.Once inside the response view, look for the three dots (...) at the top of the screen.\n
    3.Click on the three dots and select the 'Delete Resource' option.\n
    These steps will allow you to effectively modify the information and configuration of a 'resource.'""",
    }

    responseText = {
    '1': """A 'response' is a response that has been recorded and stored in the database after conducting a product run with the 'recording mode' enabled.\n All responses found in this record and marked as 'accepted' will be used later during the 'mocking mode.' In other words, responses accepted in the 'recording mode' become part of the simulated responses available for the 'mocking mode.'""",
    '2': """I understand that you can't see any 'response' at the moment because there hasn't been any product run in 'recording mode' yet.\n To record responses in the database, we need to change the mode to 'recording' and perform a product run in this mode. Please, we will proceed to change the mode and run it in 'recording mode'.""",
    '3': """To record responses in the database, we need to change the mode to 'recording' and perform a product run in this mode.\n Please, we will proceed to change the mode and run it in 'recording mode'.""",
    '4': """The "Comment" field is a feature designed to simplify the identification of various responses stored in the database.\n In this field, you can add any relevant information that helps identify the response quickly and easily. This additional information can be useful for labeling, categorizing, or describing responses, making it easier to search for and use them within the system.""",
    '5': """When a response has been recently added to the database, a button will appear in the column corresponding to that response.\n To add a comment to that response, simply click on the button, and you will be able to enter the comment in the designated field.""",
    '6': """When you already have a comment registered for a response, you will have the option to edit it. To do so, follow these steps:\n
1.Look for the button with a pencil icon associated with the comment you want to edit.\n
2.Click on the pencil button.\n
3.After clicking the pencil, an editing field will open where you can enter the new comment or make necessary edits.\n
4.Once you have entered the new comment or made the relevant edits, save the changes.\n
This way, you can update and modify comments for existing responses as needed.""",
    '7': """The 'Accepted' field is an important feature in the 'mocking mode' as it plays a crucial role in selecting responses. To enable the 'mocking mode' and allow it to consider a specific response, it is necessary to manually verify that response and mark it according to its validation status. The values that the 'Accepted' field can take are as follows:\n
True: This indicates that the response has been accepted as valid and can be used in the 'mocking mode' as an option.\n
False: It indicates that the response has been rejected as valid and will not be used in the 'mocking mode.'\n
Null: This means that the response has not been verified yet, and no decision has been made regarding its validity. In this state, the response will not be automatically considered for the 'mocking mode'.""",
    '8': """To change the value of the 'Accepted' field, follow these steps:\n
1.Click on the response you wish to update.\n
2.Scroll down in the response view until you reach the bottom.\n
3.At the bottom of the response view, you will find a button that allows you to modify the 'Accepted' status according to your needs.\n
4.Click on the corresponding button to change the value of 'Accepted' to 'True' or 'False' as necessary.\n
This process will allow you to update the acceptance status of the response in accordance with the specific requirements and verifications of your application or system.""",
}
    
class admin_Responses:
    service = {
        '1': """ADMIN: A service is an application that has been virtualized, which means it operates independently in a virtual environment. Within this service, you can find two key elements: the name by which it is identified and the host.
                    The name is the designation given to this application, which distinguishes it from others within the system. On the other hand, the host is an essential part of the URL that allows us to access this product in a specific manner.
                    """,
        '2': """ADMIN: I understand that currently, no services are being displayed, which may be because none have been registered in the system yet. To add a new service, follow these steps:\n
                    \t1.Click on 'Add Service.'\n
                    \t2.Complete the requested information, which includes:\n
                        \t\t-Name by which the service will be identified.\n
                        \t\t-Host, which is the part of the URL used to access the service.\n
                        \t\t-The IP address where the product is hosted.\n
                        -\t\tThe port on which the product is configured to operate.\n
                    \t3.Once you have entered this information, click 'Submit' to register the new service in the system.\n
                    This way, you can add a service and make it accessible in the system for further configuration and management.
                    """,
        '3': """ADMIN: To add a new service, follow these steps:\n
                    \t1.Click on 'Add Service.'
                    \t2.Complete the requested information, which includes:\n
                        \t\t-Name by which the service will be identified.\n
                        \t\t-Host, which is the part of the URL used to access the service.\n
                        \t\t-The IP address where the product is hosted.\n
                        \t\t-The port on which the product is configured to operate.\n
                    \t3.Once you have entered this information, click 'Submit' to register the new service in the system.\n
                    This way, you can add a service and make it accessible in the system for further configuration and management.
                    """,
        '4': """ADMIN: To edit an existing service, follow these steps:\n
                    \t1.Click on the service you want to edit from the list of services.\n
                    \t2.Then, look for the three dots (...) in the interface related to the service you selected.\n
                    \t3.Click on those three dots and select the 'Edit Service' option.\n
                    \t4.Modify the information you want to change, such as the name, host, IP address, or port, according to your needs.\n
                    \t5.Finally, make sure to click 'Submit' to save the changes you have made.
                    """,
        '5': """ADMIN: "To delete an existing service, follow these steps:\n
                    \t1.Click on the service you want to delete from the list of services.\n
                    \t2.Then, look for the three dots (...) in the interface related to the service you selected.\n
                    \t3.Click on those three dots and select the 'Delete Service' option."\n
                    """,
        '6': """ADMIN: To add permissions to a user, follow these steps:
                    \t1.Click on the service you want to edit from the list of services.
                    \t2.Then, look for the three dots (...) in the interface related to the service you selected.
                    \t3.Click on those three dots and select the 'Add user access' option.
                    \t4.Enter the name or email of the user you want to add.
                    \t5.Finally, click on the user you wish to add.
                    """,
    }

    resources = {
        '1': """ADMIN: A "resource" is one of the numerous access points (endpoints) available within the service. \nThe essence of these resources lies in the name by which they are identified and the path through which access to a specific endpoint can be achieved.""",
        '2': """ADMIN: At the moment, it is not possible to view any 'resource' because none has been registered for this service. To add one, please click on the 'Add Resource' button and complete the required information in the form, including the name by which it will be identified, the path to access that specific endpoint, and the corresponding method.""",
        '3': """ADMIN: To add one, please click on the 'Add Resource' button and complete the required information in the form, including the name by which it will be identified, the path to access that specific endpoint, and the corresponding method.""",
        '4': """ADMIN: The 'API modes' are the different ways in which SSV (Solera Service Virtualizer) can interact with each of the registered 'resources.' Here are the three modes:
                \n1.Transparent Mode: In this mode, all traffic arriving at the specific endpoint is directed to the expected host, and the response comes directly from that host. In other words, the interaction occurs directly with the original host without any additional interventions.
                \n2.Recording Mode: In this mode, all traffic arriving at the specific endpoint is sent to the expected host, but additionally, the response is stored in a database before being delivered. This allows for the recording and retention of a history of the received responses.
                \n3.Mocking Mode: In this mode, all traffic is intercepted, and the response comes from the responses previously stored in the database. In this case, the expected host no longer interacts, and the responses are obtained from the simulations saved in the database, facilitating the simulation of specific scenarios without affecting the original host.
                \nThese modes provide flexibility in how interactions with registered resources are managed, allowing for the adaptation of service behavior to specific needs and use cases.""",
        '5': """ADMIN: To edit a 'resource,' follow these steps:\n
                1.Click on the button to view the responses ({}) within the row of the 'resource' you want to edit.\n
                .Once inside the response view, look for the three dots (...) at the top of the screen.\n
                3.Click on the three dots and select the 'Edit Resource' option.\n
                4.Fill out the required information in the editing form.\n
                5.Finally, click 'Submit' to save the changes.\n
                These steps will allow you to effectively modify the information and configuration of a 'resource.'""",
        '6': """ADMIN: To Delete a 'resource,' follow these steps:\n
                1.Click on the button to view the responses ({}) within the row of the 'resource' you want to edit.\n
                2.Once inside the response view, look for the three dots (...) at the top of the screen.\n
                3.Click on the three dots and select the 'Delete Resource' option.\n
                These steps will allow you to effectively modify the information and configuration of a 'resource.'"""
                ,}

    responseText = {
    '1': """ADMIN: A 'response' is a response that has been recorded and stored in the database after conducting a product run with the 'recording mode' enabled. All responses found in this record and marked as 'accepted' will be used later during the 'mocking mode.' In other words, responses accepted in the 'recording mode' become part of the simulated responses available for the 'mocking mode.'""",
    '2': """ADMIN:I understand that you can't see any 'response' at the moment because there hasn't been any product run in 'recording mode' yet. To record responses in the database, we need to change the mode to 'recording' and perform a product run in this mode. Please, we will proceed to change the mode and run it in 'recording mode'.""",
    '3': """ADMIN:o record responses in the database, we need to change the mode to 'recording' and perform a product run in this mode. Please, we will proceed to change the mode and run it in 'recording mode'.""",
    '4': """ADMIN:The "Comment" field is a feature designed to simplify the identification of various responses stored in the database.\n In this field, you can add any relevant information that helps identify the response quickly and easily. This additional information can be useful for labeling, categorizing, or describing responses, making it easier to search for and use them within the system.""",
    '5': """ADMIN:When a response has been recently added to the database, a button will appear in the column corresponding to that response.\n To add a comment to that response, simply click on the button, and you will be able to enter the comment in the designated field.""",
    '6': """ADMIN:When you already have a comment registered for a response, you will have the option to edit it. To do so, follow these steps:\n
                1.Look for the button with a pencil icon associated with the comment you want to edit.\n
                2.Click on the pencil button.\n
                3.After clicking the pencil, an editing field will open where you can enter the new comment or make necessary edits.\n
                4.Once you have entered the new comment or made the relevant edits, save the changes.\n
                This way, you can update and modify comments for existing responses as needed.""",
    '7': """ADMIN:The 'Accepted' field is an important feature in the 'mocking mode' as it plays a crucial role in selecting responses. To enable the 'mocking mode' and allow it to consider a specific response, it is necessary to manually verify that response and mark it according to its validation status. The values that the 'Accepted' field can take are as follows:\n
                True: This indicates that the response has been accepted as valid and can be used in the 'mocking mode' as an option.\n
                False: It indicates that the response has been rejected as valid and will not be used in the 'mocking mode.'\n
                Null: This means that the response has not been verified yet, and no decision has been made regarding its validity. In this state, the response will not be automatically considered for the 'mocking mode'.""",
    '8': """ADMIN:To change the value of the 'Accepted' field, follow these steps:\n
                1.Click on the response you wish to update.\n
                2.Scroll down in the response view until you reach the bottom.\n
                3.At the bottom of the response view, you will find a button that allows you to modify the 'Accepted' status according to your needs.\n
                4.Click on the corresponding button to change the value of 'Accepted' to 'True' or 'False' as necessary.\n
                This process will allow you to update the acceptance status of the response in accordance with the specific requirements and verifications of your application or system."""
                ,}
    
common_questions =  {
        '1': """Solera Service Virtualizer (SSV) is a software tool or platform used in the field of service virtualization. Its main objective is to simulate and emulate services and systems in development, testing, and debugging environments. This allows developers and testers to test applications and systems in a controlled environment.
                    Service Virtualizer can create simulations of services, enabling development and testing teams to work independently of real system dependencies.\n Some key advantages of Service Virtualizer include:
                    -Dependency Isolation: It allows teams to work on components and services in isolation without relying on external systems or services that may not be available during testing.
                    -Accelerated Development: It facilitates faster development by removing constraints caused by external dependencies.
                    -Comprehensive Testing: It enables comprehensive and repeatable testing, including tests for edge cases and unusual situations.
                    In summary, Solera Service Virtualizer is an essential tool in software development and testing, helping ensure that applications and systems function effectively and reliably in various scenarios, while also reducing the time associated with testing in real-world environments.""",
        '2': """Solera Service Virtualizer (SSV) is a platform that operates in the field of service and system virtualization. Its main function is to simulate and emulate services and system components for use in development, testing, and debugging environments. Here is a general overview of how SSV works:\n
                    1.Service Registration: In SSV, the services you want to virtualize are registered. This involves defining the service's name, the host (the URL or address where the service is accessed), the IP address, and the port where the real service is hosted.\n
                    2.Resource Registration: For each service, the resources or endpoints you want to virtualize are registered. These resources represent the different functionalities or routes that can be accessed within the service.\n
                    3.API Modes: SSV offers different API modes that determine how it interacts with virtual and real resources. These modes include:\n
                        -Transparent Mode: In this mode, traffic is directed directly to the real host, and responses come from that host.\n
                        -Recording Mode: Traffic is sent to the real host, but responses are recorded and stored in SSV's database for later use.\n
                        -Mocking Mode: In this mode, SSV intercepts all traffic, and responses come from previously stored responses in the database. The real host no longer interacts in this mode.\n
                    4.Recorded Responses: When a service is executed in recording mode (Recording Mode), SSV records responses from the real service and stores them in its database. These responses can be used later in simulation mode (Mocking Mode).""",
        '3': """To start using Solera Service Virtualizer (SSV), follow these general steps:\n
                    1.Platform Access: Ensure that you have access to the SSV platform.\n
                    2.Log In: Log in to the SSV platform using the credentials provided by the system administrator.\n
                    3.Service Registration: Begin by registering the services you want to virtualize. This involves providing information about the service's name, host, IP address, and port where the real service is hosted.\n
                    4.Resource Registration: For each service, register the resources or endpoints you want to virtualize. Define the routes and methods that will be available for virtual resources.\n
                    5.API Mode Configuration: Decide how you want SSV to interact with virtual and real resources. Choose between Transparent Mode, Recording Mode, and Mocking Mode according to your needs.\n
                    6.Recording Responses: If you are using Recording Mode, execute the service to record responses from the real service in the SSV database.\n
                    7.Configuration of Comments and Acceptance: Add comments to recorded responses to easily identify them. Mark responses as 'accepted' or 'rejected' based on their validity.\n
                    8.Testing and Simulations: Use SSV to conduct tests and simulations of virtual services in a controlled environment. Verify that virtual services behave as expected and meet your application's requirements."
    """,}
cq_Menu = "1. What is SSV? \n2. How does SSV work?\n3. How can I start using SSV?"
main_Menu = "How can I assist you today?\n1. Common Questions\n2. Service\n3. Resources\n4. Response"