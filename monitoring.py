import os
import sys
import numpy as np
import pandas as pd
import paramiko
import configparser
import logging
import re
from logScanner import LogScanner
from logInfo import LogInfo
from generator import Generator
from assemblyOrder import AssemblyOrder
from detector import Detector
from logfile import LogFile

logging.basicConfig(format='%(asctime)s ---> %(message)s', level=logging.INFO)

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

def makeLogFileObject(log_file_section_str_list: list):
    # 프로젝트 디렉토리 다운로드 경로 설정
    download_local_path_list = []
    for str_val in log_file_section_str_list:
        for section in config.sections():
            str_val_split = str_val.split(".")
            if section == f"{str_val_split[0]}.PATH":
                for key in config[section]:
                    if key == ENV_INFO.lower(): 
                        download_local_path_list.extend(config[section][key].split("|"))
    # 로그 파일 객체 생성
    logfile_object_list = []
    for section in config.sections():
        for file_info in log_file_section_str_list:
            if section == file_info:
                file_num                = 0
                app_dv_cd               = file_info.split(".")[0]
                download_path           = ""
                file_server_ip          = []
                file_server_host_name   = []
                file_server_id          = []
                file_server_pw          = []
                file_path               = []
                file_name_format        = []

                for key in config[section]:
                    if key == 'file_num'                : file_num              = config[section][key]
                    if key == 'file_server_ip'          : file_server_ip        = config[section][key].split("|")
                    if key == 'file_server_host_name'   : file_server_host_name = config[section][key].split("|")
                    if key == 'file_server_id'          : file_server_id        = config[section][key].split("|")
                    if key == 'file_server_pw'          : file_server_pw        = config[section][key].split("|")
                    if key == 'file_path'               : file_path             = config[section][key].split("|")
                    if key == 'file_name_format'        : file_name_format      = config[section][key].split("|")

                for i in range(int(file_num)):
                    file_name = ""
                    fmt_list = file_name_format[i].split(",")
                    for fmt in fmt_list : 
                        if INPUT_CHECK_DATE != "" and 'YYYYMMDD' in fmt:
                            file_name = fmt.replace("YYYYMMDD", INPUT_CHECK_DATE)
                            break
                        elif INPUT_CHECK_DATE == "" and 'YYYYMMDD' not in fmt:
                            file_name = fmt
                            break

                    for local_path_val in download_local_path_list:
                        if file_server_host_name[i].lower() in local_path_val and app_dv_cd.lower() in local_path_val :
                            if "call-center" in file_path[i] or "direct-center" in file_path[i]:
                                if "call-center" in file_path[i] and "call-center" in local_path_val:
                                    download_path = local_path_val
                                    break
                                elif "direct-center" in file_path[i] and "direct-center" in local_path_val:
                                    download_path = local_path_val
                                    break
                            else:
                                download_path = local_path_val
                                break

                    obj = LogFile(ENV_INFO,
                                  app_dv_cd,
                                  file_server_ip[i],
                                  file_server_host_name[i],
                                  file_server_id[i],
                                  file_server_pw[i],
                                  file_path[i],
                                  download_path,
                                  file_name
                                  )

                    logfile_object_list.append(obj)

    return logfile_object_list

def download_logfile(log_file_object_list: list):

    for obj in log_file_object_list:

        try:
            # ftp address
            host = obj.SERVER_IP                
            port = 22   
            userId = obj.SERVER_LOGIN_ID        
            password = obj.SERVER_LOGIN_PW   

            transprot = paramiko.transport.Transport(host,port)

            # ftp connect
            transprot.connect(username = userId, password = password)
            sftp = paramiko.SFTPClient.from_transport(transprot)


            localpath = f"{obj.DOWNLOAD_PATH}{obj.LOG_FILE_NAME}"
            remotepath = f"{obj.LOG_FILE_PATH}{obj.LOG_FILE_NAME}"

            # sftp에 파일 복사
            # sftp.put(localpath, remotepath)

            # 로컬에 파일 다운로드
            sftp.get(remotepath, localpath)

            # sftp 종료
            sftp.close()

        except paramiko.SSHException as e:
            logging.info(f"[monitoring.py] SSH error occurred: {e}")

