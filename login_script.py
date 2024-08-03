import json
import asyncio
from pyppeteer import launch
from datetime import datetime, timedelta
import aiofiles
import random
import requests
import os

# 从环境变量中获取 Telegram Bot Token 和 Chat ID
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

def format_to_iso(date):
    return date.strftime('%Y-%m-%d %H:%M:%S')

async def delay_time(ms):
    await asyncio.sleep(ms / 1000)

# 全局浏览器实例
browser = None

# telegram消息
message = 'diylink自动化脚本运行\n'

async def solve_captcha(page):
    # 提示用户手动解决 CAPTCHA
    print("检测到 CAPTCHA 页面，请手动完成验证后按回车继续...")
    input("按回车键继续...")
    # 可以在此处加入对 CAPTCHA 验证后的页面状态的检测逻辑
    # 例如，检测到登录成功后继续执行

async def login(username, password):
    global browser

    page = None  # 确保 page 在任何情况下都被定义
    try:
        if not browser:
            browser = await launch(headless=False, args=['--no-sandbox', '--disable-setuid-sandbox'])

        page = await browser.newPage()
        url = 'https://console.diylink.net/login'
        await page.goto(url, {'timeout': 120000})  # 增加超时时间

        # 等待页面加载
        await page.waitForSelector('#email', {'timeout': 120000})  # 等待元素出现

        # 定位输入框
        username_input = await page.querySelector('#email')  # 使用 ID 选择器
        password_input = await page.querySelector('#password')  # 使用 ID 选择器

        if username_input and password_input:
            await page.type('#email', username)  # 填充用户名
            await page.type('#password', password)  # 填充密码
        else:
            raise Exception('无法找到用户名或密码输入框')

        # 定位并点击登录按钮
        login_button = await page.querySelector('.ant-btn-primary')  # 使用类选择器
        if login_button:
            await login_button.click()  # 点击登录按钮
        else:
            raise Exception('无法找到登录按钮')

        # 检测是否出现 CAPTCHA 页面
        await page.waitForSelector('div#cf-content', {'timeout': 15000})  # 等待 CAPTCHA 页面出现
        if await page.querySelector('div#cf-content'):
            await solve_captcha(page)
            # 重新加载页面以继续尝试登录
            await page.reload({'timeout': 120000})

        await page.waitForNavigation({'timeout': 120000})  # 增加超时时间

        is_logged_in = await page.evaluate('''() => {
            const logoutButton = document.querySelector('a[href="/logout"]');
            return logoutButton !== null;
        }''')

        return is_logged_in

    except Exception as e:
        print(f'登录时出现错误: {e}')
        return False

    finally:
        if page:
            await page.close()
        if browser:
            await browser.close()  # 确保浏览器正确关闭

async def main():
    global message
    message = 'diylink自动化脚本运行\n'

    try:
        async with aiofiles.open('accounts.json', mode='r', encoding='utf-8') as f:
            accounts_json = await f.read()
        accounts = json.loads(accounts_json)
    except Exception as e:
        print(f'读取 accounts.json 文件时出错: {e}')
        return

    for account in accounts:
        username = account['username']
        password = account['password']

        is_logged_in = await login(username, password)

        if is_logged_in:
            now_utc = format_to_iso(datetime.utcnow())
            now_beijing = format_to_iso(datetime.utcnow() + timedelta(hours=8))
            success_message = f'账号 {username} 于北京时间 {now_beijing}（UTC时间 {now_utc}）登录成功！'
            message += success_message + '\n'
            print(success_message)
        else:
            message += f'账号 {username} 登录失败，请检查账号和密码是否正确。\n'
            print(f'账号 {username} 登录失败，请检查账号和密码是否正确。')

        delay = random.randint(1000, 8000)
        await delay_time(delay)
        
    message += '所有账号登录完成！'
    await send_telegram_message(message)
    print('所有账号登录完成！')

async def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': message,
        'reply_markup': {
            'inline_keyboard': [
                [
                    {
                        'text': '问题反馈❓',
                        'url': 'https://t.me/yxjsjl'
                    }
                ]
            ]
        }
    }
    headers = {
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            print(f"发送消息到Telegram失败: {response.text}")
    except Exception as e:
        print(f"发送消息到Telegram时出错: {e}")

if __name__ == '__main__':
    asyncio.run(main())
