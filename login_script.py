import requests
from bs4 import BeautifulSoup

# 登录 URL
login_url = 'https://console.diylink.net/login'

# 登录信息
login_data = {
    'username': 'raglessschral@gmail.com',  # 替换为你的用户名
    'password': 'Hsr7528@gg'   # 替换为你的密码
}

# 创建一个会话对象，用于保持会话状态
session = requests.Session()

# 获取登录页面，以便提取 CSRF 令牌等信息（如果需要）
response = session.get(login_url)

# 检查是否成功获取页面
if response.ok:
    print('成功获取登录页面')
    
    # 解析 HTML 页面
    soup = BeautifulSoup(response.text, 'html.parser')

    # 查找可能需要的 CSRF 令牌（这里需要根据实际情况调整）
    # 假设页面中有一个名为 'csrf_token' 的隐藏输入字段
    csrf_token = soup.find('input', {'name': 'csrf_token'})
    if csrf_token:
        csrf_token_value = csrf_token.get('value')
        login_data['csrf_token'] = csrf_token_value

    # 发送登录请求
    login_response = session.post(login_url, data=login_data)

    # 检查登录是否成功
    if login_response.ok:
        print('登录成功')
        # 你可以在这里进一步处理响应，例如检查 cookies 或者访问需要登录的页面
        print('响应内容:', login_response.text[:500])  # 输出前500个字符
    else:
        print('登录失败')
        print('状态码:', login_response.status_code)
        print('响应内容:', login_response.text[:500])  # 输出前500个字符
else:
    print('获取登录页面失败')
    print('状态码:', response.status_code)
    print('响应内容:', response.text[:500])  # 输出前500个字符
