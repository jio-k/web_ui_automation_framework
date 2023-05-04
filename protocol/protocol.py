import logging
import time
import xlrd


from utils.base import ProtocolAdditionalMethods
from utils.config_tool import Config,ConfigLoad
from utils.setting import SC_SV_PATH
from utils.base import get_protocol_short_name
from utils.common import get_uuid
from utils.log import Log

app_cfg = ConfigLoad(Config.APP)


logger = Log(__name__).getlog()



# Genius Life 环境url
app_url = 'https://app-api.hualaikeji.com:443'
device_url = 'https://device-api.hualaikeji.com:443'
upgrade_url = 'https://upgrade-api.hualaikeji.com:443'
iot_url = 'iot.hualaikeji.com:8883'
qa_url = 'https://qa-api.hualaikeji.com:443'

# 美国环境url
kivo_america_upgrade_url = 'https://upgrade-api.kivolabs.com:443'
kivo_america_app_url = 'https://app-api.kivolabs.com'
kivo_america_device_url = 'https://device-api.kivolabs.com'
kivo_america_iot_url = 'https://iot.kivolabs.com'
kivo_america_qa_url = 'https://api.kivolabs.com:443'

test_app_url = 'https://test-app-api.kivolabs.com'
test_device_url = 'https://test-device-api.kivolabs.com'

# sc
app_sc = '9add9c1f817a463caba1e32c4f5e03be'
device_sc = '9add9c1f817a463caba1e32c4f5e03be'


host_mapping = {
    #美国路由app端协议
    "kivo_america_app":{
        "test":"https://test-app-api.kivolabs.com",
        "beta":"https://beta-app-api.kivolabs.com",
        "official":"https://app-api.kivolabs.com",
    },
    #美国路由device端协议
    "kivo_america_device":{
        "test":"https://test-device-api.kivolabs.com",
        "beta":"https://beta-device-api.kivolabs.com",
        "official":"https://device-api.kivolabs.com"
    },
    # 获取验证码
    "qa": {
        "test": "https://test-api.kivolabs.com",
        "official": "https://api.kivolabs.com:443"
    }
}

def get_sc_sv(file_path=SC_SV_PATH,mode='app_sv'):
    '''从文件中读取sc/sv'''
    data = xlrd.open_workbook(file_path)
    #获取sheet页，分别为app_sv/device_sv
    sheet = ''
    if mode == 'app_sv':
        sheet ='app_sv'
    elif mode == 'device_sv':
        sheet = 'device_sv'
    table =data.sheet_by_name(sheet)
    nrows = table.nrows
    sc_sv_dic = {}
    for i in range(nrows):
        url = str(table.cell(i, 0).value)
        sv = str(table.cell(i, 1).value)
        sc_sv_dic.setdefault(url, sv)
    return sc_sv_dic

