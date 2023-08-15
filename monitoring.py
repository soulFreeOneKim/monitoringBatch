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

# functions --------------------------------------------------------------------------------------------- #

def getFileName(filepath):
    path_element = filepath.split("\\")
    return path_element[-1]

def filteringPath(file_path, app_dv_cd_list):
    app_dv_cd_list = [val.lower() for val in app_dv_cd_list]
    filteredPathList = [string for string in file_path if any(sub in string for sub in app_dv_cd_list)]
    logging.info(f"[monitoring.py - filteringPath] : filteredPathList : {filteredPathList}")
    return filteredPathList
    
# ------------------------------------------------------------------------------------------------------- #


logging.basicConfig(format='%(asctime)s --- %(message)s', level=logging.INFO)

FILE_ABSOLUTE_PATH  = os.path.abspath(__file__)
ROOT_DIR            = os.path.dirname(FILE_ABSOLUTE_PATH)
CONFIG_DIR          = os.path.join(ROOT_DIR,"config")
LOG_DIR             = os.path.join(ROOT_DIR,"logs")
INI_FILE_NM         = "fileInfo.ini"


logging.info(f"absolute_file_path : {FILE_ABSOLUTE_PATH}")
logging.info(f"### ROOT_DIR : {ROOT_DIR}")
logging.info(f"CONFIG_DIR : {CONFIG_DIR}")
logging.info(f"LOG_DIR : {LOG_DIR}")



# ini 파일 파싱
config = configparser.ConfigParser()
config.read(f"{CONFIG_DIR}\{INI_FILE_NM}")

target_log_str                  = ""
target_app_dv_cd_list           = []
target_log_file_path            = []
target_log_dict                 = {}

# 로그 분석 대상 경로 및 정보 만들기
for section in config.sections():
    if section == 'LOG':
        for key in config[section]:
            if key == 'target':
                target_log_str = config[section][key] 


# VGW, VSA, VDT, VRS
target_app_dv_cd_list = target_log_str.split(",")


# app 별 로그 경로 확인
for app in target_app_dv_cd_list:
    print(f"app : {app}")
    app_path_list = config[app + '.' +"PATH"]['PATH'].split('|')
    for value in app_path_list:
        target_log_file_path.append(value)      

# 테스트
input_check_date = ""

# 특정일자 로그 조회시
if input_check_date != "":
    target_log_file_path = [item for item in target_log_file_path if 'YYYYMMDD' in item]
    target_log_file_path = [item.replace("YYYYMMDD", input_check_date) for item in target_log_file_path]

# 현재일자 로그 조회시
else :
    target_log_file_path = [item for item in target_log_file_path if 'YYYYMMDD' not in item]

# 경로 필터 후, 로그 추출
for path in filteringPath(target_log_file_path, target_app_dv_cd_list):

    log_file_path   = LOG_DIR + path
    log_file_name   = getFileName(log_file_path)
    path_info       = path.split('\\')
    app_dv_cd       = path_info[1].upper()
    log_host_nm     = path_info[2].upper()

    center_dv_cd = "COMMON"      

    if len(path_info) == 5 : center_dv_cd = path_info[3].upper()
        

    logging.info(f"log_file_name    : {log_file_name}")
    logging.info(f"path_info        : {path_info}")
    logging.info(f"app_dv_cd        : {app_dv_cd}")
    logging.info(f"log_host_nm      : {log_host_nm}")
    logging.info(f"center_dv_cd     : {center_dv_cd}")


    scanner = LogScanner(LOG_DIR + path, log_file_name)
    scanner.read_lines()

    assemblyorder   = AssemblyOrder(center_dv_cd, app_dv_cd)
    loginfo         = LogInfo(log_file_name, log_file_path, app_dv_cd, log_host_nm, center_dv_cd)
    generator       = Generator(scanner.READ_LINE_LIST, assemblyorder.PATTERN_DICT, loginfo)
    detector        = Detector(generator.LOGINFO)

    print(detector.DF)

    detector.errorExtractor()

    detector.loadCsv()