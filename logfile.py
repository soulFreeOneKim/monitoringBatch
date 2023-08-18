import os
import logging
import configparser
from dataclasses import dataclass, field, asdict, astuple, make_dataclass

@dataclass
class LogFile:
    ENV_INFO           : str = ""
    APP_DV_CD          : str = ""
    SERVER_IP          : str = ""
    SERVER_HOST_NAME   : str = ""
    SERVER_LOGIN_ID    : str = ""
    SERVER_LOGIN_PW    : str = ""
    LOG_FILE_PATH      : str = ""
    DOWNLOAD_PATH      : str = ""
    LOG_FILE_NAME      : str = ""
    

if __name__ == "__main__":    
    print(f"111111111111")
    