# IpLook
>Project done for Computer Networks discipline. The main goal of this project is to offer a visual representation of the path crossed by packets between servers and devices until the destination, as well as gathering some informations of the servers such as the provider.
![image](https://github.com/user-attachments/assets/6f49b106-4fc0-4f50-89b7-13164623a12a)

## Getting Started
1. Create a .env file with the variable `IPINFO_TOKEN = <your_token>`
    > **Note**: Go to https://ipinfo.io/ to create an account and get a token.

2. Create and activate a virtual environment to isolate the python dependencies:
    - `python3 -m venv venv`
    - `source venv/bin/activate`

3. From the project root path, run:
    
    - `pip install -r requirements.txt` to install the dependencies

    - `sudo PYTHONPATH=$(pwd) $(which python3) -m streamlit run src/app_mapa.py` to run the streamlit app

    - > **Alternatively** you can run only the integration service script to test it in terminal with: `sudo PYTHONPATH=$(pwd) $(which python3) src/integration_service.py`
