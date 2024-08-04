# login_script.py
import requests
from bs4 import BeautifulSoup
import os

def login_and_check():
    login_url = 'https://console.diylink.net/login'
    session = requests.Session()
    
    # 获取登录页面以提取 CSRF 令牌
    response = session.get(login_url)
    if response.ok:
        print('成功获取登录页面')
        
        # 解析 HTML 页面
        soup = BeautifulSoup(response.text, 'html.parser')
        csrf_token = soup.find('input', {'name': 'csrf_token'})  # 根据实际情况调整
        csrf_token_value = csrf_token.get('value') if csrf_token else None
        
        # 登录信息
        login_data = {
            'username': os.getenv('USERNAME'),  # 从环境变量中获取用户名
            'password': os.getenv('PASSWORD'),  # 从环境变量中获取密码
            'csrf_token': csrf_token_value
        }
        
        # 发送登录请求
        login_response = session.post(login_url, data=login_data)
        
        if login_response.ok:
            print('登录成功')
        else:
            print('登录失败')
            print('状态码:', login_response.status_code)
            print('响应内容:', login_response.text[:500])
    else:
        print('获取登录页面失败')
        print('状态码:', response.status_code)
        print('响应内容:', response.text[:500])

if __name__ == '__main__':
    login_and_check()
