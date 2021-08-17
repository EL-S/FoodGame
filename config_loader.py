with open('client.conf') as file:
    client_settings = {line.split(":")[0].strip():(":".join(line.split(":")[1:]).strip() if ":".join(line.split(":")[1:]).strip() not in ["True", "False"] else (True if (":".join(line.split(":")[1:]).strip() == "True") else False)) for line in file.readlines()}

with open('server.conf') as file:
    server_settings = {line.split(":")[0].strip():(":".join(line.split(":")[1:]).strip() if ":".join(line.split(":")[1:]).strip() not in ["True", "False"] else (True if (":".join(line.split(":")[1:]).strip() == "True") else False)) for line in file.readlines()}

def rewrite_client_config(settings):
    with open('client.conf', 'w') as file:
        for key,value in settings.items():
            file.write(f"{key}:{value}\n")
