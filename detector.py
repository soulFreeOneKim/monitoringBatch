import inspect
import pandas as pd
import os
import logging
import datetime

FILE_ABSOLUTE_PATH  = os.path.abspath(__file__)
ROOT_DIR            = os.path.dirname(FILE_ABSOLUTE_PATH)
RESULT_DIR          = os.path.join(ROOT_DIR,"result")

def is_file_created_today(filename):
    if not os.path.exists(filename):
        return False
    
    file_creation_time = os.path.getctime(filename)
    file_creation_date = datetime.date.fromtimestamp(file_creation_time)
    
    return file_creation_date == datetime.date.today()

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
    # 업무 rule check
    # ------------------------------------------------------------------------------------------------------- #
    def jobProcessingChecker(self, DF):
        logging.info(f"[detector.py] jobProcessingChecker start ...")

        mode = 'w' if not is_file_created_today(f'{RESULT_DIR}/result.txt') else 'a'

        with open(f'{RESULT_DIR}/result.txt', mode) as file:
            file.write(f"[Checker Start] -------------------------------------------------- \n")
            file.write(f"HOST_NAME : {self.LOGINFO.LOG_HOST_NM}, APP_DV_CD : {self.LOGINFO.APP_DV_CD}, CENTER_DV_CD :{self.LOGINFO.CENTER_DV_CD} \n")

            # ----------------------------------------------------------------------------------------------- #
            # 로그별 체크 로직
            # ----------------------------------------------------------------------------------------------- #
            if self.LOGINFO.APP_DV_CD == "VGW" and self.LOGINFO.CENTER_DV_CD == "CALL-CENTER":
                pass
            elif self.LOGINFO.APP_DV_CD == "VGW" and self.LOGINFO.CENTER_DV_CD == "DIRECT-CENTER": 
                pass


            elif self.LOGINFO.APP_DV_CD == "VSA" and self.LOGINFO.CENTER_DV_CD == "COMMON":
                df = DF
                # --- db connection check
                df_dbconnection = df[df['DETAIL_TXT'].str.contains("HikariPool")]
                con_failed_cnt = len(df_dbconnection[df_dbconnection['DETAIL_TXT'].str.contains("failed")])
                file.write(f"DB CONNECTION FAIL COUNT : {con_failed_cnt}\n")
                if con_failed_cnt != 0:
                    file.write(f"[ERROR] ---------- DB CONNECTION FAIL OCCURRED ... \n")                   

                # --- EAI INTERFACE FAILED
                df = df[~df['DETAIL_TXT'].str.contains("HikariPool")]
                df = df[df['DETAIL_TXT'].str.contains("\[CC")]
                df = df[df['DETAIL_TXT'].str.contains("EAI REQUEST")]

                for eai_id in ['V3VBS00001','V3VBS00003','V3VBS00004','V3VBS00008','V3VBS00006','V3VBS00007']:
                    file.write(f"EAI INTERFACE ID : {eai_id}\n")
                    df_filtered = df[df['DETAIL_TXT'].str.contains(f"{eai_id}")]
                    df_filtered_req =  df_filtered[df_filtered['DETAIL_TXT'].str.contains('TOTAL INPUT DATA')]
                    df_filtered_res = df_filtered[df_filtered['DETAIL_TXT'].str.contains('RETURN CODE')]['DETAIL_TXT'].str.extract(r'RETURN CODE: (\d+)')
                    df_filtered_res_code = df_filtered[df_filtered['DETAIL_TXT'].str.contains('RETURN CODE')]['DETAIL_TXT'].str.extract(r'RETURN CODE: (\d+)')
                    eai_req_cnt = len(df_filtered_req)
                    eai_res_cnt = len(df_filtered_res) 
                    eai_res_200_cnt = len(df_filtered_res_code == "200")
                    file.write(f"{eai_id} REQUEST CNT       : {eai_req_cnt}\n")
                    file.write(f"{eai_id} RESPONSE CNT      : {eai_res_cnt}\n")
                    file.write(f"{eai_id} REPONSE:200 CNT   : {eai_res_200_cnt}\n")
                    if eai_req_cnt != eai_res_200_cnt:
                        file.write(f"{eai_id} RESPONSE FAILED OCCURRED ... \n")
                    file.write(f"[Checker End] -------------------------------------------------- \n")


            elif self.LOGINFO.APP_DV_CD == "VDT" and self.LOGINFO.CENTER_DV_CD == "COMMON": 
                df = DF
                # --- db connection check
                df_dbconnection = df[df['DETAIL_TXT'].str.contains("HikariPool")]
                con_failed_cnt = len(df_dbconnection[df_dbconnection['DETAIL_TXT'].str.contains("failed")])
                file.write(f"DB CONNECTION FAIL COUNT : {con_failed_cnt}\n")
                if con_failed_cnt != 0:
                    file.write(f"[ERROR] ---------- DB CONNECTION FAIL OCCURRED ... \n") 

                # --- EAI INTERFACE FAILED
                df = df[~df['DETAIL_TXT'].str.contains("HikariPool")]
                df = df[df['DETAIL_TXT'].str.contains("\[CD")]
                df = df[df['DETAIL_TXT'].str.contains("EAI REQUEST")]

                for eai_id in ['V3VB300001']:
                    file.write(f"EAI INTERFACE ID : {eai_id}\n")
                    df_filtered = df[df['DETAIL_TXT'].str.contains(f"{eai_id}")]
                    df_filtered_req =  df_filtered[df_filtered['DETAIL_TXT'].str.contains('TOTAL INPUT DATA')]
                    df_filtered_res = df_filtered[df_filtered['DETAIL_TXT'].str.contains('RETURN CODE')]['DETAIL_TXT'].str.extract(r'RETURN CODE: (\d+)')
                    df_filtered_res_code = df_filtered[df_filtered['DETAIL_TXT'].str.contains('RETURN CODE')]['DETAIL_TXT'].str.extract(r'RETURN CODE: (\d+)')
                    eai_req_cnt = len(df_filtered_req)
                    eai_res_cnt = len(df_filtered_res) 
                    eai_res_200_cnt = len(df_filtered_res_code == "200")
                    file.write(f"{eai_id} REQUEST CNT       : {eai_req_cnt}\n")
                    file.write(f"{eai_id} RESPONSE CNT      : {eai_res_cnt}\n")
                    file.write(f"{eai_id} REPONSE:200 CNT   : {eai_res_200_cnt}\n")
                    if eai_req_cnt != eai_res_200_cnt:
                        file.write(f"[ERROR] ---------- {eai_id} RESPONSE FAILED OCCURRED ... \n")   
                    file.write(f"[Checker End] -------------------------------------------------- \n")

            elif self.LOGINFO.APP_DV_CD == "VRS" and self.LOGINFO.CENTER_DV_CD == "COMMON": 
                logging.info(f"55555")



        #logging.info(f"DataFrame : {self.DF}")

        logging.info(f"[detector.py] jobProcessingChecker ended")

    # ------------------------------------------------------------------------------------------------------- #
    # 에러 rule check
    # ------------------------------------------------------------------------------------------------------- #
    def errorExtractor(self, DF):
        logging.info(f"[detector.py] 오류 검출 로직 시작")
        logging.info(f"[detector.py] 오류 검출 로직 종료")

    # ------------------------------------------------------------------------------------------------------- #
    # dataframe csv 로 저장(필요시 사용)
    # ------------------------------------------------------------------------------------------------------- #
    def loadCsv(self):
        logging.info(f"[detector.py] CSV 결과 저장")
        self.DF.to_csv(f"{RESULT_DIR}\\{self.LOGINFO.APP_DV_CD}_{self.LOGINFO.LOG_HOST_NM}_{self.LOGINFO.INPUT_FILE_NM}.csv", index=False)
        









