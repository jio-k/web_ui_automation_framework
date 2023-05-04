import _ctypes
import os

import allure
import pytest

from utils.setting import IMAGES_SCREENSHOT_DIR
from utils.tools import get_now_time_num, get_now_time_format, env, get_case_excel_dict


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    print(item, call)
    outcome = yield
    print(outcome.get_result(), "钩子函数输出结果")
    result = outcome.get_result()
    print(result.outcome, "用例结果")
    # print(type(item), "item")
    # print(call, "call")
    if result.outcome == 'failed':
        try:

            image = os.popen('adb shell screencap -p /sdcard/01.png').read()
            print(image, "image")
            file_name = get_now_time_num() + '.png'
            file_name_path = os.path.join(IMAGES_SCREENSHOT_DIR, file_name)
            with open(file_name_path, 'rb') as f:
                image_read = f.read()
            allure.attach(image_read, "用例失败后截图   {}".format(get_now_time_format()),
                          attachment_type=allure.attachment_type.PNG)
        except Exception as e:
            print("用例失败截图操作 报错")
            print(e)
    if result.when == 'call':

        case_to_excel = get_case_excel_dict()
        case_name = str(result).split(' ')[1].split('::')[-1].replace("'", '')
        print(case_name, 'case_name')
        if result.outcome == 'failed':
            result = 'fail'
        elif result.outcome == 'passed':
            result = 'pass'
        else:
            assert False
        if case_name in case_to_excel.keys():
            case_id = case_to_excel[case_name]['case_id']
            print(case_id, 'case_id')
            check = case_to_excel[case_name]['check']
            camera_excel = _ctypes.PyObj_FromPtr(env('excel_object'))
            camera_excel.inset_case_result(case_id, result, check)
