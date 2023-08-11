import numpy as np
import pandas as pd
import os
import sys
from dataclasses import dataclass
from dataclasses import dataclass, field, asdict, astuple, make_dataclass
from typing import List



@dataclass
class LogScanner:

    TARGET_LOG_FILE_DIR     : str 
    TARGET_LOG_FILE         : str
    ENDCODING               : str = "UTF-8"
    READ_LINE_LIST          : List[str] = field(default_factory=list)    

    def read_lines(self) -> None:
        
        f = open(self.TARGET_LOG_FILE_DIR,"r",encoding=self.ENDCODING)

        self.READ_LINE_LIST = f.readlines()        
        f.close()
