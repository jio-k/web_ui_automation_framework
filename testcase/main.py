import pytest
import sys

from utils.setting import REPORT_DIR

sys.path.append('../')  # noqa
from utils.camera_excel import CameraExcel
from utils.tools import push_env, get_now_time_num


def run_main():
    camera_excel = CameraExcel(case_id_column='B', result_column='E', sheet_index=0)
    push_env('excel_object', id(camera_excel))
    pytest.main(["-s", f"--alluredir={REPORT_DIR}/{get_now_time_num()}", "web_main_test.py"])

    print('*' * 30 + '开始测试' '*' * 30)
    run_main()


print("*" * 40 + "执行完毕" + "*" * 40)

run_main()
