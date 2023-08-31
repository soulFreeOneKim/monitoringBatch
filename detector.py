import inspect
import pandas as pd
import os
import logging
import datetime
from datetime import datetime, timedelta
# from datetime import datetime, date


FILE_ABSOLUTE_PATH  = os.path.abspath(__file__)
ROOT_DIR            = os.path.dirname(FILE_ABSOLUTE_PATH)
RESULT_DIR          = os.path.join(ROOT_DIR,"result")

def is_file_created_today(filename):
    if not os.path.exists(filename):
        return False
    
    file_creation_time = os.path.getctime(filename)
    file_creation_date = datetime.fromtimestamp(file_creation_time)
    
    return file_creation_date == datetime.today()

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
        current_date = datetime.now()
        current_filename = f"result_{current_date.strftime('%Y%m%d')}.txt"
        df = DF

        with open(f'{RESULT_DIR}/{current_filename}', 'a') as file:

            # 연월시분초 포맷으로 출력
            formatted_time = current_date.strftime('%Y-%m-%d %H:%M:%S')
            file.write(f"**************************************** {formatted_time} **************************************** \n")
            file.write(f"[Checker Start] -------------------------------------------------- \n")
            file.write(f"HOST_NAME : {self.LOGINFO.LOG_HOST_NM}, APP_DV_CD : {self.LOGINFO.APP_DV_CD}, CENTER_DV_CD :{self.LOGINFO.CENTER_DV_CD} \n")

            # ----------------------------------------------------------------------------------------------- #
            # 로그별 체크 로직
            # ----------------------------------------------------------------------------------------------- #
            try:
                if self.LOGINFO.APP_DV_CD == "VGW" and self.LOGINFO.CENTER_DV_CD == "CALL-CENTER":
                    df_regi = df[df['DETAIL_TXT'].str.contains(">>>") & df['DETAIL_TXT'].str.contains("kyobocc_")]
                    df_regi_check = df_regi['DETAIL_TXT'].str.split("Gateway:", expand=True)[1].str.split(",",expand=True).drop_duplicates()
                    df_regi_check.columns = ['line', 'action', 'status']
                    df_regi_check = df_regi_check.sort_values(by = ['line','action']).reset_index(drop=True)
                    df_regi_check['action'] = df_regi_check['action'].str.replace(" ","")
                    df_regi_check_groupby = df_regi_check.groupby('action').count()['line']

                    reged_cnt       = df_regi_check_groupby.loc['REGED']
                    register_cnt    = df_regi_check_groupby.loc['REGISTER']

                    file.write(f"reged_cnt : {reged_cnt} , register_cnt : {register_cnt} \n") 

                    pattern = r"\[(\w+)\] park\(\)"
                    sr_call_park_uuid = df[df['DETAIL_TXT'].str.contains("park\(\)")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    park_uuid_cnt = len(sr_call_park_uuid)

                    pattern = r"\[(\w+)\]"
                    sr_call_bridge_uuid = df[df['DETAIL_TXT'].str.contains("bridge execute")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    bridge_uuid_cnt = len(sr_call_bridge_uuid)

                    pattern = r"\[(\w+)\]" 
                    sr_call_originate_uuid = df[df['DETAIL_TXT'].str.contains("originate\(\) uuid")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    originate_uuid_cnt = len(sr_call_originate_uuid)

                    df_outbound_uuid = df[df['DETAIL_TXT'].str.contains("Found agent")]['DETAIL_TXT'].str.split("call_uuid: ",expand=True)[1]
                    outbound_call_uuid_cnt = len(df_outbound_uuid)

                    sr_inbound_uuid = sr_call_park_uuid[~sr_call_park_uuid.isin(df_outbound_uuid)]
                    inbound_call_uuid_cnt = len(sr_inbound_uuid)

                    pattern = r"\[(\w+)\]"
                    sr_active_uuid = df[df['DETAIL_TXT'].str.contains("] callstate: ACTIVE")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    active_uuid_cnt = len(sr_active_uuid)

                    pattern = r"\[(\w+)\]"
                    sr_early_uuid = df[df['DETAIL_TXT'].str.contains("] callstate: EARLY")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    early_uuid_cnt = len(sr_early_uuid)

                    pattern = r"\[(\w+)\]"
                    sr_hangup_uuid = df[df['DETAIL_TXT'].str.contains("] callstate: HANGUP")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    hangup_uuid_cnt = len(sr_hangup_uuid)

                    pattern = r"\[(\w+)\]"
                    sr_call_destory_uuid = df[df['DETAIL_TXT'].str.contains("destroy\(\)")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    destroy_uuid_cnt = len(sr_call_destory_uuid)

                    file.write(f"park_uuid_cnt          : {park_uuid_cnt}           \n")
                    file.write(f"early_uuid_cnt         : {early_uuid_cnt}          \n")
                    file.write(f"bridge_uuid_cnt        : {bridge_uuid_cnt}         \n")
                    file.write(f"originate_uuid_cnt     : {originate_uuid_cnt}      \n")
                    file.write(f"active_uuid_cnt        : {active_uuid_cnt}         \n")
                    file.write(f"hangup_uuid_cnt        : {hangup_uuid_cnt}         \n")
                    file.write(f"destroy_uuid_cnt       : {destroy_uuid_cnt}        \n")
                    file.write(f"inbound_call_uuid_cnt  : {inbound_call_uuid_cnt}   \n")
                    file.write(f"outbound_call_uuid_cnt : {outbound_call_uuid_cnt}  \n")
                    if hangup_uuid_cnt  / 2 != park_uuid_cnt:
                        file.write(f"[warning] hangup_uuid_cnt check \n")
                    if active_uuid_cnt  / 2 != park_uuid_cnt: 
                        file.write(f"[warning] active_uuid_cnt check \n")
                    if destroy_uuid_cnt / 2 != park_uuid_cnt:
                        file.write(f"[warning] destroy_uuid_cnt check \n")
                    file.write(f"[Checker End] -------------------------------------------------- \n")
                    
                elif self.LOGINFO.APP_DV_CD == "VGW" and self.LOGINFO.CENTER_DV_CD == "DIRECT-CENTER": 

                    pattern = r"\[(\w+)\] park\(\)"
                    sr_call_park_uuid = df[df['DETAIL_TXT'].str.contains("park\(\)")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    park_uuid_cnt = len(sr_call_park_uuid)

                    pattern = r"\[(\w+)\]"
                    sr_call_bridge_uuid = df[df['DETAIL_TXT'].str.contains("bridge execute")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    bridge_uuid_cnt = len(sr_call_bridge_uuid)

                    pattern = r"\[(\w+)\]" 
                    sr_call_originate_uuid = df[df['DETAIL_TXT'].str.contains("originate\(\) uuid")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    originate_uuid_cnt = len(sr_call_originate_uuid)

                    pattern = r"\[(\w+)\]"
                    sr_active_uuid = df[df['DETAIL_TXT'].str.contains("] callstate: ACTIVE")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    active_uuid_cnt = len(sr_active_uuid)

                    pattern = r"\[(\w+)\]"
                    sr_early_uuid = df[df['DETAIL_TXT'].str.contains("] callstate: EARLY")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    early_uuid_cnt = len(sr_early_uuid)

                    pattern = r"\[(\w+)\]"
                    sr_hangup_uuid = df[df['DETAIL_TXT'].str.contains("] callstate: HANGUP")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    hangup_uuid_cnt = len(sr_hangup_uuid)

                    pattern = r"\[(\w+)\]"
                    sr_call_destory_uuid = df[df['DETAIL_TXT'].str.contains("destroy\(\)")]['DETAIL_TXT'].str.extract(pattern).drop_duplicates()[0]
                    destroy_uuid_cnt = len(sr_call_destory_uuid)

                    file.write(f"park_uuid_cnt          : {park_uuid_cnt}           \n")
                    file.write(f"early_uuid_cnt         : {early_uuid_cnt}          \n")
                    file.write(f"bridge_uuid_cnt        : {bridge_uuid_cnt}         \n")
                    file.write(f"active_uuid_cnt        : {active_uuid_cnt}         \n")
                    file.write(f"hangup_uuid_cnt        : {hangup_uuid_cnt}         \n")
                    file.write(f"destroy_uuid_cnt       : {destroy_uuid_cnt}        \n")
                    if hangup_uuid_cnt  / 2 != park_uuid_cnt:
                        file.write(f"[warning] hangup_uuid_cnt check \n")
                    if active_uuid_cnt  / 2 != park_uuid_cnt: 
                        file.write(f"[warning] active_uuid_cnt check \n")
                    if destroy_uuid_cnt / 2 != park_uuid_cnt:
                        file.write(f"[warning] destroy_uuid_cnt check \n")

                    file.write(f"[Checker End] -------------------------------------------------- \n")


                elif self.LOGINFO.APP_DV_CD == "VSA" and self.LOGINFO.CENTER_DV_CD == "COMMON":
                    # --- DB CONNECTION CHECK
                    df_dbconnection = df[df['DETAIL_TXT'].str.contains("HikariPool")]
                    con_failed_cnt = len(df_dbconnection[df_dbconnection['DETAIL_TXT'].str.contains("failed")])
                    file.write(f"DB CONNECTION FAIL COUNT : {con_failed_cnt}\n")
                    if con_failed_cnt != 0:
                        file.write(f"[ERROR] ---------- DB CONNECTION FAIL OCCURRED ... \n")                   

                    # --- EAI INTERFACE CHECK
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
                    # --- DB CONNECTION CHECK
                    df_dbconnection = df[df['DETAIL_TXT'].str.contains("HikariPool")]
                    con_failed_cnt = len(df_dbconnection[df_dbconnection['DETAIL_TXT'].str.contains("failed")])
                    file.write(f"DB CONNECTION FAIL COUNT : {con_failed_cnt}\n")
                    if con_failed_cnt != 0:
                        file.write(f"[ERROR] ---------- DB CONNECTION FAIL OCCURRED ... \n") 

                    # --- EAI INTERFACE CHECK
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
                    # --- DB CONNECTION CHECK
                    df_dbconnection = df[df['DETAIL_TXT'].str.contains("HikariPool")]
                    con_failed_cnt = len(df_dbconnection[df_dbconnection['DETAIL_TXT'].str.contains("failed")])
                    file.write(f"DB CONNECTION FAIL COUNT : {con_failed_cnt}\n")
                    if con_failed_cnt != 0:
                        file.write(f"[ERROR] ---------- DB CONNECTION FAIL OCCURRED ... \n") 
                    
                    # --- EAI INTERFACE CHECK 
                    df = df[~df['DETAIL_TXT'].str.contains("HikariPool")]
                    df_reqResistDirect_req = df[ df['DETAIL_TXT'].str.contains("reqResistDirect") & df['DETAIL_TXT'].str.contains("paramBytes.length") ]
                    df_reqResistDirect_req['DV_CD'] = 'REQ:reqResistDirect'

                    df_responseHistory_req = df[ df['DETAIL_TXT'].str.contains("responseHistory") & df['DETAIL_TXT'].str.contains("paramBytes.length") ]
                    df_responseHistory_req['DV_CD'] = 'REQ:responseHistory'

                    df_eai_res = df[ df['DETAIL_TXT'].str.contains("makeEaiCommonHeader") & df['DETAIL_TXT'].str.contains("PRCS_RSLT_DVCD") ]
                    df_eai_res['DV_CD'] = 'RES:' + df_eai_res['DETAIL_TXT'].str.extract(r'\[(\d+)\]$')

                    df_eai_req_res = pd.concat([df_reqResistDirect_req, df_responseHistory_req,df_eai_res], axis=0).sort_values(by='LOG_LINE')
                    
                    eai_stat_err_cnt = {'reqResistDirect' : 0, 'responseHistory' : 0}
                    for idx , val in enumerate(df_eai_req_res['DV_CD']):
                        if val.split(":")[-1] == 'reqResistDirect' or val.split(":")[-1] == 'responseHistory':
                            continue
                        else:
                            if val.split(":")[-1] != "0":
                                eai_stat_err_cnt[df_eai_req_res['DV_CD'].values[idx-1].split(":")[-1]] = \
                                    eai_stat_err_cnt[df_eai_req_res['DV_CD'].values[idx-1].split(":")[-1]] + 1
                    
                    if eai_stat_err_cnt['reqResistDirect'] > 0 : file.write(f"[ERROR] ---------- [reqResistDirect] RESPONSE FAILED OCCURRED ... \n")
                    if eai_stat_err_cnt['responseHistory'] > 0 : file.write(f"[ERROR] ---------- [responseHistory] RESPONSE FAILED OCCURRED ... \n")
                    
                    file.write(f"[Checker End] -------------------------------------------------- \n")
            except (ValueError, KeyError) as e:
                logging.error(f"[detector.py] AN ERROR OCCURRED !! : {e}")

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
        









