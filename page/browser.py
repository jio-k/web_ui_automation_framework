import os
from typing import TypeVar
import allure
from selenium import webdriver

from utils.setting import WEB_DRIVER_DIR
from utils.tools import env

S = TypeVar('S', bound='Browser')


class Browser(object):
    def __init__(self, driver: webdriver = None):
        self.driver = driver

    def start(self) -> S:
        """
        启动浏览器
        :return: 返回当前的实例对象
        """
        chrome_driver = os.path.join(WEB_DRIVER_DIR, 'chromedriver.exe')
        edge_driver = os.path.join(WEB_DRIVER_DIR, 'msedgedriver.exe')

        if env("browser") == "Chrome":
            self.driver = webdriver.Chrome(executable_path=chrome_driver)
        elif env("browser") == "Firefox":
            self.driver = webdriver.Firefox()
        elif env("browser") == "Edge":
            self.driver = webdriver.Edge(executable_path=edge_driver)
        elif env("browser") == "Ie":
            self.driver = webdriver.Ie()
        else:
            self.driver = webdriver.Chrome()
        self.driver.maximize_window()
        self.driver.get(env("url"))
        self.driver.implicitly_wait(env("implicitly_wait"))
        return self

    @allure.step("结束session")
    def stop(self) -> S:
        self.driver.quit()
        return self

    def login(self):
        """
        进入启动web的登录页面
        :return: 跳转到主页面
        """
        from page.login_page import LoginPage
        return LoginPage(self.driver)


if __name__ == '__main__':
    Browser().start()
