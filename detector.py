import inspect
import pandas as pd
import os
import logging

FILE_ABSOLUTE_PATH  = os.path.abspath(__file__)
ROOT_DIR            = os.path.dirname(FILE_ABSOLUTE_PATH)
RESULT_DIR          = os.path.join(ROOT_DIR,"result")

class Detector:
    
    def __init__(self, LoginfoObj) -> None:
        self.LOGINFO = LoginfoObj
        self.DF      = pd.DataFrame()
        self.COLUMN_SEQUENCE = self.LOGINFO.COLUMN_SEQUENCE
        
        self.makeDataFrame()
    
    def makeDataFrame(self):   

        for name, value in inspect.getmembers(self.LOGINFO):
            if isinstance(value, list) and name != "COLUMN_SEQUENCE":
                self.DF[name] = pd.Series(value)
        
        self.DF = self.DF[self.COLUMN_SEQUENCE]        

    # ------------------------------------------------------------------------------------------------------- #
    # error 검출 rule
    # ------------------------------------------------------------------------------------------------------- #
    def errorExtractor(self):
        logging.info(f"[detector.py] 오류 검출 로직 시작")
        logging.info(f"[detector.py] 오류 검출 로직 종료")

    # ------------------------------------------------------------------------------------------------------- #
    # dataframe csv 로 저장(필요시 사용)
    # ------------------------------------------------------------------------------------------------------- #
    def loadCsv(self):
        logging.info(f"[detector.py] CSV 결과 저장")
        self.DF.to_csv(f"{RESULT_DIR}\\{self.LOGINFO.APP_DV_CD}_{self.LOGINFO.LOG_HOST_NM}_{self.LOGINFO.INPUT_FILE_NM}.csv", index=False)
        









