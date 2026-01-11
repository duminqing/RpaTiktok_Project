"""
VMOS 服务调用模块
包含 vmos 和 paas 服务的 API 调用工具函数
"""
import binascii
import datetime
import hmac
import hashlib
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)

def get_signature(data, x_date, host, content_type, signed_headers, sk):
    """
    计算 HMAC-SHA256 签名
    
    Args:
        data: 请求的 JSON 数据
        x_date: 请求时间戳，格式：YYYYMMDDTHHMMSSZ
        host: 主机名
        content_type: 内容类型
        signed_headers: 签名的头部字段
        sk: Secret Access Key
    
    Returns:
        str: 十六进制编码的签名字符串
    """
    # 将JSON数据转换为字符串（去除空格）
    json_string = json.dumps(data, separators=(',', ':'), ensure_ascii=False)
    
    # 计算SHA-256哈希值
    hash_object = hashlib.sha256(json_string.encode())
    x_content_sha256 = hash_object.hexdigest()

    # 构建canonicalStringBuilder
    canonical_string_builder = (
        f"host:{host}\n"
        f"x-date:{x_date}\n"
        f"content-type:{content_type}\n"
        f"signedHeaders:{signed_headers}\n"
        f"x-content-sha256:{x_content_sha256}"
    )

    # 短请求时间，例如："20240101"
    short_x_date = x_date[:8]
    service = "armcloud-paas"  # 服务名

    # 构建credentialScope
    credential_scope = "{}/{}/request".format(short_x_date, service)

    # 算法
    algorithm = "HMAC-SHA256"

    # 计算canonicalStringBuilder的SHA-256哈希值
    hash_sha256 = hashlib.sha256(canonical_string_builder.encode()).hexdigest()
    
    # 构建StringToSign
    string_to_sign = (
        algorithm + '\n' +
        x_date + '\n' +
        credential_scope + '\n' +
        hash_sha256
    )

    # 第一次hmacSHA256
    first_hmac = hmac.new(sk.encode(), digestmod=hashlib.sha256)
    first_hmac.update(short_x_date.encode())
    first_hmac_result = first_hmac.digest()

    # 第二次hmacSHA256
    second_hmac = hmac.new(first_hmac_result, digestmod=hashlib.sha256)
    second_hmac.update(service.encode())
    second_hmac_result = second_hmac.digest()

    # 第三次hmacSHA256
    signing_key = hmac.new(second_hmac_result, b'request', digestmod=hashlib.sha256).digest()

    # 使用signing_key和string_to_sign计算HMAC-SHA256
    signature_bytes = hmac.new(signing_key, string_to_sign.encode(), hashlib.sha256).digest()

    # 将HMAC-SHA256的结果转换为十六进制编码的字符串
    signature = binascii.hexlify(signature_bytes).decode()

    return signature

