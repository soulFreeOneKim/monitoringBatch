from dataclasses import dataclass, field, asdict, astuple, make_dataclass
from typing import List

@dataclass
class AssemblyOrder: 
    CENTER_DV_CD : str 
    APP_DV_CD    : str 
    CASE_NM      : str = "" 
    PATTERN_DICT : dict = field(default_factory=dict)

    def __post_init__(self):
        if self.CASE_NM == "":
            self.CASE_NM = self.CENTER_DV_CD + "_" + self.APP_DV_CD

        self.patternMaker()
        
    def patternMaker(self):
        pt_dict = {}

        if self.CASE_NM == "CALL-CENTER_VGW" or self.CASE_NM == "DIRECT-CENTER_VGW":
            pt_dict['TIME'] = r'\[.*?\]'
            pt_dict['SOURCE_LINE'] = r'\(\s+\d+\)'
            pt_dict['LEVEL'] = r'INFO|ERROR'
            pt_dict['DETAIL_TXT'] = r'- (.*)'
            self.PATTERN_DICT = pt_dict
            # if "VSA" in sample_string or "VRS" in sample_string or "VDT" in sample_string:

        elif "VSA" in self.CASE_NM  or "VRS" in self.CASE_NM  or "VDT" in self.CASE_NM :
            pt_dict['TIME'] = r'(\d{2}:\d{2}:\d{2}\.\d{3})'
            pt_dict['LEVEL'] = r'\[\s*(INFO|ERROR|DEBUG)\s*\]'
            pt_dict['DETAIL_TXT'] = r'- (.*)'
            self.PATTERN_DICT = pt_dict            
          
        else:
            pass

 
if __name__ == "__main__":    
    assor = AssemblyOrder("CC","VGW")
    print(assor.__str__())
    


        


    

