from dataclasses import dataclass, field, asdict, astuple, make_dataclass
from typing import List

@dataclass
class LogInfo:
    INPUT_FILE_NM       : str = ""
    INPUT_FILE_PATH     : str = ""
    APP_DV_CD           : str = ""   
    LOG_HOST_NM         : str = ""
    CENTER_DV_CD        : str = ""
    COLUMN_SEQUENCE     : List[str] = field(default_factory=list) 
    LOG_LINE            : List[str] = field(default_factory=list) 
    TIME                : List[str] = field(default_factory=list) 
    SOURCE_LINE         : List[str] = field(default_factory=list)     
    LEVEL               : List[str] = field(default_factory=list) 
    DETAIL_TXT          : List[str] = field(default_factory=list)     
    CALL_ID             : List[str] = field(default_factory=list) 
    ERROR_YN            : List[str] = field(default_factory=list)    

    def __post_init__(self):
        self.COLUMN_SEQUENCE = ['LOG_LINE', 'TIME', 'SOURCE_LINE', 'LEVEL', 'DETAIL_TXT','CALL_ID','ERROR_YN']
    

if __name__ == "__main__":    
    linfo = LogInfo()
    print(linfo)

    



