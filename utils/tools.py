import time
from typing import NoReturn, Any
import yaml

from utils.setting import PAGE_YAML_ENVIRONMENT_PATH, PAGE_YAML_CASE_TO_EXCEL_PATH


def ts_info() -> int:
    """
    获取当前时间13位时间戳
    :return:13位调用时的时间戳
    """
    ts = int(round(time.time() * 1000))
    return ts


def get_now_time_num() -> str:
    """
    以数字格式获取当前时间，精确到秒
    :return: 当前时间
    """
    return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


def get_now_time_format() -> str:
    """
    以格式化输出当前时间，精确到秒
    :return: 当前时间
    """
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def env(key: str, file_path: str = PAGE_YAML_ENVIRONMENT_PATH) -> Any:
    """
    读取环境全局变量中的值
    :param key:  需要输入的key值
    :param file_path: 读取yaml文件的地址
    :return: 输入key 对应的value值
    """
    with open(file_path, encoding="utf-8") as f:
        env_info = yaml.safe_load(f)[key]
        frame_print(env_info, "env_info: {}".format(key))
    return env_info


def push_env(key: str, value: Any, file_path: str = PAGE_YAML_ENVIRONMENT_PATH) -> NoReturn:
    """
    向环境全局变量中修改或者增加值
    :param key: 修改或者增加的key值
    :param value: 修改或增加的value的值
    :param file_path: 读取yaml文件的地址
    :return: none
    """
    with open(file_path, encoding="utf-8") as f:
        env_info = yaml.safe_load(f)
        frame_print(env_info, "push_env_info: {}".format(key))
    env_info[key] = value
    with open(file_path, 'w', encoding="utf-8") as f:
        yaml.dump(env_info, f, sort_keys=False)


def countdown_to_num(countdown_text: str) -> int:
    """
    将倒计时文本转换更具体多少秒
    :param countdown_text: 格式以 00:00:01 结尾
    :return: 数字形式的时间 s
    """
    num = int(countdown_text[-2:])
    num = int(countdown_text[-5:-3]) * 60 + num
    num = int(countdown_text[-8:-6]) * 60 * 60 + num
    return num


def countdown_to_num2(countdown_text: str) -> int:
    """
    将倒计时文本转换更具体多少秒
    :param countdown_text: 格式以 00:01 结尾
    :param countdown_text:
    :return:
    """
    num = int(countdown_text[-2:])
    num = int(countdown_text[-5:-3]) * 60 + num
    return num


def frame_print(*args, level: str = None, file_path: str = PAGE_YAML_ENVIRONMENT_PATH) -> None:
    """
    控制框架打印级别
    :param args: 打印内容
    :param level: 打印级别 目前只有 debug（全部打印）
    :param file_path: 默认级别环境变量地址
    :return:
    """
    if level is None:
        with open(file_path, encoding="utf-8") as f:
            env_info = yaml.safe_load(f)['print_level']
        level = env_info
    if level == 'debug':
        print(get_now_time_format() + ': ', *args)
    else:
        pass


def time_format_to_num(time_format):
    time_num = None
    if 'AM' in time_format:
        time_num = time_format.replace(' AM', '')
        time_num_list = time_num.split(":")
        time_num = int(''.join([i if len(i) == 2 else '0' + i for i in time_num_list]))
    if 'PM' in time_format:
        time_num = time_format.replace(' PM', '')
        time_num_list = time_num.split(":")
        time_num = int(''.join([i if len(i) == 2 else '0' + i for i in time_num_list]))
        time_num = time_num + 1200 if time_num != '1200' else int(time_num)
    if ('AM' not in time_format) and ('PM' not in time_format):
        time_num = time_format.replace('at ', '')
        time_num_list = time_num.split(":")
        time_num = int(''.join([i if len(i) == 2 else '0' + i for i in time_num_list]))
    return time_num


def get_case_excel_dict(yml_path: str = PAGE_YAML_CASE_TO_EXCEL_PATH):
    """获取case与excel对应的信息"""
    with open(yml_path, encoding="utf-8") as f:
        case_to_excel_dict = yaml.safe_load(f)
    frame_print(case_to_excel_dict, "case_to_excel")
    return case_to_excel_dict


def is_num(character: str):
    """
    获取字符串是否为数字，可以带小数点
    """
    num_list = [str(i) for i in range(10)]
    num_list.append('.')
    if len(character) == 0:
        return False
    for s in character:
        if s not in num_list:
            return False
    if character[0] == '.' or character[-1] == '.':
        return False
    if character.count('.') > 1:
        return False
    return True
