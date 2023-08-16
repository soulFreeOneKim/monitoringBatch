from dataclasses import dataclass, field, asdict, astuple, make_dataclass

@dataclass
class LogFile:
    FILE_SERVER_IP          : str = ""
    FILE_SERVER_HOST_NAME   : str = ""
    FILE_SERVER_ID          : str = ""
    FILE_SERVER_PW          : str = ""
    FILE_FULL_PATH          : str = ""
    FILE_NAME               : str = ""

if __name__ == "__main__":    
    logFile = LogFile()
    print(logFile)