#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
大模型集成模块 - 支持多种 AI 服务
"""

import os
import json
from openai import OpenAI

# ==================== 配置 ====================

# OpenAI 配置
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', 'your-api-key-here')
OPENAI_BASE_URL = os.getenv('OPENAI_BASE_URL', 'https://api.openai.com/v1')  # 可改为中转地址

# 通义千问配置
QWEN_API_KEY = os.getenv('QWEN_API_KEY', 'your-api-key-here')

# 文心一言配置
ERNIE_API_KEY = os.getenv('ERNIE_API_KEY', 'your-api-key-here')
ERNIE_SECRET_KEY = os.getenv('ERNIE_SECRET_KEY', 'your-secret-key-here')

# ==================== OpenAI 实现 ====================

def analyze_with_openai(job_descriptions):
    """使用 OpenAI 分析职位描述"""

    client = OpenAI(
        api_key=OPENAI_API_KEY,
        base_url=OPENAI_BASE_URL
    )

    # 构造提示词
    prompt = f"""
你是一位资深的技术招聘专家和职业规划顾问。请分析以下 {len(job_descriptions)} 个职位描述，提取共性技术栈。

职位描述：
{json.dumps(job_descriptions[:10], ensure_ascii=False, indent=2)}

请按以下格式输出：

1. **核心技术栈**（按重要性排序）
   - 编程语言：
   - 框架/库：
   - 数据库：
   - 工具/平台：

2. **技能要求等级**
   - 必须掌握（出现频率>70%）：
   - 优先掌握（出现频率30-70%）：
   - 加分项（出现频率<30%）：

3. **学习路线建议**
   - 第一阶段（基础）：
   - 第二阶段（进阶）：
   - 第三阶段（高级）：

4. **资源推荐**
   - 推荐学习资源（书籍、课程、文档）

请用中文回答，内容要具体、可操作。
"""

    print("正在调用 OpenAI API 分析...")

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # 或 gpt-4, gpt-3.5-turbo
        messages=[
            {"role": "system", "content": "你是一位资深的技术招聘专家和职业规划顾问。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )

    result = response.choices[0].message.content
    print("✓ 分析完成！")

    return result


# ==================== 通义千问实现 ====================

def analyze_with_qwen(job_descriptions):
    """使用通义千问分析职位描述"""

    try:
        import dashscope
        from dashscope import Generation
    except ImportError:
        print("⚠ 请先安装通义千问 SDK: pip install dashscope")
        return None

    dashscope.api_key = QWEN_API_KEY

    prompt = f"""
分析以下职位描述，提取共性技术栈和学习建议：

{json.dumps(job_descriptions[:10], ensure_ascii=False, indent=2)}

请输出：
1. 核心技术栈（按频率排序）
2. 技能要求等级
3. 学习路线建议
"""

    print("正在调用通义千问 API 分析...")

    response = Generation.call(
        model='qwen-max',  # 或 qwen-turbo, qwen-plus
        prompt=prompt
    )

    if response.status_code == 200:
        result = response.output.text
        print("✓ 分析完成！")
        return result
    else:
        print(f"✗ 调用失败: {response.message}")
        return None


# ==================== 文心一言实现 ====================

def analyze_with_ernie(job_descriptions):
    """使用文心一言分析职位描述"""

    try:
        import requests
    except ImportError:
        print("⚠ 请先安装 requests: pip install requests")
        return None

    # 获取 access_token
    token_url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={ERNIE_API_KEY}&client_secret={ERNIE_SECRET_KEY}"
    token_response = requests.get(token_url)
    access_token = token_response.json().get('access_token')

    if not access_token:
        print("✗ 获取 access_token 失败")
        return None

    prompt = f"""
分析以下职位描述，提取共性技术栈：

{json.dumps(job_descriptions[:10], ensure_ascii=False, indent=2)}

请输出核心技术栈和学习建议。
"""

    print("正在调用文心一言 API 分析...")

    url = f"https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/completions?access_token={access_token}"

    payload = json.dumps({
        "messages": [
            {"role": "user", "content": prompt}
        ]
    })

    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        result = response.json().get('result', '')
        print("✓ 分析完成！")
        return result
    else:
        print(f"✗ 调用失败: {response.text}")
        return None


# ==================== 统一接口 ====================

def analyze_with_ai(job_descriptions, provider='openai'):
    """
    使用 AI 分析职位描述

    Args:
        job_descriptions: 职位描述列表
        provider: AI 服务提供商 ('openai', 'qwen', 'ernie')

    Returns:
        分析结果文本
    """

    if provider == 'openai':
        return analyze_with_openai(job_descriptions)
    elif provider == 'qwen':
        return analyze_with_qwen(job_descriptions)
    elif provider == 'ernie':
        return analyze_with_ernie(job_descriptions)
    else:
        print(f"✗ 不支持的 AI 服务: {provider}")
        return None


# ==================== 测试 ====================

if __name__ == '__main__':
    # 测试数据
    test_jobs = [
        {
            '职位': 'AI Agent 开发工程师',
            '描述': '负责 AI Agent 开发，要求熟悉 Python、LangChain、OpenAI API，了解 RAG 技术'
        },
        {
            '职位': 'Python 后端工程师',
            '描述': '负责后端开发，要求熟悉 Python、Django、MySQL、Redis'
        }
    ]

    # 使用 OpenAI 分析
    result = analyze_with_ai(test_jobs, provider='openai')

    if result:
        print("\n" + "="*70)
        print("分析结果：")
        print("="*70)
        print(result)
