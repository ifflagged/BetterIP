# -- coding: utf-8 --
import os
import sys
import time
from curl_cffi import requests
from turnstile_solver import TurnstileSolver, TurnstileSolverError
from yescaptcha import YesCaptchaSolver, YesCaptchaSolverError

# 配置参数
API_BASE_URL = os.environ.get("API_BASE_URL", "")
CLIENTT_KEY = os.environ.get("CLIENTT_KEY", "")
NS_RANDOM = os.environ.get("NS_RANDOM", "true")
SOLVER_TYPE = os.environ.get("SOLVER_TYPE", "turnstile")

def save_cookie_to_github_var(var_name: str, cookie: str):
    """将Cookie保存到GitHub仓库变量中"""
    import requests as py_requests
    token = os.environ.get("GH_PAT")
    repo = os.environ.get("GITHUB_REPOSITORY")
    if not token or not repo:
        print("GH_PAT 或 GITHUB_REPOSITORY 未设置，跳过变量更新")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    url_check = f"https://api.github.com/repos/{repo}/actions/variables/{var_name}"
    url_create = f"https://api.github.com/repos/{repo}/actions/variables"

    data = {"name": var_name, "value": cookie}

    response = py_requests.patch(url_check, headers=headers, json=data)
    if response.status_code == 204:
        print(f"{var_name} 更新成功")
    elif response.status_code == 404:
        print(f"{var_name} 不存在，尝试创建...")
        response = py_requests.post(url_create, headers=headers, json=data)
        if response.status_code == 201:
            print(f"{var_name} 创建成功")
        else:
            print("创建失败:", response.status_code, response.text)
    else:
        print("设置失败:", response.status_code, response.text)

# 自动保存cookie到青龙面板
def save_cookie_to_qinglong(var_name, cookie_value):
    """将Cookie保存到青龙面板环境变量"""
    import requests
    import json
    import time
    
    # 获取青龙面板配置
    ql_url = os.environ.get("QL_URL")
    client_id = os.environ.get("QL_CLIENT_ID")
    client_secret = os.environ.get("QL_CLIENT_SECRET")
    
    if not all([ql_url, client_id, client_secret]):
        print("未设置青龙面板API配置，无法保存Cookie")
        return False
        
    # 获取青龙API令牌
    token_url = f"{ql_url}/open/auth/token"
    token_params = {
        'client_id': client_id,
        'client_secret': client_secret
    }
    
    try:
        token_resp = requests.get(token_url, params=token_params)
        token_data = token_resp.json()
        
        if token_data.get('code') != 200:
            print(f"获取青龙面板令牌失败: {token_data}")
            return False
            
        token = token_data['data']['token']
        
        # 设置API请求头
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        # 查询变量是否存在
        envs_url = f"{ql_url}/open/envs"
        envs_resp = requests.get(envs_url, headers=headers)
        envs_data = envs_resp.json()
        
        if envs_data.get('code') != 200:
            print(f"查询环境变量失败: {envs_data}")
            return False
            
        # 查找指定变量
        env_id = None
        for env in envs_data['data']:
            if env['name'] == var_name:
                env_id = env['id']
                break
                
        # 更新或创建变量
        remarks = f"NodeSeek签到自动更新-{time.strftime('%Y-%m-%d %H:%M:%S')}"
        
        if env_id:  # 更新现有变量
            update_data = {
                "id": env_id,
                "name": var_name,
                "value": cookie_value,
                "remarks": remarks
            }
            update_resp = requests.put(envs_url, headers=headers, json=update_data)
            update_result = update_resp.json()
            
            if update_result.get('code') == 200:
                print(f"成功更新青龙环境变量: {var_name}")
                return True
            else:
                print(f"更新环境变量失败: {update_result}")
                return False
        else:  # 创建新变量
            create_data = [{
                "name": var_name,
                "value": cookie_value,
                "remarks": remarks
            }]
            create_resp = requests.post(envs_url, headers=headers, json=create_data)
            create_result = create_resp.json()
            
            if create_result.get('code') == 200:
                print(f"成功创建青龙环境变量: {var_name}")
                return True
            else:
                print(f"创建环境变量失败: {create_result}")
                return False
                
    except Exception as e:
        print(f"调用青龙API出错: {e}")
        return False
    
