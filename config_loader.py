with open('client.conf') as file:
    client_settings = {line.split(":")[0].strip():(":".join(line.split(":")[1:]).strip() if ":".join(line.split(":")[1:]).strip() not in ["True", "False"] else (True if (":".join(line.split(":")[1:]).strip() == "True") else False)) for line in file.readlines()}

with open('server.conf') as file:
    server_settings = {line.split(":")[0].strip():(":".join(line.split(":")[1:]).strip() if ":".join(line.split(":")[1:]).strip() not in ["True", "False"] else (True if (":".join(line.split(":")[1:]).strip() == "True") else False)) for line in file.readlines()}
