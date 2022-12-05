import configparser
import os
from pathlib import Path

# READ CONFIG FILE
lobj_parser = configparser.ConfigParser()
lstr_config_file_path = str(Path(__file__).parent.parent) + os.path.sep + "data" + os.path.sep + "config.ini"
lobj_parser.read(lstr_config_file_path)

# GET CONFIG VALUES
# PATHS
INPUT_PATH = lobj_parser.get('PATHS', 'INPUT_PATH')
INTERMEDIATE_OUTPUT_PATH = lobj_parser.get('PATHS', 'INTERMEDIATE_OUTPUT_PATH')
LEPTONICA_PATH = lobj_parser.get('PATHS', 'LEPTONICA_PATH')

# GENERAL
SAVE_INTERMEDIATE = lobj_parser.getboolean('GENERAL', 'SAVE_INTERMEDIATE')
LOGGING_LEVEL = lobj_parser.get('GENERAL', 'LOGGING_LEVEL')
CPU_CORES = lobj_parser.getint('GENERAL', 'CPU_CORES')
TEXT_BY_IMAGE_RATIO_THRESHOLD = lobj_parser.getfloat('GENERAL', 'TEXT_BY_IMAGE_RATIO_THRESHOLD')
REF_PAGES_TO_READ = lobj_parser.get('GENERAL', 'REF_PAGES_TO_READ')