class AppHttpProtocol(ProtocolAdditionalMethods):
    '''App端协议类'''
    access_token = None
    def __init__(self,env,project_name=None):
        self.app_sc = app_sc
        if project_name:
            self.host = host_mapping[project_name][env]
        else:
            protocol_short_name = get_protocol_short_name(self.__class__.__name__)
            self.host = host_mapping[protocol_short_name][env]



    def user_login(self,user_name,password,verify_code=None,app_name=None,app_version=None,**file_data):
        '''
        用户登录
        :param password: [可选]密码(两遍Md5)
        :param verify_code: [可选]验证码
        :param app_name: 软件名称，如com.ismartalarm.HLHome
        :param app_version: 软件版本，如1.3.65
        '''
        url = "%s/app/v1/user/login"%self.host
        payload = {
            "user_name":user_name,
            "login_type":1,
            "password":password,
            "verify_code":verify_code,
            "phone_system_type":2,
            "phone_id":"0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_ver":"com.viloliving.vilo___1.0.29",
            "access_token":self.access_token,
            "app_name":"com.viloliving.vilo",
            "app_version":"1.0.29",
            "sc":self.app_sc,
            "ts":int(time.time()*1000)
        }
        return url,payload

    def user_regiest(self,verify_code,user_name,app_name=None,app_version=None,**fields_data):
        '''
        用户注册
        :param verify_code:验证码
        :param user_name:用户名.邮箱格式："123@abc.com"手机格式：13位手机号
        :param app_name:软件名称，如com.ismartalarm.HLHome
        :param app_version:软件版本，如1.3.65
        '''
        url = "%s/app/v1/user/register"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get('/app/v1/user/register'),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "user_name": "123456@qq.com",
            "account_type": 2,
            "verify_code": verify_code
        }
        return url,payload

    def get_binding_token(self, app_name=None, app_version=None, phone_id=None,**fields_data):
        '''
        获取组网Token
        :param app_name: 软件名称，如com.ismartalarm.HLHome
        :param app_version: 软件版本，如1.3.65
        :param phone_id: 手机的唯一标识
        '''
        url = "%s/app/v1/device/binding_token/get" %self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get('/app/v1/device/binding_token/get'),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2
        }
        return url,payload

    def send_verify_code(self,user_name=None,phone_id=None,**fields_data):
        '''
        发送验证码
        :param user_name: 用户名
        :param phone_id: 手机的唯一标识
        '''
        url = "%s/app/v1/user/security_code/get"%self.host
        payload = {
            "user_name": "liguo@hualaikeji.com",
            "reg_type": "0",  # 获取验证码类型 0-注册新用户 1-重置密码
            "phone_system_type": 2,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_ver": "com.viloliving.vilo___1.0.29",
            "sc": self.app_sc,
            "sv":get_sc_sv().get('/app/v1/user/security_code/get'),
            "ts": int(time.time() * 1000)
        }
        return url,payload

    def qateam_get_verify_code(self, account_name="liguo@hualaikeji.com", **field_data):
        """
        获取验证码（测试专用接口，仅限加入白名单的邮箱使用）
        白名单：liguo@hualaikeji.com、sunhaopeng@hualaikeji.com
        """

        url = '%s/qateam/v1/verify_code/get'%self.host

        payload = {
            "account_name": "wangzhenjie@hualaikeji.com",
            "ts": int(time.time() * 1000),
        }

        return url, payload

    def get_binding_result(self,app_name=None,app_version=None,**field_data):
        '''获取绑定结果（子设备绑定结果也是此接口）'''
        url = '%s/app/v1/device/binding_result/get'%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get('/app/v1/device/binding_result/get'),
            "app_ver":"com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "phone_system_type": 2,
            "binding_token":''
        }
        return url,payload

    def get_binding_sub_device_token(self,device_mac,app_name=None,app_version=None,phine_id=None,**field_data):
        '''
        获取组网子设备的Token.（子设备绑定）
        :param mac:主设备MAC，如camera的mac
        :param app_name:软件名称，如com.ismartalarm.HLHome
        :param app_version:软件版本，如1.3.65
        :param phine_id:手机的唯一标识
        '''
        url = "%s/app/v1/device/binding_sub_device_token/get"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get('/app/v1/device/binding_sub_device_token/get'),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac": device_mac,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "sub_device_product_model": "KIVO_MeshRouter"
        }
        return url,payload

    def get_device_info(self,device_mac,device_model,
                        device_setting_key_filter="del",**field_data):
        '''
        获取设备信息
        @param device_mac: 设备mac
        @param device_model: 设备型号
        @param device_setting_key_filter: [可选]要查询的设置配置的key 可以是部分key，如["1","2","3"]
        @param phone_system_type: 手机系统类型 1=IOS 2=Android
        @param field_data:
        @return:
        '''
        url = f"{self.host}/app/v1/device/device_info/get"
        payload = {
            "device_mac":device_mac,
            "device_model":device_model,
            "device_setting_key_filter":device_setting_key_filter,
            "phone_system_type": 2,
            "sc": self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time() * 1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
        }
        return url,payload

    def get_device_list(self,app_name=None,app_version=None,**field_data):
        '''
        获取设备列表,设备组列表
        :param app_name:软件名称，如com.ismartalarm.HLHome
        :param app_version:软件版本，如1.3.65
        '''
        url = "%s/app/v1/device/device_list/get"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get('/app/v1/device/device_list/get'),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2
        }
        return url,payload

    def get_router_external_list(self,device_mac="del",mesh_id=None,**field_data):
        '''
        获取外接设备列表信息
        :param device_mac: 设备mac作为筛选条件 不传则返回全部外接设备
        :param mesh_id:mesh网络id   获取首月设备列表接口获取
        :return:
        '''
        url = "%s/app/v1/router/external_list/get"%self.host
        payload = {
            "sc":self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts":int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac": device_mac,
            "mesh_id": mesh_id
        }
        return url,payload

    def get_router_external_info(self, device_mac=None, mesh_id=None,**field_data):
        '''
        获取外接设备详情
        :param device_mac: 外接设备mac
        :param mesh_id: mesh网络
        :param app_version:
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/router/external_info/get"%self.host
        payload = {
            "sc":self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac":device_mac,
            "mesh_id":mesh_id
        }
        return url,payload

    def device_delete(self,device_mac,app_name=None,app_version=None,**field_data):
        '''
        删除设备
        :param app_name:
        :param app_version:
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/device/delete"%self.host
        payload = {
            "sc":self.app_sc,
            "sv":get_sc_sv().get("/app/v1/device/delete"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac": device_mac
        }
        return url,payload

    def delete_router_external_guard(self,mesh_id,device_id,**field_data):
        '''
        删除外接设备家庭守护属性
        :param mesh_id:  mesh网络
        :param device_id: 外接设备id
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/router/external_guard/delete"%self.host
        payload = {
            "sc": self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "mesh_id": mesh_id,
            "device_id":device_id,
        }
        return url,payload

    def forget_password(self,username,new_password,verify_code,**field_data):
        '''
        ：忘记密码
        :param username: 用户名.Email
        :param new_password: 密码(两遍Md5)
        :param verify_code: 收到的验证码
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/user/password/forget"%self.host
        payload = {
            "sc":self.app_sc,
            "sv": get_sc_sv().get("/app/v1/user/password/forget"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "user_name":username,
            "new_password":new_password,
            "verify_code": "动态获取"
        }
        return url,payload

    def get_router_sub_list(self,device_mac, **field_data):
        '''
        获取子设备列表信息
        :param mac: 主设备mac
        :param field_data:
        :return:
        '''
        url = '%s/app/v1/router/sub_list/get'%self.host

        payload ={
            "sc":self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac": device_mac
        }
        return url, payload

    def get_device_property_list(self,device_mac,target_pid_list=None,**field_data):
        '''
        获取设备的属性列表
        :param mac: 设备mac
        :param target_pid_list: 返回的指定的pid，如果为空，则返回全部属性
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/device/property_list/get"%self.host
        payload = {
            "sc":self.app_sc,
            "sv": get_sc_sv().get("/app/v1/device/property_list/get"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts":int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac": device_mac,
            "device_model": "KIVO_MeshRouter",
            "target_pid_list":target_pid_list
        }
        return url,payload

    def set_property_list(self,device_mac,property_list=None,**field_data):
        '''
        设置一组属性
        :param mac: 设备mac
        :param property_list: 属性列表
        :return:
        '''
        url = "%s/app/v1/device/property_list/set"%self.host
        payload = {
            "sc":self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac":device_mac,
            "device_model": "KIVO_MeshRouter",
            "property_list":property_list
        }
        return url,payload

    def get_user_device_property(self,device_mac,**field_data):
        '''
        获取用户设备之间的属性关系
        :param mac: 设备mac
        :return:
        '''
        url = "%s/app/v1/user/device_property/get"%self.host
        payload = {
            "sc":self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts":int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac":device_mac
        }
        return url,payload


    def get_device_list_property_list(self,device_list,target_pid_list=''):
        '''
        获取多个设备的指定属性
        :param device_list: 设备列表
        :param target_pid_list: 返回的指定的pid，如果为空，则返回全部属性
        :return:
        '''
        url = "%s/app/v1/device_list/property_list/get"%self.host
        payload = {
            "sc": self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time() * 1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_list": device_list,
            "target_pid_list":target_pid_list
        }
        return url,payload

    def set_user_device_property(self,device_mac,property_list,**field_data):
        '''
        修改用户与设备之间的属性关系
        :param mac: 设备mac
        :param property_list: 属性列表
        :return:
        '''
        url = "%s/app/v1/user/device_property/set"%self.host
        payload = {
            "sc":self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts":int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac": device_mac,
            "property_list": property_list
        }
        return url,payload

    def set_router_external_info(self,device_mac,mesh_id,property_list,**field_data):
        '''
        设置外接设备信息
        :param mac: 外接设备mac
        :param mesh_id: mesh网络
        :return:
        '''
        url = "%s/app/v1/router/external_info/set"%self.host
        payload = {
            "sc":self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac": device_mac,
            "mesh_id":mesh_id,
            "property_list": property_list
        }
        return url,payload

    def run_action(self,instance_id,action_key,action_params,**field_data):
        '''
        执行动作
        :param instance_id: 动作执行者的唯一标识，默认"".如果执行者是设备，则填写设备mac.如果是场景，则填写场景ID.
        :param action_params: 动作参数。如果是延时：{"delay_second":60}。如果是设备：根据设备支持的协议填写。
        :param action_key: 动作的名称
        :param provider_key: 提供者唯一标识
        :param custom_string: 自定义字符串,云端不处理,原样返回
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/auto/action/run"%self.host
        payload = {
            "sc":self.app_sc,
            "sv": get_sc_sv().get("/app/v1/auto/action/run"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "provider_key": "KIVO_MeshRouter",
            "action_key": action_key,
            "instance_id": instance_id,
            "custom_string": "",
            "action_params": action_params
        }
        return url,payload

    def modify_device_info(self,device_mac,device_nickname=None,**field_data):
        '''
        修改设备信息
        :param mac: 设备mac
        :param device_nickname: 设备昵称
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/device/device_info/set"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get("/app/v1/device/device_info/set"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac":device_mac,
            "device_nickname": "测试2(主)",
            "device_logo_info": "",
            "device_timezone_city": "Asia/Shanghai"
        }
        return url,payload

    def set_category_info(self,device_mac,mesh_id,species_id=None,brand_id=None,**field_data):
        '''
        设置设备品牌信息

        :param mac: 外接设备mac
        :param species_id: 种类id未选择传0 ，例如种类选择手机 传手机的id
        :param brand_id: 品牌id未选择传0,例如 品牌小米 将id传给我
        :param mesh_id: mesh网络ID
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/system/category_info/set"%self.host
        payload = {
            "sc": self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_mac": device_mac,
            "mesh_id": mesh_id,
            "species_id": 1,
            "brand_id": 0,
            "brand_model_id": 0
        }
        return url,payload

    def get_category_list(self,category_list_type=None,category_type=None,
                          category_name=None,category_id=None,**field_data):
        '''
        获取分类列表
        :param category_list_type: 获取分类列表 0全部分类 1全部品牌
        :param category_type: 种类类别
        :param category_name: 种类名称
        :param category_id:  种类id
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/system/category_list/get"%self.host
        payload = {
            "sc":self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "category_list_type": "0",
            "category_type": "",
            "category_name": "",
            "category_id": 0
        }
        return url,payload

    def get_external_guard(self,device_id,mesh_id,**field_data):
        '''
        获取守护信息
        :param device_mac: 外接设备id
        :param mesh_id:  mesh网络
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/router/external_guard/get"%self.host
        payload = {
            "sc": self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "mesh_id": mesh_id,
            "device_id": device_id
        }
        return url,payload

    def add_external_guard(self,mesh_id,device_list):
        '''
        外接设备添加守护功能
        :param mesh_id:  mesh网络
        :param device_list: 添加守护的设备集合
        :return:

        e.g:"device_list": [
        {
            "device_id": "2047DAE1ADDA",
            "rules_list": [
                {
                    "time_rules": "1320|540|1111111",
                    "is_enable": 1
                }
            ]
        }
    ]
        '''
        url = "%s/app/v1/router/external_guard/add"%self.host
        payload = {
            "sc": self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "mesh_id": mesh_id,
            "device_list": device_list
        }
        return url,payload

    def set_external_guard(self,mesh_id,device_list,**field_data):
        '''
        外接设备设置守护功能
        :param mesh_id:  mesh网络
        :param device_list: 添加守护的设备集合
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/router/external_guard/set"%self.host
        payload = {
            "sc": self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "mesh_id": mesh_id,
            "device_list": device_list
        }
        return url,payload

    def get_block_list(self,mesh_id,**field_data):
        '''
        获取mesh网络黑名单列表
        :param mesh_id:
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/router/block_list/get"%self.host
        payload = {
            "sc": self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "mesh_id": mesh_id
        }
        return url,payload

    def delete_external_guard(self,mesh_id,device_id,rules_id_list='del',block_id_list='del',**field_data):
        '''
        删除外接设备家庭守护属性
        :param mesh_id:  mesh网络
        :param device_mac: 外接设备mac
        :param rules_id_list: 时间段集合 [时间段1ID,时间段2Id,]
        :param block_id_list: 黑名单集合 [黑名单1ID,黑名单2Id,]
        :return:
        '''
        url = "%s/app/v1/router/external_guard/delete"%self.host
        payload = {
            "sc":self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts":int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "mesh_id": mesh_id,
            "device_id": device_id,
            "rules_id_list":rules_id_list,
            "block_id_list":block_id_list
        }
        return url,payload

    def get_router_flow_list(self,mesh_id,begin_ts,end_ts,query_unit,exdevice_list=None,**field_data):
        '''
        获取路由器历史数据
        :param mesh_id:  mesh网络标识
        :param begin_ts:开始时间 如查询小时单位 则需要将时间戳精确到当天小时的整点 例子：一月24号11点
                        查询时间在周和月接口返回每天的值时  时间戳为每天的零点 例：一月23号 0点  查询周 传周天零点 到周一零点
                        查询月传 例如 查询1月份数据  开始时间 2021 年1月1号零点 到 2021年2月1号零点。
        :param end_ts: 结束时间  如查询小时单位 则需要将时间戳精确到当天小时的整点 例子：一月24号11点
                        查询时间在周和月接口返回每天的值时  时间戳为每天的零点 例：一月23号 0点
                        查询周 传周天零点 到周一零点    查询月传 例如 查询1月份数据  开始时间 2021 年1月1号零点 到 2021年2月1号零点。
        :param query_unit:  查询时间单位 0小时 1天 2周 3月
        :param exdevice_list: 需要查询某一个mesh网络下的外接设备的时候传此参数
        :return:
        '''
        url = "%s/app/v1/router/flow_list/get"%self.host
        payload = {
            "sc": self.app_sc,
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "mesh_id": mesh_id,
            "begin_ts": begin_ts,
            "end_ts": end_ts,
            "query_unit": query_unit
        }
        return url,payload

    def set_user_info(self,logo='',nickname='',**field_data):
        '''
        修改用户信息
        :param logo: 图片内容base64信息,不修改的时候传入""
        :param nickname: 用户昵称,不修改的时候传入""
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/user/user_info/set"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get("/app/v1/user/user_info/set"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2
        }
        return url,payload

    def get_message_list(self,begin_ts,end_ts,count,**field_data):
        '''
        获取消息列表
        :param begin_ts: 要查询的开始时间(时间戳)
        :param end_ts: 要查询的结束时间(时间戳)
        :param count: 要查询的日志数量,最多20条
        :return:
        '''
        url = "%s/app/v1/message_list/get"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": "4b36fee4597144088fb5510b4ca2ff41",
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "begin_ts": begin_ts,
            "end_ts": end_ts,
            "count": count
        }
        return url,payload

    def get_upgrade_list(self,**field_data):
        '''获取支持升级的设备'''
        url = "%s/app/v1/device/upgrade_list/get"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get("/app/v1/device/upgrade_list/get"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2
        }
        return url,payload

    def add_feedback(self,subject,comments,device_mac,common_contact,**field_data):
        '''
        增加问题反馈
        :param subject: 反馈主题
        :param comments: 反馈注释
        :param device_mac: 设备MAC
        :param common_contact: 常用联系方式
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/system/feedback/add"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get("/app/v1/system/feedback/add"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 1,
            "subject": subject,
            "comments": comments,
            "device_mac": device_mac,
            "common_contact": common_contact,
            "ticket_number": ""
        }
        return url,payload

    def delete_message_list(self,message_id_list,**field_data):
        '''
        删除消息列表
        :param message_id_list: 消息Id
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/message_list/delete"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get("/app/v1/message_list/delete"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "message_id_list": message_id_list
        }
        return url,payload

    def get_user_info(self,**field_data):
        '''
        获取用户信息
        :return:
        '''
        url = "%s/app/v1/user/user_info/get"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get("/app/v1/user/user_info/get"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token":self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2
        }
        return url,payload

    def change_password(self,old_password,new_password,**field_data):
        '''
        修改密码
        :param old_password: 原密码(两遍Md5)
        :param new_password: 新密码(两遍Md5)
        :param field_data:
        :return:
        '''
        url = "%s/app/v1/user/password/change"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get("/app/v1/user/password/change"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time()*1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "old_password": old_password,
            "new_password": new_password
        }
        return url,payload

    def delete_router_external(self,device_id,mesh_id):
        '''
        删除当前mesh网络下的外接设备关系
        :param device_id: 外接设备mac
        :param mesh_id: 网络id
        :return:
        '''
        url = "%s/app/v1/router/external/delete"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get("/app/v1/user/password/change"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time() * 1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "device_id":device_id,
            "mesh_id":mesh_id
        }
        return url,payload



    def add_isp_device(self,qr_info_list,**field_data):
        '''
        ISP设备入库
        @param qr_info_list:
        @param field_data:
        @return:
        '''

        url = "%s/app/v1/isp_device/add"%self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get("/app/v1/user/password/change"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time() * 1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "qr_info_list":qr_info_list
        }
        return url,payload

    def move_isp_mesh(self,move_info,**field_data):
        '''
        isp转移mesh网络
        @param mesh_id_list: mesh网络id ["mesh id1"]
        @param target_email: 转移的用户邮箱
        @param first_name: 姓
        @param last_name: 名
        @param address1: 地址信息1
        @param field_data:
        @return:
        move_info: [
                {
                    "mesh_id_list":mesh_id_list,
                    "target_users_info":{
                        "target_email":target_email,
                        "first_name":first_name,
                        "last_name":last_name,
                        "address1":address1
                    }
                }
            ]
        '''
        url = "%s/app/v1/isp_mesh/move" % self.host
        payload = {
            "sc": self.app_sc,
            "sv": get_sc_sv().get("/app/v1/user/password/change"),
            "app_ver": "com.viloliving.vilo___1.0.29",
            "ts": int(time.time() * 1000),
            "access_token": self.access_token,
            "phone_id": "0b865ea4-ee4c-4e8e-a473-bc95bf8b54e4",
            "app_name": "com.viloliving.vilo",
            "app_version": "1.0.29",
            "phone_system_type": 2,
            "move_info": move_info
        }
        return url, payload



class DeviceHttpProtocol(ProtocolAdditionalMethods):
    '''device端协议类'''
    def __init__(self,env,project_name=None):
        self.device_sc = device_sc
        if project_name:
            self.host = host_mapping[project_name][env]
        else:
            protocol_short_name = get_protocol_short_name(self.__class__.__name__)
            self.host = host_mapping[protocol_short_name][env]

    def get_r(self,mac,product_model=None,product_type=None,hardware_ver=None,firmware_ver=None,**field_data):
        '''
        验证设备是否存在,存在返回R.支持Camera.
        :param mac: 产品唯一编号(设备Mac),目前参数主体包括Camera 和 Dongle
        :param product_model: 产品型号
        :param product_type: 产品类型
        :param hardware_ver: 硬件版本
        :param firmware_ver: 固件版本
        :return:
        '''
        url = "%s/device/v1/authentication/r/get"%self.host
        payload = {
            "mac": "E4AAEC4402EE",
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "sc": self.device_sc,
            "sv": "8eae00531b934947be2cf6d63cdf6e1c",
            "ts": int(time.time()*1000)
        }
        return url,payload

    def verify_enr(self,mac,enr,r=None,verify_method=None,agent_device=None,
                   product_model=None,product_type=None,hardware_ver=None,firmware_ver=None,**field_data):
        '''
        需要传入全部R'.
        :param mac:
        :param enr:
        :param r:
        :param verify_method:
        :param agent_device:
        :param product_model:
        :param product_type:
        :param hardware_ver:
        :param firmware_ver:
        :param fields_data:
        :return:
        '''
        url = "%s/device/v1/authentication/enr/verify"%self.host
        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "sc": self.device_sc,
            "sv": get_sc_sv(mode='device_sv').get('/device/v1/authentication/verification_enr'),
            "ts": int(time.time()*1000)
        }
        return url,payload

    def device_binding(self,mac,enr,token,product_model=None,product_type=None, **field_data):
        """
        用户绑定使用Token与用户进行绑定
        :param mac: 产品唯一编号(设备Mac),目前参数主体包括Camera 和 Dongle
        :param enr: R’前16位。验证R'时需要传入全R' 获取R时传入""
        :param token: 绑定token
        :param product_model: 产品型号
        :param product_type: 产品类型
        """
        url = '%s/device/v1/binding'%self.host

        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "sc": self.device_sc,
            "ts": int(time.time()*1000),
            "token": token
        }
        return url, payload

    def add_master_device(self,mac,enr,**field_data):
        '''
        添加主设备
        :param mac:产品唯一编号(设备Mac)
        :param enr:R’前16位
        '''
        url = "%s/device/v1/router/mesh/set"%self.host
        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "ip": "192.168.58.1",
            "nick_name": "主设备",
            "property_list": [
                {"pid":"P5","pvalue":"0"},
                {"pid":"P2123","pvalue":"1"},
                {"pid":"P2129","pvalue":"0"},
                {"pid":"P2130","pvalue":"0"}
            ],
            "ts": int(time.time()*1000),
            "sc": self.device_sc,
            "sv":"b6807715a2df4587b138b81921350dda"
        }
        return url,payload

    def add_master_device_new(self,mac,enr,**field_data):
        '''
        添加主设备
        :param mac:产品唯一编号(设备Mac)
        :param enr:R’前16位
        '''
        url = "%s/device/v1/router/mesh_test/set"%self.host
        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "ip": "192.168.58.1",
            "nick_name": "主设备",
            "property_list": [
                {"pid":"P5","pvalue":"0"},
                {"pid":"P2123","pvalue":"1"},
                {"pid":"P2129","pvalue":"0"},
                {"pid":"P2130","pvalue":"0"}
            ],
            "ts": int(time.time()*1000),
            "sc": self.device_sc,
            "sv":"b6807715a2df4587b138b81921350dda"
        }
        return url,payload

    def add_sub_device(self,mac,enr,sub_mac,sub_enr,nick_name='del',ip='del',
                       sub_device_property_list='del',exdevice_list='del',**field_data):
        '''
        增加子设备及子外接设备
        :param mac:主设备mac
        :param enr:主设备enr
        :param sub_mac: 子设备mac
        :param sub_enr:子设备enr
        :param nick_name:设备昵称
        :param sub_device_property_list:设备属性
        :param sub_device_list:子设备列表
        '''
        url = "%s/device/v1/router/sub_device/add"%self.host
        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "sub_device_list": [
                {
                    "mac": sub_mac,
                    "enr": sub_enr,
                    "nick_name": nick_name,
                    "ip": ip,
                    "sub_device_property_list": sub_device_property_list,
                    "exdevice_list": exdevice_list,
                }
            ],
            "ts": int(time.time()*1000),
            "sc": self.device_sc,
            "sv": get_sc_sv(mode='device_sv').get('/device/v1/binding/sub_device')
        }
        return url,payload

    def add_external_device(self,mac,enr,nick_name='del',ip='del',product_model='del'
                            ,product_type='del',**field_data):
        '''
        添加主外接设备
        :param mac:主设备mac
        :param enr:主设备enr
        :param nick_name:名称
        :param ip:设备ip
        :param product_model:外接设备型号
        :param product_type:外接设备类型
        '''
        url = "%s/device/v1/router/external_device/add"%self.host
        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "exdevice_list": [
                {
                    "mac": "2047DAE1ADDA",
                    "nick_name": nick_name,
                    "ip": ip,
                    "product_model": product_model,
                    "product_type": product_type,
                    "exdevice_property_list": [
                        {
                        "pid": "P5",
                        "pvalue": "1"
                        },
                        {
                        "pid": "P2145",
                        "pvalue": "0"
                        },
                        {
                        "pid": "P2146",
                        "pvalue": "0"
                        },
                        {
                        "pid": "P2147",
                        "pvalue": "57"
                        },
                        {
                        "pid": "P2148",
                        "pvalue": "4"
                        },
                        {
                        "pid": "P2153",
                        "pvalue": "0"
                        }
                    ]
                }
            ],
            "ts": int(time.time()*1000),
            "sc": self.device_sc
        }
        return url,payload

    def get_iot_certificate(self,mac,enr,**field_data):
        '''
        获取IOT证书信息
        :param mac: 产品唯一编号(设备Mac),目前参数主体包括Camera 和 Dongle
        :param enr: R’前16位。验证R'时需要传入全R' 获取R时传入""
        :param field_data:
        :return:
        '''
        url = "%s/device/v1/iot_certificate/get"%self.host
        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "sc": self.device_sc,
            "sv": get_sc_sv(mode='device_sv').get('/device/v1/iot_certificate/get'),
            "ts": int(time.time()*1000)
        }
        return url,payload

    def get_log_address_list(self,mac,enr,**field_data):
        '''获取上传历史数据的地址的接口'''
        url = "%s/device/v1/router/log_address_list/get"%self.host
        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "file_relative_path": [],
            "sc": self.device_sc,
            "ts": int(time.time() * 1000)
        }
        return url,payload

    def set_device_info(self,mac,enr,ssid=None,ip=None,is_gateway=None,
                        is_temperature_humidity=None,nike_name=None,**field_data):
        '''
        更新设备信息
        :param mac:
        :param enr:
        :param ssid: 路由器的ssid,可选项
        :param ip: 内网的ip,可选项
        :param is_gateway: 是否具有网关功能,0=否 1=是,可选项
        :param is_temperature_humidity: 是否具有温湿度功能,0=否 1=是,可选项
        :return:
        '''
        url = "%s/device/v1/device_info/set"%self.host
        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "sc": self.device_sc,
            "sv": get_sc_sv(mode='device_sv').get('/device/v1/device_info/set'),
            "ts": int(time.time() * 1000)
        }
        return url,payload

    def get_resource_package(self,mac,enr,resource_package_key_list=None,**field_data):
        '''
        资源包获取
        :param mac:  产品唯一编号(设备Mac),目前参数主体包括Camera 和 Dongle
        :param enr:  R’前16位。验证R'时需要传入全R' 获取R时传入""
        :param resource_package_key_list: 资源包key_list
        :param field_data:
        :return:
        '''
        url = "%s/device/v1/resource_package/get"%self.host
        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "sc": self.device_sc,
            "sv": get_sc_sv(mode='device_sv').get('/device/v1/device_info/set'),
            "ts": int(time.time() * 1000)
        }
        return url,payload

    def get_device_external_guard(self,mac,enr=None,**field_data):
        '''
        获取家庭守护信息
        :param mac: 主设备mac
        :param enr: R’前16位。验证R'时需要传入全R' 获取R时传入""
        :return:
        '''
        url = "%s/device/v1/router/external_guard/get"%self.host
        payload = {
            "mac": mac,
            "enr": enr,
            "product_model": "KIVO_MeshRouter",
            "product_type": "Router",
            "hardware_ver": "1.0.0.0",
            "firmware_ver": "5.16.0.30",
            "sc": self.device_sc,
            "sv": get_sc_sv(mode='device_sv').get('/device/v1/device_info/set'),
            "ts": int(time.time() * 1000)
        }
        return url,payload


class QaHttpProtocol(ProtocolAdditionalMethods):
    '''测试工程师专用协议类（非业务）'''
    def __init__(self, env, project_name=None):
        if project_name:
            self.host = host_mapping[project_name][env]

        else:
            project_name = "qa"
            self.host = host_mapping[project_name][env]

    def qateam_get_verify_code(self, account_name="liguo@hualaikeji.com",verify_code_type: str = "del",
                               **field_data):
        """
        获取验证码（测试专用接口，仅限加入白名单的邮箱使用）
        verify_code_type  1=注册 2=修改密码 3=重置密码 4=添加账号
        """
        url = f'{self.host}/qateam/v1/verify_code/get'

        payload = {
            "account_name": "liguo@hualaikeji.com",
            "ts": int(time.time() * 1000)
        }

        return url, payload

class TestIspWeb(ProtocolAdditionalMethods):
    headers = {
        "Content-Type": "application/json",
        "H-SignatureMethod": "1",
        "H-AppKey": '5be027c460364fbcb6e54c762dd325ac',
        "H-AccessToken": "",
        "H-accesspath": "/vilo - inventory",
        "H-Signature": "动态计算"
    }

    app_secret = "7c4b3e35c94145d89c9374dcdfe9c40f"

    def __init__(self):
        pass

    def add_user_info(self,account_name,password,**field_data):
        '''
        获取token
        @param account_name: 用户名
        @param password: 密码
        @param field_data:
        @return:
        '''
        url = "https://test-usercenter-api.kivolabs.com/api/token/get"
        payload = {
            "app_id":"bfa842fc4d04a20508dc7ec61574",
            "data":{
                "account_name":account_name,
                "account_type":2,
                "password":password
            },
            "language":"en",
            "sc": "5be027c460364fbcb6e54c762dd325ac",
            "sv": "6e6fcfe8cfdf4622beb45b659491a6bd"
        }
        return url,payload

    def get_isp_device_list(self):
        '''
        获取设备
        @return:
        '''
        url = "https://test-isp-api.viloliving.com/isp/v1/device/device_list/get"
        payload = {
            "app_version":"1.0.29",
            "app_name":"com.viloliving.vilo",
            "request_id":get_uuid(),
            "data":{
                "filter_group":[],
                "order":"desc",
                "page_index":1,
                "page_size":100
            },
            "os_name":"5.0",
            "os_version":"5.0",
            "timestamp":int(time.time() * 1000)
        }
        return url,payload

    def delete_isp_list_device(self,device_mac,**field_data):
        '''
        删除isp库中设备
        @param device_mac: 需要删除的mac
        @param field_data:
        @return:
        '''
        url = "https://test-isp-api.viloliving.com/isp/v1/device/delete"
        payload = {
            "app_version": "1.0.29",
            "app_name": "com.viloliving.vilo",
            "request_id": "b446e388cd96469fb5c01bd31d7f5adc",
            "data": {
                "device_mac":device_mac,
                "type":1
            },
            "os_name": "5.0",
            "os_version": "5.0",
            "timestamp": int(time.time() * 1000)
        }
        return url, payload


if __name__ == '__main__':
    device = DeviceHttpProtocol(env="test",project_name="kivo_america_device")
    print(device.get_r(mac="E8DA000A569F"))


