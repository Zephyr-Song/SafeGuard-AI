"""
测试智谱AI连接
"""

import requests
import json
import sys

# 设置UTF-8输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 智谱AI配置
api_key = "b5efeb5a1d304d10aa9ce0a5284a0129.ySYT67zO996HPRvk"
model = "glm-4"
url = "https://open.bigmodel.cn/api/paas/v4/chat/completions"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

data = {
    "model": model,
    "messages": [
        {"role": "user", "content": "你好，请回复'测试成功'"}
    ],
    "temperature": 0.3,
    "max_tokens": 100
}

print("正在测试智谱AI连接...")
print(f"API地址: {url}")
print(f"模型: {model}")
print("-" * 50)

try:
    response = requests.post(url, headers=headers, json=data, timeout=30)
    
    print(f"状态码: {response.status_code}")
    print("-" * 50)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ API连接成功！")
        print("-" * 50)
        print("AI回复:")
        print(result['choices'][0]['message']['content'])
        print("\n配置正确，可以开始使用！")
    else:
        print("❌ API连接失败")
        print(f"错误信息: {response.text}")
        
except Exception as e:
    print(f"❌ 连接错误: {e}")
