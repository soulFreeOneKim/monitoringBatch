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

def getFileName(filepath):
    path_element = filepath.split("\\")
    return path_element[-1]


logging.basicConfig(format='%(asctime)s --- %(message)s', level=logging.INFO)

file_absolute_path  = os.path.abspath(__file__)
root_dir            = os.path.dirname(file_absolute_path)
config_dir          = os.path.join(root_dir,"config")
log_dir             = os.path.join(root_dir,"logs")
ini_file_nm         = "fileInfo.ini"


logging.info(f"absolute_file_path : {file_absolute_path}")
logging.info(f"### root_dir : {root_dir}")
logging.info(f"config_dir : {config_dir}")
logging.info(f"log_dir : {log_dir}")



# ini 파일 파싱
config = configparser.ConfigParser()
config.read(f"{config_dir}\{ini_file_nm}")

target_log_str          = ""
target_log_list         = []
target_log_file_path    = []
target_log_dict         = {}

# 로그 분석 대상 경로 및 정보 만들기
for section in config.sections():
    if section == 'LOG':
        for key in config[section]:
            if key == 'target':
                target_log_str = config[section][key] 

target_log_list = target_log_str.split(",")
logging.info(f"target_log_list : {target_log_list}")

# app 별 로그 경로 확인
for app in target_log_list:
    print(f"app : {app}")
    app_path_list = config[app + '.' +"PATH"]['PATH'].split('|')
    for value in app_path_list:
        target_log_file_path.append(value)      

logging.info(f"target_log_file_path : {target_log_file_path}")

# 테스트
input_check_date = ""

# 특정일자 로그 조회시
if input_check_date != "":
    target_log_file_path = [item for item in target_log_file_path if 'YYYYMMDD' in item]
    target_log_file_path = [item.replace("YYYYMMDD", input_check_date) for item in target_log_file_path]

# 현재일자 로그 조회시
else :
    target_log_file_path = [item for item in target_log_file_path if 'YYYYMMDD' not in item]


for path in target_log_file_path:

    log_file_name       = getFileName(log_dir + path)

    scanner = LogScanner(log_dir + path, log_file_name)
    scanner.read_lines()

    #assemblyorder = AssemblyOrder("CC","VGW")
    assemblyorder = AssemblyOrder("CD","VGW")

    # loginfo = LogInfo("call_center_1.log", "VBSGW01P", "CC", "VGW")
    loginfo = LogInfo(log_file_name, "VGW", "VBSGW01P", "CD")

    generator = Generator(scanner.READ_LINE_LIST, assemblyorder.PATTERN_DICT, loginfo)

    detector = Detector(generator.LOGINFO)

    print(detector.DF)

    detector.errorExtractor()

    detector.loadCsv()