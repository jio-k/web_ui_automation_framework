import os,sys
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import logging,time
import requests,json

from protocol.protocol import AppHttpProtocol,DeviceHttpProtocol
from utils.data_handle import get_enr,firmware_ver,read_json,save_json,http_put
from utils.setting import DATA_PATH,AWS_PATH,LOG_PATH
from utils.assert_retry import RetryRequestAssert
from utils.iot_device_thread import IotDeviceThread
from utils.common import rmtree_dir,get_uuid

logger =logging.getLogger(__name__)
logger.setLevel(logging.INFO)#设置初始显示级别



class Server:
    '''服务类'''
    def __init__(self,app_protocol=None,device_protocol=None,qa_protocol=None,server=None):

        self.app_protocol = app_protocol
        self.device_protocol = device_protocol
        self.qa_protocol = qa_protocol
        self.server = server

    def get_enr(self,mac):
        '''通过mac获取enr'''


        #获取r
        http_data = self.device_protocol.get_r(mac=mac)
        r = get_value(http_data,'random_number')

        # 通过本地的key和获取到的r进行rsa加密，生产enr
        enr = get_enr(mac=mac,r=r)
        return enr

    def get_verify_code(self,reg_type,user_name):
        '''
        获取验证码
        :param reg_type:获取验证码类型 0-注册新用户 1-重置密码
        :return:
        '''
        http_data = self.app_protocol.send_verify_code(reg_type=reg_type,user_name=user_name)
        assert http_data['status_code'] == 200
        assert get_value(http_data,'code') == "1"

        http_data = self.app_protocol.qateam_get_verify_code(account_name=user_name)
        assert http_data['status_code'] == 200
        assert http_data['res']['code'] == '1'
        verify_code = http_data['res']['data']['verify_code']
        return verify_code


    def add_binding_device(self,mac,access_token=None,error_enr=None,save=True,
                           hardware_ver='1.0.0.0', firmware_ver='5.16.0.30',force_verify=True,
                           ensure_binding_success=True):
        '''
        用户添加绑定设备
        :param mac:
        :param access_token:
        :param error_enr:
        :param save:
        :param hardware_ver:
        :param firmware_ver:
        :param force_verify:
        :param ensure_binding_success:
        :return:
        '''
        # 读取device_binding_info文件里内容，字典格式
        device_binding_info = read_json(filename='device_binding_info', file_path=DATA_PATH)
        mac_binding_info = device_binding_info.get(mac)

        # 获取绑定token
        if access_token:
            http_data = self.app_protocol.get_binding_token(access_token=access_token)
        else:
            http_data = self.app_protocol.get_binding_token()
        binding_token = get_value(http_data, ['binding_token'])



        if error_enr:
            save = False
            enr = error_enr
        elif not mac_binding_info or (
                hardware_ver != '1.0.0.0' or firmware_ver != '5.16.0.30') or access_token or force_verify:
            # 获取enr
            enr = self.get_enr(mac)

            # 验证enr
            RetryRequestAssert(self.device_protocol.verify_enr, mac=mac, enr=enr).wait(timeout=2, frequency=0.5) \
                .assert_equal("['res']['code']", '1')


        else:
            enr = mac_binding_info.get('enr')

        if save:  # 是否写入配置文件
            device_binding_info[mac] = dict(binding_token=binding_token, enr=enr)
            save_json(file_path=DATA_PATH, filename='device_binding_info', data=device_binding_info)

        # 设备通过token进行绑定
        RetryRequestAssert(self.device_protocol.device_binding, mac=mac, enr=enr[:16], token=binding_token) \
            .wait(timeout=2, frequency=0.5).assert_equal("['res']['code']", '1')

        if ensure_binding_success:
            # 获取绑定结果
            http_data = self.app_protocol.get_binding_result(binding_token=binding_token)
            assert get_value(http_data, 'code') == '1'
            assert get_value(http_data, 'binding_code') == 0
            assert get_value(http_data, 'binding_error_code') == 0
            assert get_value(http_data, 'binding_result') == 1
            assert get_value(http_data, 'device_mac') == mac
        return binding_token, enr


    def test_add_binding_device(self,mac):
        http_data = self.app_protocol.get_binding_token()
        binding_token = get_value(http_data, ['binding_token'])

        enr = self.get_enr(mac)

        RetryRequestAssert(self.device_protocol.verify_enr, mac=mac, enr=enr).wait(timeout=2, frequency=0.5) \
            .assert_equal("['res']['code']", '1')

        RetryRequestAssert(self.device_protocol.device_binding, mac=mac, enr=enr[:16], token=binding_token) \
            .wait(timeout=2, frequency=0.5).assert_equal("['res']['code']", '1')
        return enr


    def add_binding_master_device(self,mac,nick_name="主设备",ip="192.168.58.1"):
        '''
        用户添加绑定设备后将设备设为主设备
        :param mac:
        :return:
        '''
        #设备与用户进行绑定
        binding_token,enr = self.add_binding_device(mac=mac)

        #将设备设置成主设备
        http_data = self.device_protocol.add_master_device(mac=mac,enr=enr[:16],nick_name=nick_name,ip=ip)
        assert get_value(http_data,'status_code') == 200
        assert get_value(http_data,'code') == '1'
        return enr

    def add_binding_sub_device(self,mac,sub_mac,hardware_ver='1.0.0.0',firmware_ver='5.16.0.30',
                               ensure_binding_success=False):
        '''
        用户添加绑定子设备
        :param mac: 主设备mac地址
        :param sub_mac: 子设备mac地址
        :param hardware_ver:硬件版本
        :param firmware_ver:固件版本
        :param ensure_binding_success: 保证绑定成功
        :return:
        '''

        #绑定主设备
        # self.add_binding_device(mac=mac,ensure_binding_success=True)#####################################
        self.add_binding_master_device(mac=mac)

        #获取组网子设备的Token.（子设备绑定）
        http_data = self.app_protocol.get_binding_sub_device_token(device_mac=mac)
        assert get_value(http_data,'code') == '1'
        sub_binding_token = get_value(http_data,'binding_token')

        #获取enr
        sub_enr = self.get_enr(sub_mac)


        #验证enr
        RetryRequestAssert(self.device_protocol.verify_enr,mac=sub_mac,enr=sub_enr,
                           hardware_ver=hardware_ver,firmware_ver=firmware_ver)\
            .wait(timeout=2,frequency=0.5).assert_equal("['res']['code']", '1')

        # 设备通过token进行绑定
        RetryRequestAssert(self.device_protocol.device_binding,mac=sub_mac,enr=sub_enr[:16],
                           token=sub_binding_token,hardware_ver=hardware_ver,firmware_ver=firmware_ver)\
            .wait(timeout=2,frequency=0.5).assert_equal("['res']['code']", '1')

        if ensure_binding_success:
            #获取绑定结果
            http_data = self.app_protocol.get_binding_result(binding_token=sub_binding_token)
            assert get_value(http_data,'code') == '1'
            assert get_value(http_data,'binding_code') == 0
            assert get_value(http_data,'binding_error_code') == 0
            assert get_value(http_data,'binding_result') == 1
            assert get_value(http_data,'device_mac') == sub_mac

        return sub_binding_token,sub_enr

    def add_master_external_device(self,mac,enr,ip='192.168.58.2',nick_name='主设备',property_list=None,
                                   ex_mac='2047DAE1ADDA',ex_nick_name='主外接设备',ex_ip='192.168.58.101',
                                   ex_property_list=None):
        '''
        添加主设备、主外接设备
        :param mac: 主设备mac
        :param enr: 主设备enr
        :param ip: 主设备ip
        :param nick_name: 主设备名称
        :param property_list: 主设备属性
        :param ex_mac: 主外接设备mac
        :param ex_nick_name: 主外接设备名称
        :param ex_ip: 主外接设备ip
        :param exdevice_property_list: 主外接设备属性
        :return:
        '''
        #主设备属性
        if property_list is None:
            property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },#在线离线状态,1:在线 0:离线
                {
                    "pid": "P2123",
                    "pvalue": "1"
                },#路由器的指示灯状态,1:开 0:关
                {
                    "pid": "P2129",
                    "pvalue": "0"
                },#主子设备入网方式0有线，1无线，2 混合
                {
                    "pid": "P2130",
                    "pvalue": "100"
                },#路由信号强度
                # {
                #     "pid": "P2150",
                #     "pvalue": "1"
                # }#流量统计开关, 用户层级,0不开启  1 开启
            ]
        # 添加主设备
        http_data = self.device_protocol.add_master_device(mac=mac,enr=enr[:16],
                                                           ip=ip,nick_name=nick_name,property_list=property_list)
        assert get_value(http_data,'code') == '1'

        #主外接设备属性
        if ex_property_list is None:
            ex_property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },#在线离线状态,1:在线 0:离线
                {
                    "pid": "P2145",
                    "pvalue": "142"
                },#外接设备的实时上传速率，单位bit
                {
                    "pid": "P2146",
                    "pvalue": "80"
                },#外接设备的实时下载速率，单位bit
                {
                    "pid": "P2147",
                    "pvalue": "67"
                },#外接设备的网络信号强度
                {
                    "pid": "P2148",
                    "pvalue": "4"
                },#外接设备接入网络的方式,1:有线;2:2.4G无线;4:5G无线
                {
                    "pid": "P2149",
                    "pvalue": int(time.time()*1000)
                },#外接设备接入网络的时间
                {
                    "pid": "P2153",
                    "pvalue": "0"
                }#外接设备是否禁止联网,1:开 0:关
            ]

        #主外接设备入参
        exdevice_list = [
            {
                "mac": ex_mac,
                "nick_name": ex_nick_name,
                "ip": ex_ip,
                "product_model": "KIVO_MeshRouter_Other",
                "product_type": "KIVO_MeshRouter_Other",
                "exdevice_property_list":ex_property_list
            }
        ]

        #添加主外接设备
        http_data = self.device_protocol.add_external_device(mac=mac,enr=enr[:16],exdevice_list=exdevice_list)
        assert get_value(http_data,'code') == '1'
        # 获取mesh_id
        mesh_id = self.get_mesh_id(mac=mac)
        return mesh_id


    def add_single_master_external_device(self,mac,enr,ex_property_list=None,ex_mac='2047DAE1ADDB',
                                          ex_nick_name='主外接设备2',ex_ip='192.168.68.100'):
        '''
        #追加主外接设备
        :param mac: 主设备mac
        :param enr: 主设备enr
        :param ex_property_list: 主外接设备属性
        :param ex_mac: 主外接设备mac
        :param ex_nick_name: 主外接设备名称
        :param ex_ip: 主外接设备ip
        :return:
        '''
        # 主外接设备属性
        if ex_property_list is None:
            ex_property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },  # 在线离线状态,1:在线 0:离线
                {
                    "pid": "P2145",
                    "pvalue": "142"
                },  # 外接设备的实时上传速率，单位bit
                {
                    "pid": "P2146",
                    "pvalue": "80"
                },  # 外接设备的实时下载速率，单位bit
                {
                    "pid": "P2147",
                    "pvalue": "67"
                },  # 外接设备的网络信号强度
                {
                    "pid": "P2148",
                    "pvalue": "4"
                },  # 外接设备接入网络的方式,1:有线;2:2.4G无线;4:5G无线
                {
                    "pid": "P2149",
                    "pvalue": int(time.time() * 1000)
                },  # 外接设备接入网络的时间
                {
                    "pid": "P2153",
                    "pvalue": "0"
                }  # 外接设备是否禁止联网,1:开 0:关
            ]
        # 主外接设备入参
        exdevice_list = [
            {
                "mac": ex_mac,
                "nick_name": ex_nick_name,
                "ip": ex_ip,
                "product_model": "KIVO_MeshRouter_Other",
                "product_type": "KIVO_MeshRouter_Other",
                "exdevice_property_list":ex_property_list
            }
        ]
        #添加主外接设备
        http_data = self.device_protocol.add_external_device(mac=mac,enr=enr[:16],exdevice_list=exdevice_list)
        '''
        测试专项，临时注释，返回http_data
        '''
        # assert get_value(http_data,'code') == '1'
        return http_data

    def add_single_sub_external_device(self, mac,
                                enr,
                                sub_enr,
                                sub_mac,
                                sub_property_list=None,
                                sub_ex_property_list=None,
                                sub_nick_name='子设备',
                                sub_ip='192.168.58.100',
                                sub_ex_mac='SEX888K8I8DD',
                                sub_ex_nick_name='子外接设备',
                                sub_ex_ip='192.168.58.102'):
        '''
        追加子外接设备
        :param mac: 主设备mac
        :param enr: 主设备enr
        :param sub_mac: 子设备mac
        :param force_verify:
        :param sub_property_list: 子设备属性
        :param sub_ex_property_list: 子外接设备属性
        :param sub_nick_name: 子设备名称
        :param sub_ip: 子设备ip
        :param sub_ex_mac: 子外接设备mac
        :param sub_ex_nick_name: 子外接设备名称
        :param sub_ex_ip: 子外接设备ip
        :return:
        '''

        # 子设备属性
        if sub_property_list is None:
            sub_property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },  # 在线离线状态,1:在线 0:离线
                {
                    "pid": "P2123",
                    "pvalue": "1"
                },  # 路由器的指示灯状态,1:开 0:关
                {
                    "pid": "P2129",
                    "pvalue": "1"
                },  # 主子设备入网方式0有线，1无线，2 混合
                {
                    "pid": "P2130",
                    "pvalue": "81"
                }  # 路由信号强度
            ]
        # 子外接设备属性
        if sub_ex_property_list is None:
            sub_ex_property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },  # 在线离线状态,1:在线 0:离线
                {
                    "pid": "P2145",
                    "pvalue": "142"
                },  # 外接设备的实时上传速率，单位bit
                {
                    "pid": "P2146",
                    "pvalue": "80"
                },  # 外接设备的实时下载速率，单位bit
                {
                    "pid": "P2147",
                    "pvalue": "67"
                },  # 外接设备的网络信号强度
                {
                    "pid": "P2148",
                    "pvalue": "4"
                },  # 外接设备接入网络的方式,1:有线;2:2.4G无线;4:5G无线
                {
                    "pid": "P2149",
                    "pvalue": int(time.time() * 1000)
                },  # 外接设备接入网络的时间
                {
                    "pid": "P2153",
                    "pvalue": "0"
                }  # 外接设备是否禁止联网,1:开 0:关
            ]
        # 子外接设备参数
        sub_device_list = [
            {
                "mac": sub_mac,  # 子设备mac
                "enr": sub_enr[:16],  # 子设备enr
                "nick_name": sub_nick_name,  # 子设备名称
                "ip": sub_ip,  # 子设备名称
                "sub_device_property_list": sub_property_list,  # 子设备属性
                "exdevice_list": [{  # 外接设备属性
                    "mac": sub_ex_mac,  # 子外接设备mac
                    "nick_name": sub_ex_nick_name,  # 子外接设备名称
                    "ip": sub_ex_ip,  # 子外接设备ip
                    "exdevice_property_list": sub_ex_property_list
                }]
            }
        ]
        # 增加子设备以及子外接设备
        http_data = self.device_protocol.add_sub_device(mac=mac, enr=enr[:16], sub_mac=sub_mac, sub_enr=sub_enr,
                                                        sub_device_list=sub_device_list)
        '''
        测试专项临时注释，返回http_data
        '''
        # assert get_value(http_data, 'code') == '1'
        # return sub_enr
        return http_data

    def get_mesh_id(self,mac):
        '''
        获取mesh_id
        :param mac: 主设备mac
        :return:
        '''
        http_data = self.app_protocol.get_device_list()
        for device_info in get_value(http_data,'device_list'):
            if mac == device_info['mac']:
                mesh_id = get_value(device_info,'mesh_id')
                break
        else:
            assert False,'未找到设备mesh_id'
        return mesh_id

    def add_sub_external_device(self,mac,enr,sub_mac,force_verify=True,sub_property_list=None,sub_ex_property_list=None,
                                sub_nick_name='子设备',sub_ip='192.168.58.100',sub_ex_mac='SEX888K8I8DD',
                                sub_ex_nick_name='子外接设备',sub_ex_ip='192.168.58.102'):
        '''
        添加子设备以及子外接设备
        :param mac: 主设备mac
        :param enr: 主设备enr
        :param sub_mac: 子设备mac
        :param force_verify:
        :param sub_property_list: 子设备属性
        :param sub_ex_property_list: 子外接设备属性
        :param sub_nick_name: 子设备名称
        :param sub_ip: 子设备ip
        :param sub_ex_mac: 子外接设备mac
        :param sub_ex_nick_name: 子外接设备名称
        :param sub_ex_ip: 子外接设备ip
        :return:
        '''
        #用户添加绑定子设备
        sub_binding_token,sub_enr = self.add_binding_device(mac=sub_mac,ensure_binding_success=True,force_verify=force_verify)

        #子设备属性
        if sub_property_list is None:
            sub_property_list = [
                    {
                    "pid": "P5",
                    "pvalue": "1"
                    },#在线离线状态,1:在线 0:离线
                    {
                    "pid": "P2123",
                    "pvalue": "1"
                    },#路由器的指示灯状态,1:开 0:关
                    {
                    "pid": "P2129",
                    "pvalue": "1"
                    },#主子设备入网方式0有线，1无线，2 混合
                    {
                    "pid": "P2130",
                    "pvalue": "81"
                    }#路由信号强度
            ]
        #子外接设备属性
        if sub_ex_property_list is None:
            sub_ex_property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },#在线离线状态,1:在线 0:离线
                {
                    "pid": "P2145",
                    "pvalue": "142"
                },#外接设备的实时上传速率，单位bit
                {
                    "pid": "P2146",
                    "pvalue": "80"
                },#外接设备的实时下载速率，单位bit
                {
                    "pid": "P2147",
                    "pvalue": "67"
                },#外接设备的网络信号强度
                {
                    "pid": "P2148",
                    "pvalue": "4"
                },#外接设备接入网络的方式,1:有线;2:2.4G无线;4:5G无线
                {
                    "pid": "P2149",
                    "pvalue": int(time.time()*1000)
                },#外接设备接入网络的时间
                {
                    "pid": "P2153",
                    "pvalue": "0"
                }#外接设备是否禁止联网,1:开 0:关
            ]
        #子外接设备参数
        sub_device_list = [
                {
                    "mac": sub_mac,#子设备mac
                    "enr": sub_enr[:16],#子设备enr
                    "nick_name": sub_nick_name,#子设备名称
                    "ip": sub_ip,#子设备名称
                    "sub_device_property_list": sub_property_list,#子设备属性
                    "exdevice_list":[{      #外接设备属性
                        "mac":sub_ex_mac,#子外接设备mac
                        "nick_name":sub_ex_nick_name,#子外接设备名称
                        "ip":sub_ex_ip,#子外接设备ip
                        "exdevice_property_list":sub_ex_property_list
                    }]
                }
            ]
        #增加子设备以及子外接设备
        http_data = self.device_protocol.add_sub_device(mac=mac,enr=enr[:16],sub_mac=sub_mac,sub_enr=sub_enr,
                                                        sub_device_list=sub_device_list)
        assert get_value(http_data,'code') == '1'
        return sub_enr

    def add_sub_device(self,mac,enr,sub_mac,force_verify=True,sub_property_list=None,
                       sub_nick_name="子设备",
                       sub_ip="192.168.58.10"):
        '''
        添加子设备
        :param mac: 主设备mac
        :param enr: 主设备enr
        :param sub_mac: 子设备mac
        :param force_verify:
        :param sub_property_list:
        :param sub_nick_name:
        :param sub_ip:
        :return:
        '''

        sub_binding_token, sub_enr = self.add_binding_device(mac=sub_mac, ensure_binding_success=True,
                                                             force_verify=force_verify)
        # 子设备属性
        if sub_property_list is None:
            sub_property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },  # 在线离线状态,1:在线 0:离线
                {
                    "pid": "P2123",
                    "pvalue": "1"
                },  # 路由器的指示灯状态,1:开 0:关
                {
                    "pid": "P2129",
                    "pvalue": "1"
                },  # 主子设备入网方式0有线，1无线，2 混合
                {
                    "pid": "P2130",
                    "pvalue": "81"
                }  # 路由信号强度
            ]
            # 子设备参数
            sub_device_list = [
                {
                    "mac": sub_mac,  # 子设备mac
                    "enr": sub_enr[:16],  # 子设备enr
                    "nick_name": sub_nick_name,  # 子设备名称
                    "ip": sub_ip,  # 子设备名称
                    "sub_device_property_list": sub_property_list,  # 子设备属性
                }
            ]
            # 增加子设备以及子外接设备
            http_data = self.device_protocol.add_sub_device(mac=mac, enr=enr[:16], sub_mac=sub_mac, sub_enr=sub_enr,
                                                            sub_device_list=sub_device_list)
            assert get_value(http_data, 'code') == '1'
            return sub_enr

    def add_master_sub_external_device(self,mac,sub_mac,ex_mac='2047DAE1ADDA',sub_ex_mac='SEX888K8I8ED',property_list=None,
                                       ex_property_list=None,sub_property_list=None,sub_ex_property_list=None):
        '''
        添加主、子设备，以及主子外接设备
        :param mac: 主设备mac
        :param sub_mac: 子设备mac
        :param ex_mac: 主外接设备mac
        :param sub_ex_mac: 子外接设备mac
        :param property_list: 主设备属性
        :param ex_property_list: 主外接设备属性
        :param sub_property_list: 子设备属性
        :param sub_ex_property_list: 子外接设备属性
        :return:
        '''
        #用户添加绑定设备
        binding_token, enr = self.add_binding_device(mac=mac,ensure_binding_success=True,force_verify=True)

        # 主设备属性
        if property_list is None:
            property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },  # 在线离线状态,1:在线 0:离线
                {
                    "pid": "P2123",
                    "pvalue": "1"
                },  # 路由器的指示灯状态,1:开 0:关
                {
                    "pid": "P2129",
                    "pvalue": "0"
                },  # 主子设备入网方式0有线，1无线，2 混合
                {
                    "pid": "P2130",
                    "pvalue": "100"
                }  # 路由信号强度
            ]
        # 主外接设备属性
        if ex_property_list is None:
            ex_property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },  # 在线离线状态,1:在线 0:离线
                {
                    "pid": "P2145",
                    "pvalue": "142"
                },  # 外接设备的实时上传速率，单位bit
                {
                    "pid": "P2146",
                    "pvalue": "80"
                },  # 外接设备的实时下载速率，单位bit
                {
                    "pid": "P2147",
                    "pvalue": "67"
                },  # 外接设备的网络信号强度
                {
                    "pid": "P2148",
                    "pvalue": "4"
                },  # 外接设备接入网络的方式,1:有线;2:2.4G无线;4:5G无线
                {
                    "pid": "P2149",
                    "pvalue": int(time.time() * 1000)
                },  # 外接设备接入网络的时间
                {
                    "pid": "P2153",
                    "pvalue": "0"
                }  # 外接设备是否禁止联网,1:开 0:关
            ]

        # 子设备属性
        if sub_property_list is None:
            sub_property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },  # 在线离线状态,1:在线 0:离线
                {
                    "pid": "P2123",
                    "pvalue": "1"
                },  # 路由器的指示灯状态,1:开 0:关
                {
                    "pid": "P2129",
                    "pvalue": "1"
                },  # 主子设备入网方式0有线，1无线，2 混合
                {
                    "pid": "P2130",
                    "pvalue": "81"
                }  # 路由信号强度
            ]
        # 子外接设备属性
        if sub_ex_property_list is None:
            sub_ex_property_list = [
                {
                    "pid": "P5",
                    "pvalue": "1"
                },  # 在线离线状态,1:在线 0:离线
                {
                    "pid": "P2145",
                    "pvalue": "142"
                },  # 外接设备的实时上传速率，单位bit
                {
                    "pid": "P2146",
                    "pvalue": "80"
                },  # 外接设备的实时下载速率，单位bit
                {
                    "pid": "P2147",
                    "pvalue": "67"
                },  # 外接设备的网络信号强度
                {
                    "pid": "P2148",
                    "pvalue": "4"
                },  # 外接设备接入网络的方式,1:有线;2:2.4G无线;4:5G无线
                {
                    "pid": "P2149",
                    "pvalue": int(time.time() * 1000)
                },  # 外接设备接入网络的时间
                {
                    "pid": "P2153",
                    "pvalue": "0"
                }  # 外接设备是否禁止联网,1:开 0:关
            ]


        #添加主外接设备
        mesh_id = self.add_master_external_device(mac,enr,ip='192.168.58.3',nick_name='测试9楼(主)',
                                        property_list=property_list,ex_mac=ex_mac,ex_nick_name='主外1',
                                        ex_ip='192.168.68.110',ex_property_list=ex_property_list)

        #增加子外接设备
        self.add_sub_external_device(mac,enr,sub_mac,sub_property_list=sub_property_list,
                                     sub_ex_property_list=sub_ex_property_list,sub_nick_name='测试9楼(子)',
                                     sub_ip='192.168.58.103',sub_ex_mac=sub_ex_mac,sub_ex_nick_name='子外1',
                                     sub_ex_ip='192.168.58.105')
        return enr,mesh_id

    def add_device_and_iot_connect(self,mac):
        '''用户绑定设备，设备起iot连接设备'''
        binding_token,enr = self.add_binding_device(mac,ensure_binding_success=True,force_verify=True)
        idt = self.iot_connect(mac,enr=enr)
        return enr,idt

    def iot_connect(self,mac,enr):
        '''
        启动iot连接
        :param mac: 产品唯一编号(设备Mac)
        :param enr: R’前16位。验证R'时需要传入全R' 获取R时传入""
        :return:
        '''
        #获取iot证书
        iot_info = self.device_protocol.get_iot_certificate(mac=mac,enr=enr[:16])
        client_id = get_value(iot_info,'client_id')
        keep_alive = get_value(iot_info,'keep_alive')

        #iot证书保存路径
        root_ca_path = os.path.join(AWS_PATH,'root_cert')
        client_private_key_path = os.path.join(AWS_PATH,"%s_client_private_key"%mac)
        client_ca_path = os.path.join(AWS_PATH,"%s_client_cert"%mac)


        #证书下载地址
        root_cert_url = get_value(iot_info,'root_cert_url')
        client_private_key_url = get_value(iot_info,'client_private_key_url')
        client_cert_url = get_value(iot_info,'client_cert_url')

        #下载证书
        self.download_ca(ca_url=root_cert_url,ca_path=root_ca_path,mac=mac)
        self.download_ca(ca_url=client_private_key_url,ca_path=client_private_key_path,mac=mac)
        self.download_ca(ca_url=client_cert_url,ca_path=client_ca_path,mac=mac)

        server = self.server
        if server == "test":
            server= 'kivo_america_test'
        else:
            server = 'kivo_america_offi'
        idt = IotDeviceThread(server,enr[:16],client_id,keep_alive,root_ca_path,client_ca_path,
                              client_private_key_path)
        idt.setDaemon(True)
        idt.start()

        #确保iot启动完成
        idt.queue_get(expect_action='iot启动完成')
        # idt.set_disconnect()#断开iot连接
        return idt

    @staticmethod
    def save_ca(ca_path,ca_data):
        '''本地保存证书'''
        with open(ca_path,'w') as fw:
            fw.write(ca_data)

    def download_ca(self,ca_url,ca_path,mac):
        '''下载证书'''
        # if not os.path.exists(ca_path):
        for _ in range(3):
            try:
                r = requests.get(ca_url,timeout=2.5)
            except Exception as e:
                logger.info("【下载证书失败，请重试】【%s】\n【异常信息】-【%s】"%(mac,e))
            else:
                self.save_ca(ca_path=ca_path,ca_data=r.text)
                logger.info("【证书下载成功】【%s】"%mac)
                break
        else:
            logger.info("【重试完成,下载证书最终失败】【%s】"%mac)

    def start_iot_add_master_external_device_upload_log_address(self,mac,ex_mac,flow_stat_up,flow_stat_down,
                                                                file_relative_path,data_time_ts,idt=None):
        if not idt:
            binding_token,enr = self.add_binding_device(mac=mac,ensure_binding_success=True,force_verify=True)
            self.iot_connect(mac=mac,enr=enr)
        else:
            enr = idt.enr

        data = {"pid": "P2150","pvalue": "1"}
        idt.master_initiative_report(data=data)
        self.add_master_external_device(mac=mac,enr=enr[:16],ex_mac=ex_mac)

        #上传路由器历史数据
        data = [{
            "ExDeviceMac": ex_mac,
            "FlowStatUp": flow_stat_up,
            "FlowStatDown": flow_stat_down
        }]
        self.upload_log_address(mac,enr,file_relative_path,data_time_ts,data)

    def upload_log_address(self,mac,enr,file_relative_path,data_time_ts,data):
        """
                上传路由器历史数据
                @param mac: 主设备mac
                @param enr: R'
                @param file_relative_path: 格式为: {deviceMac}/{year}-{month}-{day}-{hh}-{mm}-{ss}.txt
                @param data_time_ts: log文件内的时间戳
                @param data: 外接设备、上下行速率
                        [
                                {
                                    "ExDeviceMac": ex_mac,
                                    "FlowStatUp": '5105144',
                                    "FlowStatDown": '8020814'
                                },
                                {
                                    "ExDeviceMac": 'MMM666K8I8DL',
                                    "FlowStatUp": '666',
                                    "FlowStatDown": '888'
                                },
                            ]
        """
        # 获取上传历史数据的地址的接口
        http_data = self.device_protocol.get_log_address_list(mac=mac,enr=enr[:16],file_relative_path=[file_relative_path])
        put_url = http_data["res"]["data"]["log_address_list"][0]

        #清空文件夹
        if os.path.exists(LOG_PATH):
            rmtree_dir(dir_path=LOG_PATH)
        else:
            os.mkdir(LOG_PATH)

        #写入历史数据txt    ["E4AAEC4402EE/2021-04-26-09-39-15.txt"]
        log_path = os.path.join(LOG_PATH,file_relative_path.split("/")[-1])

        log_address_data = {
            "UserId": "HUALAI-%s"%get_uuid(),
            "DeviceMac": mac,
            "DateTimeTs": data_time_ts,
            "Data": data
        }
        with open(log_path,'w') as fw:
            fw.write(json.dumps(log_address_data))

        #上传历史数据
        put_log_address =http_put(log_path,put_url)
        assert put_log_address is True












if __name__ == '__main__':
    pass








