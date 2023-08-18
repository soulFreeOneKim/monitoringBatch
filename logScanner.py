import numpy as np
import pandas as pd
import re
import os
import sys
import logging
from dataclasses import dataclass
from dataclasses import dataclass, field, asdict, astuple, make_dataclass
from typing import List



@dataclass
class LogScanner:

    TARGET_LOG_FILE_PATH     : str 
    TARGET_LOG_FILE          : str
    ENDCODING                : str = "UTF-8"
    PATTERN_DICT             : dict = field(default_factory=dict)
    READ_LINE_LIST           : List[str] = field(default_factory=list)
    
    def read_lines(self) -> None:
        
        f = open(f"{self.TARGET_LOG_FILE_PATH}{self.TARGET_LOG_FILE}","r",encoding=self.ENDCODING)

        lines = f.readlines()

        adjusted_lines = []
        buffer = ""

        for line in lines:

            stripped_line = line.strip()

            for key, value in self.PATTERN_DICT.items():
                attr = key                
                match = re.search(value, stripped_line)
                try:
                    result = match.group()
                except AttributeError:
                    result = ""
            
            # 패턴이 매칭 되는 경우
            if result:
                # 버퍼에 내용이 있으면 adjusted_lines에 추가
                if buffer:
                    adjusted_lines.append(buffer)
                    buffer = ""
                buffer += stripped_line
            else:
                # 태그가 없는 경우 버퍼에 라인 추가
                buffer += stripped_line

        # 마지막 버퍼 내용 추가
        if buffer:
            adjusted_lines.append(buffer)

        self.READ_LINE_LIST = adjusted_lines      

        f.close()