# ------------------------------------------------------------------------------------------------------- #

FILE_ABSOLUTE_PATH  = os.path.abspath(__file__)
ROOT_DIR            = os.path.dirname(FILE_ABSOLUTE_PATH)
CONFIG_DIR          = os.path.join(ROOT_DIR,"config")
LOG_DIR             = os.path.join(ROOT_DIR,"logs")
INPUT_CHECK_DATE    = ""
INI_FILE_NM         = "fileInfo.ini"
ENV_INFO            = ""
IS_LOCAL            = ""

logging.info(f"[monitoring.py] FILE_ABSOLUTE_PATH   : {FILE_ABSOLUTE_PATH}")
logging.info(f"[monitoring.py] ROOT_DIR             : {ROOT_DIR}")
logging.info(f"[monitoring.py] CONFIG_DIR           : {CONFIG_DIR}")
logging.info(f"[monitoring.py] LOG_DIR              : {LOG_DIR}")

# ------------------------------------------------------------------------------------------------------- #
# ini 파일 파싱 ------------------------------------------------------------------------------------------ #
# ------------------------------------------------------------------------------------------------------- #
# config = configparser.ConfigParser()
config = configparser.ConfigParser(inline_comment_prefixes=(';')) # 주석은 ; 로
config.read(f"{CONFIG_DIR}/{INI_FILE_NM}")

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
            if key == 'target': target_log_str = config[section][key] 
    elif section == 'INPUT':
        for key in config[section]:
            if key == 'env' : ENV_INFO = config[section][key]
            if key == 'date': INPUT_CHECK_DATE = config[section][key]
            if key == 'is_local' : IS_LOCAL = config[section][key]

# ------------------------------------------------------------------------------------------------------- #
# INI 파일의 TARGET(로그 분석 대상 APP 구분) 추출
# ------------------------------------------------------------------------------------------------------- #
target_app_dv_cd_list = target_log_str.split("|")
logging.info(f"[monitoring.py] target_app_dv_cd_list : {target_app_dv_cd_list}")
# ------------------------------------------------------------------------------------------------------- #
# 다운로드 대상  로그 파일 처리
# ------------------------------------------------------------------------------------------------------- #
log_file_section_str_list   =   []
log_file_object_list        =   []

for app_dv_cd_val in target_app_dv_cd_list:
    log_file_section_str_list.append(f"{app_dv_cd_val}.{ENV_INFO}.LOGFILE")

logging.info(f"[monitoring.py] log_file_section_str_list : {log_file_section_str_list}")
log_file_object_list = makeLogFileObject(log_file_section_str_list)
logging.info(f"[monitoring.py] log_file_object_list : {log_file_object_list}")

# ------------------------------------------------------------------------------------------------------- #
# SFTP 접속 후 대상 로그 download - local 제외
# ------------------------------------------------------------------------------------------------------- #
if IS_LOCAL != 'Y':
    download_logfile(log_file_object_list)

# ------------------------------------------------------------------------------------------------------- #
# 분석대상 로그파일 객체에 대해서 처리
# ------------------------------------------------------------------------------------------------------- #
for obj in log_file_object_list:
    
    log_file_path   = LOG_DIR + obj.DOWNLOAD_PATH
    log_file_name   = obj.LOG_FILE_NAME
    path_info       = obj.DOWNLOAD_PATH.split('/')
    app_dv_cd       = obj.APP_DV_CD
    log_host_nm     = obj.SERVER_HOST_NAME

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

    logscanner      = LogScanner(log_file_path, log_file_name, "UTF-8", assemblyorder.PATTERN_DICT)
    logscanner.read_lines()

    loginfo         = LogInfo(log_file_name, log_file_path, app_dv_cd, log_host_nm, center_dv_cd)

    generator       = Generator(logscanner.READ_LINE_LIST, assemblyorder.PATTERN_DICT, loginfo)
    generator.generate()
    
    detector        = Detector(generator.LOGINFO)

    detector.jobProcessingChecker(detector.DF)
    #detector.errorExtractor(detector.DF)
    #detector.loadCsv()