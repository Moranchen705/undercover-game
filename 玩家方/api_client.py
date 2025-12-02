"""
API通信模块
负责与主持方服务器的所有HTTP通信
"""
import requests
import time
from typing import Dict, Optional, List


class APIClient:
    """游戏方API客户端"""
    
    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        """
        初始化API客户端
        :param base_url: 主持方服务器地址，例如 "http://192.168.1.100:5000"
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.timeout = 5  # 请求超时时间5秒
        self.last_error = None  # 保存最后一次错误信息
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[Dict]:
        """
        发送HTTP请求的通用方法
        :param method: HTTP方法（GET/POST）
        :param endpoint: API端点路径
        :param kwargs: 其他请求参数
        :return: 响应数据字典，失败返回None，错误信息保存在self.last_error中
        """
        url = f"{self.base_url}{endpoint}"
        self.last_error = None  # 保存最后一次错误信息
        try:
            if method.upper() == 'GET':
                response = self.session.get(url, **kwargs)
            elif method.upper() == 'POST':
                response = self.session.post(url, **kwargs)
            else:
                return None
            
            # 先尝试解析JSON响应（即使状态码不是200）
            try:
                data = response.json()
                print(f"[API客户端] 响应状态码: {response.status_code}, 响应数据: {data}")
            except:
                # 如果不是JSON响应，使用raise_for_status抛出异常
                print(f"[API客户端] 无法解析JSON响应，状态码: {response.status_code}")
                response.raise_for_status()
                return None
            
            # 检查响应码
            if data.get('code') == 200:
                return data.get('data', {})
            else:
                # 业务逻辑错误（如400），保存错误信息
                error_msg = data.get('message', '未知错误')
                self.last_error = error_msg
                print(f"[API客户端] API错误: {error_msg}")
                return None
                
        except requests.exceptions.HTTPError as e:
            # HTTP错误（如404, 500等）
            try:
                error_data = e.response.json()
                error_msg = error_data.get('message', str(e))
            except:
                error_msg = str(e)
            self.last_error = error_msg
            print(f"HTTP错误: {error_msg}")
            return None
        except requests.exceptions.ConnectionError:
            self.last_error = f"连接失败：无法连接到服务器 {self.base_url}"
            print(self.last_error)
            return None
        except requests.exceptions.Timeout:
            self.last_error = "请求超时"
            print(self.last_error)
            return None
        except requests.exceptions.RequestException as e:
            self.last_error = f"请求异常: {e}"
            print(self.last_error)
            return None
        except Exception as e:
            self.last_error = f"未知错误: {e}"
            print(self.last_error)
            return None
    
    def register(self, group_name: str) -> Optional[Dict]:
        """
        注册组名
        :param group_name: 组名
        :return: 注册结果，包含group_name和total_groups
        """
        return self._make_request('POST', '/api/register', json={'group_name': group_name})
    
    def get_word(self, group_name: str) -> Optional[str]:
        """
        获取自己的词语
        :param group_name: 组名
        :return: 词语字符串，失败返回None
        """
        result = self._make_request('GET', '/api/word', params={'group_name': group_name})
        return result.get('word') if result else None
    
    def get_status(self) -> Optional[Dict]:
        """
        获取游戏阶段状态
        :return: 状态信息字典，包含status, round, active_groups等
        """
        return self._make_request('GET', '/api/status')
    
    def submit_description(self, group_name: str, description: str) -> Optional[Dict]:
        """
        提交描述
        :param group_name: 组名
        :param description: 描述内容
        :return: 提交结果，包含round和total_descriptions
        """
        return self._make_request('POST', '/api/describe', json={
            'group_name': group_name,
            'description': description
        })
    
    def submit_vote(self, voter_group: str, target_group: str) -> Optional[Dict]:
        """
        提交投票
        :param voter_group: 投票者组名
        :param target_group: 被投票者组名
        :return: 提交结果，失败时返回None
        """
        print(f"[API客户端] 准备提交投票: {voter_group} -> {target_group}")
        result = self._make_request('POST', '/api/vote', json={
            'voter_group': voter_group,
            'target_group': target_group
        })
        print(f"[API客户端] 投票结果: {result}, 错误: {self.last_error}")
        return result
    
    def get_result(self) -> Optional[Dict]:
        """
        获取最近一次投票结果
        :return: 投票结果字典，包含round, vote_count, eliminated等
        """
        return self._make_request('GET', '/api/result')
    
    def report_issue(self, group_name: str, report_type: str, detail: str) -> Optional[Dict]:
        """
        上报异常
        :param group_name: 组名
        :param report_type: 异常类型
        :param detail: 异常详情
        :return: 上报结果，包含ticket和recorded_at
        """
        return self._make_request('POST', '/api/report', json={
            'group_name': group_name,
            'type': report_type,
            'detail': detail
        })
    
    def get_groups(self) -> Optional[List[Dict]]:
        """
        获取所有注册的组
        :return: 组列表
        """
        result = self._make_request('GET', '/api/groups')
        return result.get('groups', []) if result else None
    
    def get_descriptions(self) -> Optional[Dict]:
        """
        获取当前回合的所有描述
        :return: 描述信息字典，包含round和descriptions列表
        """
        return self._make_request('GET', '/api/descriptions')


# 测试代码
if __name__ == '__main__':
    print("=" * 60)
    print("API客户端测试")
    print("=" * 60)
    print("\n提示：此文件主要用于测试API连接")
    print("实际使用时，请运行 client.py 启动GUI界面")
    print("\n注意：测试前请确保后端服务器已启动！")
    print("启动方法：运行 平台方/backend.py")
    print("=" * 60)
    
    # 测试API连接
    server_url = input("\n请输入服务器地址（直接回车使用默认 http://127.0.0.1:5000）: ").strip()
    if not server_url:
        server_url = "http://127.0.0.1:5000"
    
    client = APIClient(server_url)
    
    # 测试连接
    print(f"\n正在连接服务器: {server_url}")
    status = client.get_status()
    if status:
        print("✓ 服务器连接成功！")
        print(f"当前状态: {status}")
    else:
        print("✗ 服务器连接失败")
        print("\n可能的原因：")
        print("1. 后端服务器未启动（请运行 平台方/backend.py）")
        print("2. 服务器地址不正确")
        print("3. 防火墙阻止了连接")
        exit(1)
    
    # 测试注册
    print("\n" + "=" * 60)
    group_name = input("请输入测试组名（直接回车跳过注册测试）: ").strip()
    if group_name:
        print(f"正在注册: {group_name}")
        result = client.register(group_name)
        if result:
            print(f"✓ 注册成功！总组数: {result.get('total_groups', 0)}")
        else:
            print("✗ 注册失败（可能组名已存在）")
    
    print("\n测试完成！")

