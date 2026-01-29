# 大模型集成使用指南

## 快速开始

### 1. 选择 AI 服务商

| 服务商 | 优点 | 缺点 | 费用 |
|--------|------|------|------|
| **OpenAI** | 效果最好，支持 GPT-4 | 需要科学上网 | $0.002/1K tokens |
| **通义千问** | 国内访问快，免费额度 | 效果略逊 | 有免费额度 |
| **文心一言** | 国内访问快，免费额度 | 效果略逊 | 有免费额度 |

### 2. 获取 API Key

#### OpenAI
1. 访问 https://platform.openai.com/api-keys
2. 注册账号（需要国外手机号）
3. 创建 API Key
4. 充值（最低 $5）

#### 通义千问（推荐国内用户）
1. 访问 https://dashscope.console.aliyun.com/
2. 登录阿里云账号
3. 开通 DashScope 服务
4. 创建 API Key（有免费额度）

#### 文心一言
1. 访问 https://console.bce.baidu.com/qianfan/
2. 登录百度账号
3. 创建应用，获取 API Key 和 Secret Key

### 3. 配置环境变量

创建 `.env` 文件：

```bash
# OpenAI 配置
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
OPENAI_BASE_URL=https://api.openai.com/v1

# 或使用通义千问
QWEN_API_KEY=sk-xxxxxxxxxxxxx

# 或使用文心一言
ERNIE_API_KEY=xxxxxxxxxxxxx
ERNIE_SECRET_KEY=xxxxxxxxxxxxx

# 启用 AI 分析
USE_AI_ANALYSIS=true
AI_PROVIDER=openai  # 或 qwen, ernie
```

### 4. 安装依赖

```bash
# 激活虚拟环境
source venv/bin/activate

# 安装 OpenAI SDK
pip install openai

# 或安装通义千问 SDK
pip install dashscope

# 或安装 requests（文心一言）
pip install requests
```

### 5. 运行分析

```bash
# 方式1：使用关键词提取（不需要 API Key）
python analyze_tech_stack.py

# 方式2：使用 AI 深度分析（需要 API Key）
export USE_AI_ANALYSIS=true
export AI_PROVIDER=openai  # 或 qwen, ernie
python analyze_tech_stack.py
```

## 完整工作流程

```bash
# 1. 爬取职位数据
python boss_spider.py

# 2. 分析技术栈
python analyze_tech_stack.py

# 3. 查看结果
cat tech_stack_analysis.json
```

## 代码示例

### 直接调用 AI 分析

```python
from ai_analyzer import analyze_with_ai

# 准备职位数据
jobs = [
    {'职位': 'AI工程师', '描述': '...'},
    {'职位': 'Python开发', '描述': '...'}
]

# 使用 OpenAI 分析
result = analyze_with_ai(jobs, provider='openai')
print(result)

# 使用通义千问分析
result = analyze_with_ai(jobs, provider='qwen')
print(result)
```

## 费用说明

### OpenAI
- GPT-4o-mini: $0.15/1M input tokens, $0.60/1M output tokens
- 分析 100 个职位约 $0.05-0.10

### 通义千问
- 免费额度：100万 tokens/月
- 超出后：¥0.008/1K tokens

### 文心一言
- 免费额度：50万 tokens/月
- 超出后：¥0.012/1K tokens

## 常见问题

### Q: OpenAI API 无法访问？
A: 使用国内中转服务，修改 `OPENAI_BASE_URL`

### Q: 如何降低费用？
A:
1. 使用 gpt-4o-mini 而不是 gpt-4
2. 只分析前 50 个职位
3. 使用国内服务（通义千问、文心一言）

### Q: 不想用 API，有其他方案吗？
A: 可以使用本地模型（Ollama + Llama）或关键词提取模式

## 进阶：集成到主程序

修改 `analyze_tech_stack.py`，在 `main()` 函数末尾添加：

```python
# 如果启用 AI 分析
if USE_AI_ANALYSIS:
    from ai_analyzer import analyze_with_ai

    print("\n开始 AI 深度分析...")
    ai_result = analyze_with_ai(descriptions, provider=AI_PROVIDER)

    if ai_result:
        report['AI分析结果'] = ai_result
        print("\n" + "="*70)
        print("AI 分析结果：")
        print("="*70)
        print(ai_result)
```

## 推荐配置

**新手推荐**：通义千问（免费额度足够，国内访问快）

**追求效果**：OpenAI GPT-4o-mini（效果好，费用低）

**完全免费**：关键词提取模式（不需要 API Key）
