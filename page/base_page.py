import inspect
import os
import platform
import signal
import time
from typing import TypeVar, Union, List, Tuple
from PIL import Image, ImageDraw
import selenium.common
import yaml
import allure
from time import sleep
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait


from page.browser import Browser
from utils.decorator import find_handle
from utils.setting import IMAGES_SCREENSHOT_DIR, PAGE_YAML_DIR
from utils.tools import get_now_time_format, get_now_time_num, env, push_env, frame_print

S = TypeVar('S', bound='BasePage')
ENV_SCREENSHOT_LEVEL = env('screenshot_level')


class BasePage(Browser):
    by_mode_list = ['id', 'xpath', 'link text', 'partial link text', 'name', 'tag name',
                    'class name', 'css selector', '-windows uiautomation',
                    'accessibility id', '-image', '-custom']

    def find(self, by: Union[str, Tuple], location: str = None,
             replace_value: Union[str, tuple, None] = None, screenshot_level: str = ENV_SCREENSHOT_LEVEL) -> WebElement:
        """
        封装单元素定位方法
        :param by: 元素定位方式 str 参考webDriver源码中 BY 和 MobileBy
        :param location: 元素定位信息
        :param replace_value: 参数替换
        :param screenshot_level: 元素截图标记等级
        :return: 定位元素对象
        """
        if type(by) is tuple:
            by, location = by
        elif type(by) is str:
            if by not in BasePage.by_mode_list:
                by, location = self.locator(by, replace_value=replace_value, stack_num=2)
            else:
                if location is None:
                    raise ValueError('if "by" is positioning mode, parameter '
                                     '"location" needs to be passed in')
        else:
            raise ValueError('parameter "by" can only be string or tuple')
        frame_print(self.driver, 'driver')
        allure.attach("{} {}    {}".format(by, location, get_now_time_format()), "定位方式和定位信息、时间")
        element = self.find_ele(by, location)
        if screenshot_level == 'debug':
            self.debug_screenshot(element, f'debug_{get_now_time_num()}.png')
        return element

    @find_handle
    def find_ele(self, by: str, location: str) -> WebElement:
        return self.driver.find_element(by, location)

    def finds(self, by: str, location: str) -> Union[List[WebElement], List]:
        """
        封装多元素定位方法
        :param by: 元素定位方式 str 参考webDriver源码中 BY 和 MobileBy
        :param location: 元素定位信息
        :return: 定位元素组对象
        """
        frame_print(self.driver, 'driver')
        allure.attach("{} {}    {}".format(by, location, get_now_time_format()), "定位方式和定位信息、时间")
        self.driver: WebElement
        elements = self.driver.find_elements(by, location)
        return elements

    def search_device(self, device_name: str) -> WebElement:
        """
        这个方法基于webDriver标准定位方法，Android和Ios都可以使用
        :param device_name: 设备昵称
        :return: 设备主页的page对象
        """
        frame_print(self.driver, 'search')
        element = self.find('xpath',
                            "//*[contains(@label,'{}') or contains(@text,'{}')]".format(device_name, device_name))
        return element

    def search_device_by_android(self, device_name: str) -> WebElement:
        """
        这个方法基于Android的Uiautomator原生定位方式，只有Android可以使用，相对于webDriver标准定位方式，效率更高
        :param device_name: 设备昵称
        :return: 设备主页的page对象
        """
        element = self.find('-android uiautomator',
                            'new UiScrollable(new UiSelector().scrollable(true).instance('
                            '0)).scrollIntoView(new UiSelector().text("%s").instance('
                            '0));' % device_name)

        frame_print('search_device_by_android')
        return element

    @allure.step("下拉屏幕")
    def down_refresh(self, pixel_value: int = 0, x1_offset: int = 0,
                     y1_offset: int = 100, x2_offset: int = 0, y2_offset: int = 0,
                     duration: int = 500, sleep_status: bool = False, sleep_num: Union[int, None] = None) -> S:
        """
        页面下拉刷新，默认从屏幕最上方，滑倒下方屏幕 3/4 的位置
        pixel_value: 滑动像素数
        x1_offset, y1_offset, x2_offset, y2_offset: 在默认坐标基础上的偏移量
        duration: 滑动时长
        sleep_status: 是否传入sleep()方法
        sleep_num: 如果传入sleep()方法，所睡眠的时间
        """
        size = self.driver.get_window_size()
        frame_print(size, 'size')
        self.driver.swipe(size['width'] // 2 - x1_offset, y1_offset,
                          size['width'] // 2 - x2_offset,
                          pixel_value if pixel_value != 0 else (size['height'] // 4) * 3 + y2_offset,
                          duration=sleep(sleep_num) if sleep_status else duration)  # noqa
        return self

    @allure.step("向上滑动，默认一屏")
    def wipe_up(self, pixel_value: int = 0, x1_offset: int = 0,
                y1_offset: int = 100, x2_offset: int = 0, y2_offset: int = 100,
                duration: int = 500, sleep_status: bool = False, sleep_num: Union[int, None] = None) -> S:
        """
        向上滑动，默认一屏，从屏幕中间最下面滑倒最上面
        pixel_value: 滑动像素数
        x1_offset, y1_offset, x2_offset, y2_offset: 在默认坐标基础上的偏移量
        duration: 滑动时长
        sleep_status: 是否传入sleep()方法
        sleep_num: 如果传入sleep()方法，所睡眠的时间
        """
        size = self.driver.get_window_size()
        frame_print(size, 'size')
        self.driver.swipe(size['width'] // 2 - x1_offset, size['height'] - y1_offset,
                          size['width'] // 2 - x2_offset,
                          (size['height'] - pixel_value) if pixel_value != 0 else y2_offset,
                          duration=sleep(sleep_num) if sleep_status else duration)  # noqa
        return self

    @allure.step("向左滑动")
    def left_slide(self, element: WebElement = None, x1_offset: int = 100,
                   y1_offset: int = 100, x2_offset: int = 0, y2_offset: int = 100,
                   duration: int = 500, sleep_status: bool = False, sleep_num: Union[int, None] = None) -> S:
        if element is None:
            size = self.driver.get_window_size()
        else:
            size = element.size
        frame_print(size, 'size')
        self.driver.swipe(size['width'] - x1_offset, size['height'] // 2 - y1_offset,
                          0 + x2_offset,
                          size['height'] // 2 - y2_offset,
                          duration=sleep(sleep_num) if sleep_status else duration)  # noqa
        return self

    @allure.step("睡眠等待")
    def wait(self, second_num: int) -> S:
        """
        睡眠时，每2s向webDriver发送一次“心跳”
        :param second_num: 睡眠时间
        :return: 停留在本页面
        """
        frame_print('wait {} s'.format(second_num))
        if second_num <= 3:
            time.sleep(second_num)
        else:
            second_num = second_num // 2
            for i in range(second_num):
                self.driver.page_source  # noqa
                time.sleep(2)
        return self

    def click_suggestions_name(self, suggestion_name: str) -> S:
        """
        点击web提供的默认设备命名
        :param suggestion_name: 设备名字
        :return:
        """
        self.find('xpath',
                  '//*[contains(@text,"{}")]'.format(suggestion_name, suggestion_name)).click()
        return self

    def screenshot(self, file_name: str, image_dir: str = IMAGES_SCREENSHOT_DIR) -> S:
        """
        封装截图方法
        :param file_name: 图片文件名字
        :param image_dir:  图片文件目录
        :return: 停留在本页
        """
        self.driver.get_screenshot_as_file(image_dir + file_name)
        with open(image_dir + file_name, 'rb') as f:
            image_read = f.read()
        allure.attach(image_read, file_name + " {}".format(get_now_time_format()),
                      attachment_type=allure.attachment_type.PNG)
        return self

    @allure.step("停止录像")
    def stop_record(self) -> S:
        os_type = platform.system()
        if os_type == "Windows":
            try:
                os.kill(0, signal.CTRL_C_EVENT)
            except KeyboardInterrupt:
                frame_print("win 停止录像")
        else:
            os.kill(env('record_pid'), signal.SIGINT)
        return self

    @staticmethod
    def locator(
            element_name: str,
            file_path: Union[str, None] = None,
            replace_value: Union[str, tuple, int, None] = None,
            stack_num: int = 1
    ):
        """
        从与调用该方法的的py文件同名的yaml文件中，解析ui的定位值
        :param stack_num: 文件列表序列
        :param replace_value: 如果定位中存在被定位值，输入替换对象
        :param element_name: 定位昵称 自妇产
        :param file_path: 默认为none 则解析同名文件，如果传入用传入的值
        :return: 元组，定位方式by + location
        """
        if file_path:
            file_path = file_path
        else:
            file_name_py = inspect.stack()[stack_num].filename
            file_name_yml = os.path.basename(file_name_py)[:-3] + ".yml"
            file_path = os.path.join(PAGE_YAML_DIR, file_name_yml)
        with open(file_path, encoding="utf-8") as f:
            elements_info: dict
            elements_info = yaml.safe_load(f)["locator"]
            element_info = elements_info[element_name]
        element_info_by = element_info["by"]
        element_info_location = element_info["location"]
        if replace_value:
            if type(replace_value) is tuple:
                element_info_location = element_info_location.format(*replace_value)
            else:
                element_info_location = element_info_location.format(replace_value)
        return element_info_by, element_info_location

    def attribute(self, attribute: str, file_path: Union[str, None] = None) -> str:
        """
        从与调用该方法的的py文件同名的yaml 文件中，解析ui的定位值及属性名，并返回属性值
        :param attribute: 属性名
        :param file_path: 默认为none 则解析同名文件，如果传入用传入的值
        :return: 属性值信息
        """
        if file_path:
            file_path = file_path
        else:
            file_name_py = inspect.stack()[1].filename
            frame_print("func_name_py ", file_name_py)
            file_name_yml = os.path.basename(file_name_py)[:-3] + ".yml"
            print("file_name_yaml ", file_name_yml)
            file_path = os.path.join(PAGE_YAML_DIR, file_name_yml)
            frame_print("访问的yaml文件地址 ", file_path)
        with open(file_path, encoding="utf-8") as f:
            # func_name = inspect.stack()[1].function
            # print(func_name, "func_name")
            attribute_info = yaml.safe_load(f)["locator"][attribute]
            frame_print("attribute_info", attribute_info)
        return self.find(*self.locator(attribute, stack_num=2)) \
            .get_attribute(attribute_info["attribute"])

    def get_element_in_page(self, element: Union[str, tuple],
                            time_out: int = 2, describe: Union[str, None] = None) -> (S, bool):
        """
        获取某个元素是否在当前页面内存在
        element: 元素名称或者元素locator
        """
        if type(element) is tuple:
            sign = element
        elif type(element) is str:
            sign = self.locator(element_name=element, stack_num=2)
        else:
            raise ValueError("Wrong type for parameter element")
        try:
            WebDriverWait(self.driver, timeout=time_out).until(
                expected_conditions.presence_of_element_located(sign))
            status = True
            frame_print("get_element_in_page: 发现{}元素".format(sign))
        except selenium.common.exceptions.TimeoutException:
            status = False
            frame_print("get_element_in_page: 等待{}s，未发现{}元素".format(time_out, sign))
        with allure.step("获取某元素是否在页面内" if describe is None else describe):
            self.screenshot('get_element_in_page' + get_now_time_num() + '.png')
            allure.attach("{} {}".format(sign, status), "获取方式及结果信息")
        return self, status

    def crash_record(self, now_page: str, mark: str) -> None:
        """
        当判断web发生崩溃时，在测试报告中记录该时间和时间
        :param now_page: 目前页面名字
        :param mark: 校验web是否崩溃 的标识 一般为页面独有的文案
        :return:
        """
        frame_print("【疑似发生崩溃】 当前实际页面与page对象校对失败 即将重启web")
        push_env("crash_count_num", env("crash_count_num") + 1)
        self.screenshot('AutomationsPage' + get_now_time_num() + '.png')
        allure.attach("{} 页面校验标识内容: {}".format(now_page, mark), "【疑似发生崩溃】 {}".format(get_now_time_num()))

    def debug_screenshot(self, ele: WebElement, file_name: str) -> None:
        """
        截取当前页面并标记传入元素的位置
        @param ele: 元素对象
        @param file_name 文件名
        return
        """
        img_dir = os.path.join(IMAGES_SCREENSHOT_DIR, file_name)

        # 截取手机当前页面图片
        self.driver.get_screenshot_as_file(img_dir)
        x1, y1 = ele.location['x'], ele.location['y']
        x2, y2 = ele.size['width'] + x1, ele.size['height'] + y1
        width, height = self.driver.get_window_size().values()
        # 读取图片对象
        im = Image.open(img_dir)
        im_width, im_height = im.size[0], im.size[1]
        # 获取左上角坐标x y跟屏幕的百分比
        percentage_x1 = x1 / width
        percentage_y1 = y1 / height
        # 获取右下角坐标x y跟屏幕的百分比
        percentage_x2 = x2 / width
        percentage_y2 = y2 / height  # 通过图片的宽跟高乘与百分比 得出保存下来的图片坐标
        left = [int(percentage_x1 * im_width), int(percentage_y1 * im_height)]
        right = [int(percentage_x2 * im_width), int(percentage_y2 * im_height)]
        frame_print(left, 'left')
        frame_print(right, 'right')
        draw = ImageDraw.Draw(im)

        # 根据左上角和右下角坐标定位一个矩形方框
        draw.line((left[0], left[1], right[0], left[1]), fill='red', width=5)
        draw.line((left[0], left[1], left[0], right[1]), fill='red', width=5)
        draw.line((left[0], right[1], right[0], right[1]), fill='red', width=5)
        draw.line((right[0], left[1], right[0], right[1]), fill='red', width=5)

        # 保存对图片的处理
        im.save(img_dir)

        # 二进制读取图片对象
        with open(img_dir, 'rb') as f:
            image_read = f.read()

        # 在allure报告内添加png格式图片附件
        allure.attach(
            image_read, f"debug.png", attachment_type=allure.attachment_type.PNG
        )
