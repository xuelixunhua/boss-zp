# 技术栈分析工具使用指南

## 快速开始

### 1. 不使用大模型（免费）

直接运行，使用关键词提取：

```bash
python analyze_tech_stack.py
```

### 2. 使用大模型（需要 API Key）

#### 方案 A：通义千问（推荐，国内最方便）

**步骤 1：获取 API Key**
1. 访问 https://dashscope.aliyun.com/
2. 注册/登录阿里云账号
3. 开通 DashScope 服务（有免费额度）
4. 创建 API Key

**步骤 2：安装依赖**
```bash
pip install dashscope
```

**步骤 3：配置 API Key**
```bash
# 方式1：设置环境变量（推荐）
export QWEN_API_KEY="your_api_key_here"

# 方式2：直接修改代码
# 编辑 analyze_tech_stack.py，找到 API_KEYS，填入你的 key
```

**步骤 4：启用大模型**
编辑 `analyze_tech_stack.py`，修改：
```python
USE_LLM = True  # 改为 True
LLM_PROVIDER = 'qwen'
```

**步骤 5：运行**
```bash
python analyze_tech_stack.py
```

---

#### 方案 B：OpenAI GPT-4（效果最好）

**步骤 1：获取 API Key**
1. 访问 https://platform.openai.com/
2. 注册账号（需要科学上网）
3. 充值（最低 $5）
4. 创建 API Key

**步骤 2：安装依赖**
```bash
pip install openai
```

**步骤 3：配置**
```bash
export OPENAI_API_KEY="sk-..."
```

编辑代码：
```python
USE_LLM = True
LLM_PROVIDER = 'openai'
```

---

#### 方案 C：DeepSeek（便宜，效果好）

**步骤 1：获取 API Key**
1. 访问 https://platform.deepseek.com/
2. 注册账号
3. 充值（很便宜，1元可以用很久）
4. 创建 API Key

**步骤 2：安装依赖**
```bash
pip install openai
```

**步骤 3：配置**
```bash
export DEEPSEEK_API_KEY="sk-..."
```

编辑代码：
```python
USE_LLM = True
LLM_PROVIDER = 'deepseek'
```

---

## 输出说明

### 1. 控制台输出
- 高频技术 Top 10
- 学习建议

### 2. JSON 文件
`tech_stack_analysis.json` 包含：
- 完整技术栈统计
- 高频技术列表
- 学习建议
- 大模型分析结果（如果启用）

---

## 费用说明

| 大模型 | 费用 | 说明 |
|--------|------|------|
| 关键词提取 | 免费 | 本地运行 |
| 通义千问 | ~0.01元/次 | 有免费额度 |
| DeepSeek | ~0.001元/次 | 非常便宜 |
| OpenAI GPT-4 | ~0.5元/次 | 较贵 |

---

## 常见问题

**Q: 没有职位描述数据？**
A: 先运行爬虫：`python boss_spider.py`

**Q: API Key 不生效？**
A: 检查环境变量是否设置成功：`echo $QWEN_API_KEY`

**Q: 想换其他大模型？**
A: 修改 `LLM_PROVIDER` 参数即可

**Q: 大模型分析失败？**
A: 会自动降级到关键词提取，不影响基础功能
