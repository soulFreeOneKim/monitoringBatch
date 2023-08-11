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

        if self.CASE_NM == "CC_VGW" or self.CASE_NM == "CD_VGW":
            pt_dict['TIME'] = r'\[.*?\]'
            pt_dict['SOURCE_LINE'] = r'\(\s+\d+\)'
            pt_dict['LEVEL'] = r'INFO|ERROR'
            pt_dict['DETAIL_TXT'] = r' - .+'
            self.PATTERN_DICT = pt_dict
            
        elif self.CASE_NM == "CC_ADT" or self.CASE_NM == "CD_ADT" :
            pass
        else:
            pass

 
if __name__ == "__main__":    
    assor = AssemblyOrder("CC","VGW")
    print(assor.__str__())
    
    # "","type","detail",['r"\[[^\]]*\]"']



        


    

