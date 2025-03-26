# IpLook
>Project done for Computer Networks discipline. The main goal of this project is to offer a visual representation of the path crossed by packets between servers and devices until the destination, as well as gathering some informations of the connections made between the servers and of the servers themself.

## Getting Started
From the project root path, run:

`$pip install -r requirements.txt`

`$sudo PYTHONPATH=$(pwd) $(which python3) src/integration_service.py`

> Create a .env file with the variable IPINFO_TOKEN = <your_token>