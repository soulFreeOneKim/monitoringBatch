import os
import sys
import numpy as np
import pandas as pd
import configparser
import logging
import re
from logScanner import LogScanner
from logInfo import LogInfo
from logInfoGenerator import Generator
from assemblyOrder import AssemblyOrder
from detector import Detector

logging.basicConfig(format='%(asctime)s --- %(message)s', level=logging.INFO)

# ------------------------------------------------------------------------------------------------------- #
# 함수 정의  --------------------------------------------------------------------------------------------- #
# ------------------------------------------------------------------------------------------------------- #

def getFileName(filepath):
    path_element = filepath.split("\\")
    return path_element[-1]

def filteringPath(file_path, app_dv_cd_list):
    app_dv_cd_list = [val.lower() for val in app_dv_cd_list]
    filteredPathList = [string for string in file_path if any(sub in string for sub in app_dv_cd_list)]
    logging.info(f"[monitoring.py] : filteredPathList : {filteredPathList}")
    return filteredPathList
    

FILE_ABSOLUTE_PATH  = os.path.abspath(__file__)
ROOT_DIR            = os.path.dirname(FILE_ABSOLUTE_PATH)
CONFIG_DIR          = os.path.join(ROOT_DIR,"config")
LOG_DIR             = os.path.join(ROOT_DIR,"logs")
INPUT_CHECK_DATE    = ""
INI_FILE_NM         = "fileInfo.ini"

logging.info(f"[monitoring.py] FILE_ABSOLUTE_PATH   : {FILE_ABSOLUTE_PATH}")
logging.info(f"[monitoring.py] ROOT_DIR             : {ROOT_DIR}")
logging.info(f"[monitoring.py] CONFIG_DIR           : {CONFIG_DIR}")
logging.info(f"[monitoring.py] LOG_DIR              : {LOG_DIR}")

# ------------------------------------------------------------------------------------------------------- #
# ini 파일 파싱 ------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------- #
config = configparser.ConfigParser()
config.read(f"{CONFIG_DIR}\{INI_FILE_NM}")

# ------------------------------------------------------------------------------------------------------- #
# 변수 선언
# ------------------------------------------------------------------------------------------------------- #
target_log_str                  = ""
target_app_dv_cd_list           = []
target_log_file_path            = []
target_log_dict                 = {}

# ------------------------------------------------------------------------------------------------------- #
# 로그 분석 대상 경로 및 정보, 특정 체크일자 확인
# ------------------------------------------------------------------------------------------------------- #
for section in config.sections():
    if section == 'LOG':
        for key in config[section]:
            if key == 'target':
                target_log_str = config[section][key] 
    elif section == 'INPUT':
        for key in config[section]:
            if key == 'date':
                INPUT_CHECK_DATE = config[section][key]

# ------------------------------------------------------------------------------------------------------- #
# INI 파일의 TARGET(로그 분석 대상 APP 구분) 추출
# ------------------------------------------------------------------------------------------------------- #
target_app_dv_cd_list = target_log_str.split(",")

# ------------------------------------------------------------------------------------------------------- #
# app 별 로그 경로 확인
# ------------------------------------------------------------------------------------------------------- #
for app in target_app_dv_cd_list:
    app_path_list = config[app + '.' +"PATH"]['PATH'].split('|')
    for value in app_path_list:
        target_log_file_path.append(value)      

# ------------------------------------------------------------------------------------------------------- #
# 특정일자 로그 조회시
# ------------------------------------------------------------------------------------------------------- #
logging.info(f"[monitoring.py] INPUT_CHECK_DATE : {INPUT_CHECK_DATE}")

if INPUT_CHECK_DATE != "":
    target_log_file_path = [item for item in target_log_file_path if 'YYYYMMDD' in item]
    target_log_file_path = [item.replace("YYYYMMDD", INPUT_CHECK_DATE) for item in target_log_file_path]

# ------------------------------------------------------------------------------------------------------- #
# 현재일자 로그 조회시
# ------------------------------------------------------------------------------------------------------- #
else :
    target_log_file_path = [item for item in target_log_file_path if 'YYYYMMDD' not in item]

# ------------------------------------------------------------------------------------------------------- #
# 경로 필터링 후 로그 처리
# ------------------------------------------------------------------------------------------------------- #
for path in filteringPath(target_log_file_path, target_app_dv_cd_list):

    log_file_path   = LOG_DIR + path
    log_file_name   = getFileName(log_file_path)
    path_info       = path.split('\\')
    app_dv_cd       = path_info[1].upper()
    log_host_nm     = path_info[2].upper()

    # 센터 구분 필요없는 경우 default
    center_dv_cd = "COMMON"      

    # 센터별로 로그 다르게 쌓이는 경우에 한해..
    if len(path_info) == 5 : center_dv_cd = path_info[3].upper()
        
    logging.info(f"[monitoring.py] log_file_name    : {log_file_name}")
    logging.info(f"[monitoring.py] path_info        : {path_info}")
    logging.info(f"[monitoring.py] app_dv_cd        : {app_dv_cd}")
    logging.info(f"[monitoring.py] log_host_nm      : {log_host_nm}")
    logging.info(f"[monitoring.py] center_dv_cd     : {center_dv_cd}")

    assemblyorder   = AssemblyOrder(center_dv_cd, app_dv_cd)

    logscanner      = LogScanner(LOG_DIR + path, log_file_name, "UTF-8", assemblyorder.PATTERN_DICT)
    logscanner.read_lines()

    loginfo         = LogInfo(log_file_name, log_file_path, app_dv_cd, log_host_nm, center_dv_cd)

    generator       = Generator(logscanner.READ_LINE_LIST, assemblyorder.PATTERN_DICT, loginfo)
    generator.generate()
    
    detector        = Detector(generator.LOGINFO)

    logging.info(f"[monitoring.py] detector.DF : {detector.DF}")

    detector.errorExtractor()
    detector.loadCsv()