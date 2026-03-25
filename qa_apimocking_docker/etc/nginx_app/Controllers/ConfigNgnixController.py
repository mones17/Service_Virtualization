import os

def add_route_to_server_block(server_name, route_path):
    # Get the base path of the current directory where the ConfigNgnixController.py file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the complete path to the "sites_available" directory
    sites_available_dir = os.path.abspath('/etc/nginx/sites-available')
    resources_dir = os.path.abspath(os.path.join(current_dir, "..", "Resources"))
    server_config_file = os.path.join(sites_available_dir, server_name)
    if os.path.exists(server_config_file):
        try:
            # The file server_name exists
            with open(server_config_file, "r") as f:
                # The previously saved configuration is stored in the variable "existing_config"
                existing_config = f.read()
            # Load the file where the skeleton for configuring a new block is located.
            location_block_nginx_config_file = os.path.join(resources_dir, "location_block.txt")
            if os.path.exists(location_block_nginx_config_file):
                with open(location_block_nginx_config_file, 'r') as file:
                    new_block = file.read()
            # The new configuration blocks is added to the existing saved configuration
            new_block = new_block.replace('{new_location}', route_path)
            existing_config = existing_config.replace('# {new_location_block}', new_block)
            with open(server_config_file, "w") as f:
                f.write(existing_config)
            os.system("nginx -s reload")
        except :
            return False   
    else:
        return False
    return True

def add_service(server_name, actual_ip, port):
    # Get the base path of the current directory where the ConfigNgnixController.py file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the complete path to the "sites_available" directory
    sites_available_dir = os.path.abspath('/etc/nginx/sites-available')
    resources_dir = os.path.abspath(os.path.join(current_dir, "..", "Resources"))
    server_config_file = os.path.join(sites_available_dir, server_name)
    if os.path.exists(server_config_file):
        return False
    else:
        try:
            # There is no existing configuration file for the server block. Create a new one
            default_nginx_config_file = os.path.join(resources_dir, "ngnix_default_config.txt")
            if os.path.exists(default_nginx_config_file):
                with open(default_nginx_config_file, 'r') as file:
                    data = file.read()
                data = data.replace('{ip_address_realAPI}', actual_ip)
                data = data.replace('{real_port}', port)
                data = data.replace('{upstream}', server_name + '.actual')
                data = data.replace('{server_name}', server_name)
                # Save the configuration file in the "sites_available" folder
                with open(server_config_file, "w") as f:
                    f.write(data)
                os.system("nginx -s reload")
        except :
           return False
    return True

def edit_service(host, new_host, ip, new_ip, port, new_port):
    sites_available_dir = os.path.abspath('/etc/nginx/sites-available')
    server_config_file = os.path.join(sites_available_dir, host)
    if os.path.exists(server_config_file):
        try:
            with open(server_config_file, "r") as f:
                existing_config = f.read()
            if new_ip and new_port:
                block_to_replace = "server " + ip + ":" + port + ";"
                new_block = "server " + new_ip + ":" + new_port + ";"
                existing_config = existing_config.replace(block_to_replace, new_block)
            elif new_ip and not new_port:
                block_to_replace = "server " + ip + ":" + port + ";"
                new_block = "server " + new_ip + ":" + port + ";"
                existing_config = existing_config.replace(block_to_replace, new_block)
            elif new_port and not new_ip:
                block_to_replace = "server " + ip + ":" + port + ";"
                new_block = "server " + ip + ":" + new_port + ";"
                existing_config = existing_config.replace(block_to_replace, new_block)
            if new_host:
                # This block is for changing the url in the configuration file
                block_to_replace = "https://" + host + ".actual; # default_block"
                new_block = "https://" + new_host + ".actual; # default_block"
                # This is for https
                existing_config = existing_config.replace(block_to_replace, new_block)
                # This is for http
                block_to_replace = "http://" + host + ".actual; # default_block"
                new_block = "http://" + new_host + ".actual; # default_block"
                existing_config = existing_config.replace(block_to_replace, new_block)
                # This block is for changing the upstream block
                upstream_to_replace = "upstream " + host + ".actual {"
                new_upstream = "upstream " + new_host + ".actual {"
                existing_config = existing_config.replace(upstream_to_replace, new_upstream)
                # This block is for changing the server_name block
                server_name_to_replace = "server_name  " + host + ";"
                new_server_name = "server_name  " + new_host + ";"
                # This is for https
                existing_config = existing_config.replace(server_name_to_replace, new_server_name)
                # This is for http
                existing_config = existing_config.replace(server_name_to_replace, new_server_name)
                # Rename the file
                new_server_config_file = os.path.join(sites_available_dir, new_host)  
                os.rename(server_config_file, new_server_config_file)  
                server_config_file = new_server_config_file
            with open(server_config_file, "w") as f:
                f.write(existing_config)
            os.system("nginx -s reload")
        except:
            return False
    else:
        return False
    return True

