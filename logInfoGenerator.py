import os
import re
import logging
from logInfo import LogInfo

class Generator:

    def __init__(self, read_file_list, pattern_dict, LogInfo) -> None:
        self.READ_FILE_LIST = read_file_list
        self.PATTERN_DICT = pattern_dict
        self.LOGINFO      = LogInfo
        self.generate()    
        

    def generate(self):
        for idx, line in enumerate(self.READ_FILE_LIST):
            self.LOGINFO.LOG_LINE.append(idx+1)
            for key, value in self.PATTERN_DICT.items():
                attr = key                
                search = re.search(value, line)
                if hasattr(self.LOGINFO, attr):
                    attribute_value = getattr(self.LOGINFO, attr)
                    attribute_value.append(search.group())        
                    line = line.replace(search.group(), "", 1)

if __name__ == "__main__":    
    print(1)