def paas_url_util(url, data, ak=None, sk=None):
    """
    PAAS 服务 API 调用工具
    
    Args:
        url: API 路径
        data: 请求数据（字典）
        ak: Access Key ID（可选，默认从 settings 读取）
        sk: Secret Access Key（可选，默认从 settings 读取）
    
    Returns:
        dict: API 响应结果
    """
    if ak is None:
        ak = settings.ACCESS_KEY_ID
    if sk is None:
        sk = settings.SECRET_ACCESS_KEY
    
    x_date = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    content_type = "application/json"
    signed_headers = "content-type;host;x-content-sha256;x-date"
    short_date = x_date[:8]
    host = "openapi-hk.armcloud.net"
    
    try:
        # 获取signature
        signature = get_signature(data, x_date, host, content_type, signed_headers, sk)
        full_url = f"http://openapi-hk.armcloud.net{url}"
        payload = json.dumps(data)
        
        headers = {
            'Content-Type': content_type,
            'x-date': x_date,
            'x-host': host,
            'authorization': f"HMAC-SHA256 Credential={ak}/{short_date}/armcloud-paas/request, "
                            f"SignedHeaders=content-type;host;x-content-sha256;x-date, "
                            f"Signature={signature}"
        }
        
        response = requests.request("POST", full_url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()  # 如果状态码不是 200，会抛出异常
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"PAAS API 调用失败: {url}, 错误: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"PAAS API 响应解析失败: {url}, 错误: {str(e)}")
        raise

def vmos_url_util(url, data, access_key=None, secret_key=None):
    """
    VMOS 服务 API 调用工具
    
    Args:
        url: API 路径
        data: 请求数据（字典）
        access_key: Access Key ID（可选，默认从 settings 读取）
        secret_key: Secret Access Key（可选，默认从 settings 读取）
    
    Returns:
        dict: API 响应结果
    """
    if access_key is None:
        access_key = settings.ACCESS_KEY_ID
    if secret_key is None:
        secret_key = settings.SECRET_ACCESS_KEY
    
    x_date = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    content_type = "application/json;charset=UTF-8"
    signed_headers = "content-type;host;x-content-sha256;x-date"
    short_date = x_date[:8]
    host = "api.vmoscloud.com"
    
    try:
        # 获取signature
        signature = get_signature(data, x_date, host, content_type, signed_headers, secret_key)
        full_url = f"https://api.vmoscloud.com{url}"
        
        payload = json.dumps(data, ensure_ascii=False)
        headers = {
            'content-type': content_type,
            'x-date': x_date,
            'x-host': host,
            'authorization': f"HMAC-SHA256 Credential={access_key}, "
                            f"SignedHeaders=content-type;host;x-content-sha256;x-date, "
                            f"Signature={signature}"
        }
        
        response = requests.request("POST", full_url, headers=headers, data=payload, timeout=30)
        response.raise_for_status()  # 如果状态码不是 200，会抛出异常
        return response.json()
    
    except requests.exceptions.RequestException as e:
        logger.error(f"VMOS API 调用失败: {url}, 错误: {str(e)}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"VMOS API 响应解析失败: {url}, 错误: {str(e)}")
        raise

# VMOS API 端点常量
class VMOSEndpoints:
    """VMOS API 端点常量"""
    PAD_TASK_DETAIL = '/vcpcloud/api/padApi/padTaskDetail'
    PAD_INFOS = '/vcpcloud/api/padApi/infos'
    PAD_ADB = '/vcpcloud/api/padApi/adb'

# 便捷函数：获取 pad 任务详情
def get_pad_task_detail(task_ids, access_key=None, secret_key=None):
    data = {"taskIds": task_ids}
    return vmos_url_util(VMOSEndpoints.PAD_TASK_DETAIL, data, access_key, secret_key)

# 便捷函数：获取 pad 连接详情
def get_pad_adb(padCode, enable=True, access_key=None, secret_key=None):
    adbResult = vmos_url_util(VMOSEndpoints.PAD_ADB, {'padCode': padCode, 'enable': enable}, access_key, secret_key)
    adbInfo = parseAdb(adbResult)
    adbInfo['pad_code']=padCode
    return adbInfo

def parseAdb(adbResult):
    adbInfo= doParseAdb(adbResult['data']['command'])
    adbInfo['password']=adbResult['data']['key']
    logger.info(adbInfo)
    return adbInfo

def doParseAdb(adbCmd):
    adbInfo={}
    adbInfo['username']=adbCmd.split(' ')[2].split('@')[0]
    adbInfo['hostname']=adbCmd.split(' ')[2].split('@')[1]
    adbInfo['port']=adbCmd.split(' ')[4]
    adbInfo['local_port']=adbCmd.split(' ')[6].split(':')[0]
    adbInfo['remote_host']=adbCmd.split(' ')[6].split(':')[1]
    adbInfo['remote_port']=adbCmd.split(' ')[6].split(':')[2]
    return adbInfo