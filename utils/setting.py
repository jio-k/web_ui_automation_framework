import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MAC_DIR = os.path.join(BASE_DIR, 'data', 'genius_life_product_mac_key.xlsx')
DATA_DIR = os.path.join(BASE_DIR, 'data')
SC_SV_DIR = os.path.join(BASE_DIR, 'data', 'sv.xlsx')
AWS_DIR = os.path.join(BASE_DIR, DATA_DIR, 'aws')
LOG_DIR = os.path.join(BASE_DIR, 'log')
CONFIG_DIR = os.path.join(BASE_DIR, "data")
IMAGES_DIR = os.path.join(BASE_DIR, 'images')
PAGE_DIR = os.path.join(BASE_DIR, 'page')
WEB_DRIVER_DIR = os.path.join(BASE_DIR, 'web_driver')
REPORT_DIR = os.path.join(BASE_DIR, 'report')
UTILS_DIR = os.path.join(BASE_DIR, 'utils')

IMAGES_SCREENSHOT_DIR = os.path.join(IMAGES_DIR, 'screenshot')
PAGE_YAML_DIR = os.path.join(PAGE_DIR, 'YAML')
PAGE_YAML_ENVIRONMENT_PATH = os.path.join(PAGE_YAML_DIR, 'environment.yml')
PAGE_YAML_CASE_TO_EXCEL_PATH = os.path.join(PAGE_YAML_DIR, 'case_to_excel.yml')

