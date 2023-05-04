import allure


@allure.feature("路由器网站UI自动化测试")
class TestWebMain:

    @allure.story("启动浏览器")
    def setup_class(self):
        pass

    @allure.story("结束session")
    def teardown_class(self):
        pass

    @allure.story("test")
    def test_01_test(self):
        pass