# 多账号支持
def parse_multi_accounts():
    """解析环境变量中的多账号信息，支持&和换行符作为分隔符"""
    accounts = []
    
    # 获取所有可能的账号配置
    all_users = []
    all_passes = []
    all_cookies = []
    
    # 解析USER/USER数字格式
    base_user = os.environ.get("NS_USERNAME", "")
    if base_user:
        all_users.append(base_user)
    
    for i in range(1, 100):
        user_key = f"NS_USERNAME{i}"
        if user_key in os.environ and os.environ[user_key]:
            all_users.append(os.environ[user_key])
        else:
            break
    
    # 解析PASS/PASS数字格式
    base_pass = os.environ.get("NS_PASSWORD", "")
    if base_pass:
        all_passes.append(base_pass)
    
    for i in range(1, 100):
        pass_key = f"NS_PASSWORD{i}"
        if pass_key in os.environ and os.environ[pass_key]:
            all_passes.append(os.environ[pass_key])
        else:
            break
    
    # 解析NS_COOKIES
    cookie_str = os.environ.get("NS_COOKIES", "")
    if cookie_str:
        # 支持&和换行符作为分隔符
        for separator in ["&", "\n"]:
            if separator in cookie_str:
                all_cookies = cookie_str.split(separator)
                all_cookies = [c.strip() for c in all_cookies if c.strip()]
                break
        else:
            all_cookies = [cookie_str]
    
    # 组合账号信息
    # 1. 如果有cookie，先添加只有cookie的账号
    for i, cookie in enumerate(all_cookies):
        username = f"账号{i+1}" if i >= len(all_users) else all_users[i]
        password = "" if i >= len(all_passes) else all_passes[i]
        accounts.append({"NS_USERNAME": username, "NS_PASSWORD": password, "cookie": cookie})
    
    # 2. 如果有用户名密码但没有对应cookie的账号
    for i in range(len(all_cookies), max(len(all_users), len(all_passes))):
        if i < len(all_users) and all_users[i]:
            username = all_users[i]
            password = all_passes[i] if i < len(all_passes) else ""
            accounts.append({"NS_USERNAME": username, "NS_PASSWORD": password, "cookie": ""})
    
    return accounts

def load_send():
    global send
    global hadsend
    cur_path = os.path.abspath(os.path.dirname(__file__))
    sys.path.append(cur_path)
    if os.path.exists(cur_path + "/notify.py"):
        try:
            from notify import send
            hadsend = True
        except:
            print("加载notify.py的通知服务失败，请检查~")
            hadsend = False
    else:
        print("加载通知服务失败,缺少notify.py文件")
        hadsend = False

load_send()


def session_login(username, password):
    # 根据环境变量选择使用哪个验证码解决器
    try:
        if SOLVER_TYPE.lower() == "yescaptcha":
            print("正在使用 YesCaptcha 解决验证码...")
            solver = YesCaptchaSolver(
                api_base_url="https://api.yescaptcha.com",
                client_key=CLIENTT_KEY
            )
        else:  # 默认使用 turnstile_solver
            print("正在使用 TurnstileSolver 解决验证码...")
            solver = TurnstileSolver(
                api_base_url=API_BASE_URL,
                client_key=CLIENTT_KEY
            )
        
        token = solver.solve(
            url="https://www.nodeseek.com/signIn.html",
            sitekey="0x4AAAAAAAaNy7leGjewpVyR",
            verbose=True
        )
        
        if not token:
            print("获取验证码令牌失败，无法登录")
            return None
            
    except (TurnstileSolverError, YesCaptchaSolverError) as e:
        print(f"验证码解析错误: {e}")
        return None
    except Exception as e:
        print(f"获取验证码过程中发生异常: {e}")
        return None
    
    # 创建会话并登录
    session = requests.Session(impersonate="chrome110")
    
    try:
        session.get("https://www.nodeseek.com/signIn.html")
    except Exception as e:
        print(f"访问登录页面失败: {e}")
    
    url = "https://www.nodeseek.com/api/account/signIn"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        'sec-ch-ua': "\"Not A(Brand\";v=\"99\", \"Microsoft Edge\";v=\"121\", \"Chromium\";v=\"121\"",
        'sec-ch-ua-mobile': "?0",
        'sec-ch-ua-platform': "\"Windows\"",
        'origin': "https://www.nodeseek.com",
        'sec-fetch-site': "same-origin",
        'sec-fetch-mode': "cors",
        'sec-fetch-dest': "empty",
        'referer': "https://www.nodeseek.com/signIn.html",
        'accept-language': "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
        'Content-Type': "application/json"
    }
    
    data = {
        "username": username,
        "password": password,
        "token": token,
        "source": "turnstile"
    }
    
    try:
        response = session.post(url, json=data, headers=headers)
        response_data = response.json()
        print(response_data)
        
        if response_data.get('success') == True:
            
            cookie_dict = session.cookies.get_dict()
            cookie_string = '; '.join([f"{name}={value}" for name, value in cookie_dict.items()])
            #print(f"获取到的Cookie: {cookie_string}")
            
            return cookie_string
        else:
            message = response_data.get('message', '登录失败')
            print(f"登录失败: {message}")
            return None
    except Exception as e:
        print("登录异常:", e)
        print("实际响应内容:", response.text if 'response' in locals() else "没有响应")
        return None


