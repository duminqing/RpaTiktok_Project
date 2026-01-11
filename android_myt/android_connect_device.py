import logging
import socket
import subprocess
import threading

import uiautomator2 as u2
from paramiko import SSHClient, AutoAddPolicy

from . import vmos_api

logger = logging.getLogger(__name__)
def connect_device(device_id: str,pad_code: str,local_ip: str,local_port: int):
    """ 连接设备 """
    prepareEnviroment(device_id, pad_code, local_ip, local_port)
    return u2.connect( f"{local_ip}:{local_port}")


def prepareEnviroment(device_id: str, pad_code: str, local_ip: str, local_port: int):
    """ 准备环境 """
    if device_id.startswith("VMOS"):
        #判断如果device_id以"VMOS"开头
        pad_info = vmos_api.get_pad_adb(pad_code)
        pad_info["device_id"] = device_id
        pad_info["local_ip"] = local_ip
        pad_info["local_port"] = local_port
        open_ssh(pad_info)
        connect_adb(pad_info)
    elif device_id.startswith("MYT"):
        #否则使用adb connect命令连接设备
        pad_info = {}
        pad_info["device_id"] = device_id
        pad_info["local_ip"] = local_ip
        pad_info["local_port"] = local_port
        connect_adb(pad_info)


def open_ssh(pad_info: dict):
    """创建SSH连接并保持60分钟不断开"""
    username = pad_info['username']
    hostname = pad_info['hostname']
    port = int(pad_info['port'])
    local_port = int(pad_info['local_port'])
    remote_host = pad_info['remote_host']
    remote_port = int(pad_info['remote_port'])
    password = pad_info['password']
    device_id = pad_info.get('device_id')

    
    logger.info(f" {device_id} 正在为设备创建SSH连接: {username}@{hostname}:{port}")
    logger.info(f" {device_id} 端口转发配置: localhost:{local_port} -> {remote_host}:{remote_port}")
    
    try:
        # 建立 SSH 连接
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        
        ssh.connect(
            hostname=hostname,
            port=port,
            username=username,
            password=password,
            timeout=3600,
            allow_agent=False,
            look_for_keys=False
        )
        
        # 建立端口转发
        transport = ssh.get_transport()
        # 设置 keepalive 保持连接活跃
        transport.set_keepalive(30)  # 每30秒发送一次 keepalive
        # 在后台线程中监听本地端口并转发
        def forward_port():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('127.0.0.1', local_port))
            sock.listen(5)
            logger.info(f'开始监听本地端口: {local_port}')
            while True:
                try:
                    # 检查 SSH 连接是否仍然活跃
                    if not transport.is_active():
                        logger.error('SSH 连接已断开，停止端口转发')
                        break
                    client, addr = sock.accept()
                    channel = transport.open_channel(
                        'direct-tcpip',
                        (remote_host, remote_port),
                        (addr[0], addr[1])
                    )
                    if channel is None:
                        logger.error(f'无法建立到 {remote_host}:{remote_port} 的通道')
                        client.close()
                        continue
                    def forward_data(src, dst):
                        try:
                            while True:
                                data = src.recv(4096)
                                if not data:
                                    break
                                dst.send(data)
                        except:
                            pass
                        finally:
                            try:
                                src.close()
                                dst.close()
                            except:
                                pass
                    threading.Thread(
                        target=forward_data,
                        args=(client, channel),
                        daemon=True
                    ).start()
                    threading.Thread(
                        target=forward_data,
                        args=(channel, client),
                        daemon=True
                    ).start()
                except Exception as e:
                    logger.error(f'端口转发错误: {str(e)}')
                    if not transport.is_active():
                        break
        tunnel_thread = threading.Thread(target=forward_port, daemon=True)
        tunnel_thread.start()
        logger.info(f'{device_id}SSH 隧道建立成功，本地端口: {local_port} -> {remote_host}:{remote_port}')
        return True
    except Exception as e:
        logger.error(f'{device_id}建立 SSH 隧道失败: {str(e)}', exc_info=True)
        return False

def connect_adb(pad_info: dict):
    """ 连接ADB """
    try:
        cmd = f"adb connect {pad_info['local_ip']}:{pad_info['local_port']}"
        print(f"执行命令: {cmd}")
        # 执行adb命令
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        # 检查命令执行结果
        if result.returncode == 0:
            logger.info(f"ADB连接成功: {result.stdout.strip()}")
            return True
        else:
            logger.error(f"ADB连接失败: {result.stderr.strip()}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error(f"ADB命令执行超时")
        return False
    except Exception as e:
        logger.error(f"执行ADB命令时发生错误: {str(e)}", exc_info=True)
        return False