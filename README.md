1.环境安装
==========
1.1 selenium安装
-------------
下载命令：selenium==3.141.0

1.2 WebDriver
---------------
无需下载，程序会自动下载兼容当前前浏览器的版本

1.3 支持浏览器
---------
Chrome、Firefox、Edge、Ie
默认启动本地设为默认浏览器的浏览器

1.5 allure
----------
测试报告解析工具

windows下载链接： https://github.com/allure-framework/allure2/releases/tag/2.7.0

mac可以命令行安装：

`brew install allure`

2.目录说明
=========

2.1 web_ui_automation_framework/page/
----------------------------
主要编写目录，存放page模型文件的目录

2.2 web_ui_automation_framework/page/yaml
---------------------------------
主要编写目录，存放yaml文件的目录，包括页面元素定位、环境变量、WebDriver初始化drvier变量

2.3 web_ui_automation_framework/testcase/
--------------------------------
主要编写目录，存放case的文件目录，依照pytest框架编写规范

2.4 web_ui_automation_framework/testcase/report
--------------------------------------
存储测试报告所需要的的目录

2.5 web_ui_automation_framework/images/
------------------------------
存储项目依赖的图片目录，如需要图片识别，一般将识别图片放在该目录下

2.6 web_ui_automation_framework/images/screenshot/
------------------------------------------
项目中对电脑屏幕截图存储的目录，包括主动截图、case失败自动截图、定位失败截图

2.7 web_ui_automation_framework/utils/
-----------------------------
存储工具方法的目录，例如装饰器、常用方法等

2.8 web_ui_automation_framework/record/
-----------------------------
存储电脑录像的目录

2.9 web_ui_automation_framework/copywriting/
----------------------------------
存储web页面文案的目录

2.10 web_ui_automation_framework/log/
------------------------------
网页 log 目录

3.命名规范
=============
3.1 元素定位抽取，yaml文件名与py文件名需要相同
----------------------------------------------
比如在page文件中的页面python文件为:**web_main_page.py**

那么在yaml文件存储该文件的元素定位yaml文件命名需要为: **web_main_page.yml**

在调用self.locator()方法时，会自动在yaml目录下寻找与当前文件同名的yaml文件去解析定位元素信息