def delete_service(service_name):
    sites_available_dir = os.path.abspath('/etc/nginx/sites-available')
    server_config_file = os.path.join(sites_available_dir, service_name)
    if os.path.exists(server_config_file):
        try:
            os.remove(server_config_file)
            os.system("nginx -s reload")
        except :
            return False
    else:
        False
    return True

def delete_route(service, route):
    # Define the path to the Nginx configuration directory
    sites_available_dir = os.path.abspath('/etc/nginx/sites-available')
    # Construct the full path to the server configuration file
    server_config_file = os.path.join(sites_available_dir, service)
    # Check if the server configuration file exists
    if os.path.exists(server_config_file):
        try:
            # Read the existing configuration from the file
            with open(server_config_file, "r") as f:
                existing_config = f.readlines()
            # Initialize variables to track formatting
            inside_block = False
            indentation = ''
            # Initialize a list to store the modified content
            modified_content = []
            # Loop through lines in the existing configuration
            for line in existing_config:
                # Check if the line contains the start of a location block
                if f'location /{route} {{' in line:
                    inside_block = True 
                    indentation = line[:line.find('location')]
                    continue
                # Check if we are inside the location block and found the end
                if inside_block and '}' in line:
                    inside_block = False
                    continue
                # If not inside the location block or it hasn't ended yet, add the line
                if not inside_block:
                    modified_content.append(line)
            # Write the modified content back to the configuration file
            with open(server_config_file, 'w') as f:
                f.write(''.join(modified_content))
            # Reload Nginx to apply the changes
            os.system("nginx -s reload")
            return True
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            return False

    return False

def enable_proxy_access(server_name):
    # Get the base path of the current directory where the ConfigNgnixController.py file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the complete path to the "sites_available" directory
    sites_available_dir = os.path.abspath('/etc/nginx/sites-available')
    resources_dir = os.path.abspath(os.path.join(current_dir, "..", "Resources"))
    server_config_file = os.path.join(sites_available_dir, server_name)
    if os.path.exists(server_config_file):
        try:
            # The file server_name exists
            with open(server_config_file, "r") as f:
                # The previously saved configuration is stored in the variable "existing_config"
                existing_config = f.read()
            block_to_replace = "https://" + server_name + ".actual; # default_block"
            http_to_replace = "http://" + server_name + ".actual; # default_block"
            new_block = "http://python; # default_block"
            # This should modify the first proxy pass block
            existing_config = existing_config.replace(block_to_replace, new_block)
            # This should modify the second proxy pass block
            existing_config = existing_config.replace(http_to_replace, new_block)
            with open(server_config_file, "w") as f:
                f.write(existing_config)
            print(existing_config)
            os.system("nginx -s reload")
        except :
            return False
    else:
        return False
    return True

def disable_proxy_access(server_name):
    # Get the base path of the current directory where the ConfigNgnixController.py file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the complete path to the "sites_available" directory
    sites_available_dir = os.path.abspath('/etc/nginx/sites-available')
    resources_dir = os.path.abspath(os.path.join(current_dir, "..", "Resources"))
    server_config_file = os.path.join(sites_available_dir, server_name)
    if os.path.exists(server_config_file):
        try:
            # The file server_name exists
            with open(server_config_file, "r") as f:
                # The previously saved configuration is stored in the variable "existing_config"
                existing_config = f.read()
            new_block = "https://" + server_name + ".actual; # default_block"
            http_block = "http://" + server_name + ".actual; # default_block"
            block_to_replace = "http://python; # default_block"
            # This should modify the first proxy pass block
            existing_config = existing_config.replace(block_to_replace, new_block)
            # This should modify the second proxy pass block
            existing_config = existing_config.replace(block_to_replace, http_block)
            with open(server_config_file, "w") as f:
                f.write(existing_config)
            print(existing_config)
            os.system("nginx -s reload")
        except :
            return False
    else:
        return False
    return True

# Example usage:
# delete_route("your_server_config.conf", "/your_route")