def sign(cookie):
    if not cookie:
        print("请先设置Cookie")
        return "no_cookie", ""
        
    url = f"https://www.nodeseek.com/api/attendance?random={NS_RANDOM}"
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0",
        'origin': "https://www.nodeseek.com",
        'referer': "https://www.nodeseek.com/board",
        'Cookie': cookie
    }

    try:
        response = requests.post(url, headers=headers, impersonate="chrome110")
        response_data = response.json()
        print(f"签到返回: {response_data}")
        message = response_data.get('message', '')
        
        # 简化判断逻辑
        if "鸡腿" in message or response_data.get('success') == True:
            # 如果消息中包含"鸡腿"或success为True，都视为签到成功
            print(f"签到成功: {message}")
            return "success", message
        elif "已完成签到" in message:
            print(f"已经签到过: {message}")
            return "already_signed", message
        elif message == "USER NOT FOUND" or response_data.get('status') == 404:
            print("Cookie已失效")
            return "invalid_cookie", message
        else:
            print(f"签到失败: {message}")
            return "fail", message
            
    except Exception as e:
        print("发生异常:", e)
        return "error", str(e)

if __name__ == "__main__":
    # 解析多账号信息
    accounts = parse_multi_accounts()
    
    if not accounts:
        print("未找到任何账号信息")
        if hadsend:
            send("nodeseek签到", "未找到任何账号信息")
        exit(0)
    
    # 存储所有账号的通知信息
    all_messages = []
    # 用于收集有效的Cookie
    valid_cookies = []
    
    # 循环处理每个账号
    for i, account in enumerate(accounts):
        account_name = account["NS_USERNAME"] if account["NS_USERNAME"] else f"账号{i+1}"
        print(f"\n===== 开始处理{account_name} =====")
        
        # 尝试使用现有Cookie签到
        sign_result, sign_message = "no_cookie", ""
        
        if account["cookie"]:
            sign_result, sign_message = sign(account["cookie"])
        
        # 处理签到结果
        if sign_result in ["success", "already_signed"]:
            status = "签到成功" if sign_result == "success" else "今天已经签到过了"
            print(f"{account_name}: {status}")
            all_messages.append(f"{account_name}: {sign_message}")
            # 收集有效的Cookie
            valid_cookies.append(account["cookie"])
        else:
            # 签到失败或没有Cookie，尝试登录
            if account["NS_USERNAME"] and account["NS_PASSWORD"]:
                print(f"{account_name}: 尝试登录获取新Cookie...")
                cookie = session_login(account["NS_USERNAME"], account["NS_PASSWORD"])
                if cookie:
                    print(f"{account_name}: 登录成功，使用新Cookie签到")
                    account["cookie"] = cookie
                    sign_result, sign_message = sign(cookie)
                    
                    status = "签到成功" if sign_result in ["success", "already_signed"] else "签到失败"
                    print(f"{account_name}: {status}")
                    
                    message = f"{account_name}: {sign_message}"
                    if sign_result in ["success", "already_signed"]:
                        message += f"\nCookie: {cookie}"
                        # 收集新获取的有效Cookie
                        valid_cookies.append(cookie)
                    all_messages.append(message)
                else:
                    print(f"{account_name}: 登录失败")
                    all_messages.append(f"{account_name}: 登录失败")
            else:
                print(f"{account_name}: 无法执行操作：没有有效Cookie且未设置用户名密码")
                all_messages.append(f"{account_name}: 无法执行操作：没有有效Cookie且未设置用户名密码")
    
    # 发送合并后的通知
    if hadsend and all_messages:
        send("nodeseek多账号签到", "\n\n".join(all_messages))
    
    # 保存所有有效Cookie到GitHub变量
# 保存所有有效Cookie
if valid_cookies:
    combined_cookies = "&".join(valid_cookies)
    print(f"共收集到{len(valid_cookies)}个有效Cookie")
    
    # 检查是否在GitHub Actions环境
    if os.environ.get("GITHUB_ACTIONS") == "true":
        print("\n===== 保存Cookie到GitHub变量 =====")
        # 将Cookie保存到GitHub变量
        try:
            save_cookie_to_github_var("NS_COOKIES", combined_cookies)
            print("Cookie已成功保存到GitHub变量")
        except Exception as e:
            print(f"保存Cookie到GitHub变量时出现错误: {e}")
    
    # 检查是否存在青龙面板配置
    elif os.environ.get("QL_URL"):
        print("\n===== 保存Cookie到青龙面板环境变量 =====")
        # 将Cookie保存到青龙面板环境变量
        try:
            save_result = save_cookie_to_qinglong("NS_COOKIES", combined_cookies)
            if save_result:
                print("Cookie已成功保存到青龙面板环境变量")
            else:
                print("保存Cookie到青龙面板环境变量失败")
        except Exception as e:
            print(f"保存Cookie到青龙面板环境变量时出现错误: {e}")
    else:
        print("\n未检测到GitHub Actions或青龙面板环境，新Cookie将不会被自动保存")
        if len(valid_cookies) > 0:
            print("\n以下是有效的Cookie，可以手动更新：")
            for i, cookie in enumerate(valid_cookies):
                print(f"账号{i+1}: {cookie}")
