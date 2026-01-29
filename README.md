# BOSS 直聘职位分析工具

## 项目简介

使用 DrissionPage 实现 BOSS 直聘岗位数据采集，通过 API 拦截技术获取真实薪资数据，并使用大模型自动生成技术栈分析报告和学习路线。

## 功能特点

- ✅ 自动化采集岗位数据
- ✅ 获取真实薪资信息（绕过字体编码）
- ✅ 自动翻页抓取多页数据
- ✅ 获取职位详细描述
- ✅ 智能技术栈分析（关键词 + 大模型）
- ✅ 自动生成学习路线报告（Markdown 格式）
- ✅ 一键运行，无需手动操作

## 技术栈

- Python 3.9+
- DrissionPage - 浏览器自动化
- python-dotenv - 环境变量管理
- 通义千问/OpenAI/DeepSeek - 大模型分析（可选）

## 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux

# 安装依赖
pip install -r requirements.txt
```

### 2. 配置 API Key（可选，用于大模型分析）

编辑 `.env` 文件：

```bash
QWEN_API_KEY=your_api_key_here
```

### 3. 一键运行

```bash
# 修改 run.py 中的搜索关键词
# SEARCH_QUERY = 'AI工程师'

# 运行
python run.py
```

**就这么简单！** 等待完成后，会在浏览器中自动打开 `tech_stack_analysis.md` 报告。

---

## 📖 使用流程

### 方式一：完整自动化流程（推荐）

```bash
# 1. 修改 run.py 中的搜索关键词
# 2. 运行一键脚本
source venv/bin/activate
python run.py
```

### 方式二：分步执行

#### 步骤1：数据采集
```bash
source venv/bin/activate
python boss_spider.py
```
- 会生成 `data.csv` 文件
- 如果在**阶段2**中止，已采集的数据��保存到CSV

#### 步骤2：生成分析报告
```bash
python analyze_tech_stack.py
```
- 读取 `data.csv`
- 生成 `tech_stack_analysis.md`（人类可读报告）
- 生成 `tech_stack_analysis.json`（详细数据）

---

## 🔄 中断后如何恢复

### 情况1：在阶段1（滚动收集）中止
- 数据不完整，建议重新运行爬虫
- 命令：`python boss_spider.py`

### 情况2：在阶段2（获取详情）中止
- **已有数据在 `data.csv` 中**
- 直接运行分析即可生成报告
- 命令：`python analyze_tech_stack.py`

### 情况3：分析阶段中止
- 直接重新运行分析即可
- 命令：`python analyze_tech_stack.py`

---

## 📁 输出文件说明

| 文件 | 说明 | 用途 |
|------|------|------|
| `tech_stack_analysis.md` | Markdown格式的学习路线报告 | **主要查看这个** |
| `tech_stack_analysis.json` | JSON格式详细数据 | 程序读取 |
| `data.csv` | 原始职位数据 | 备份查看 |

---

## ⚙️ 配置参数

### 在 `run.py` 中修改：

```python
# 搜索关键词
SEARCH_QUERY = 'AI工程师'    # 修改这里

# 城市代码
CITY_CODE = '101020100'      # 上海

# 滚动次数（采集数量）
MAX_SCROLLS = 20

# 是否启用大模型分析
USE_LLM_ANALYSIS = True
```

### 城市代码对照表

| 城市 | 代码 |
|------|------|
| 北京 | 100010000 |
| 上海 | 101020100 |
| 深圳 | 101280600 |
| 杭州 | 101210100 |
| 广州 | 101280100 |
| 成都 | 101270100 |

---

## 💡 使用技巧

1. **首次使用**：建议先测试小数据量，设置 `MAX_SCROLLS = 3`
2. **大量采集**：设置 `MAX_SCROLLS = 50` 可采集约 750 个职位
3. **关闭大模型**：如果不需要深度分析，设置 `USE_LLM_ANALYSIS = False`
4. **查看进度**：爬虫运行时会显示当前进度和采集数量

---

## ❓ 常见问题

### Q: 如何只生成报告，不重新采集？
A: 直接运行 `python analyze_tech_stack.py`

### Q: 阶段2太慢，可以跳过吗？
A: 可以，注释掉 `boss_spider.py` 中的阶段2代码（第168-224行）

### Q: 想分析其他城市的职位？
A: 修改 `run.py` 中的 `CITY_CODE` 参数

### Q: 报告中的技能等级是怎么分的？
A: 由大模型（通义千问）根据职位描述自动分析得出

### Q: 无法获取数据？
A: 检查是否完成人机验证、确认已登录 BOSS 直聘、检查网络连接

### Q: 薪资显示为编码字符？
A: 本项目使用 API 拦截技术，直接获取 JSON 数据，不会出现字体编码问题

---

## 项目结构

```
boss-spider/
├── README.md                 # 项目说明
├── USAGE.md                  # 快速使用指南
├── run.py                    # 一键运行脚本 ⭐
├── boss_spider.py            # 爬虫主程序
├── analyze_tech_stack.py     # 技术栈分析模块
├── ai_analyzer.py            # 大模型集成
├── requirements.txt          # 依赖列表
├── .env                      # 环境变量配置
├── data.csv                  # 原始职位数据（运行后生成）
├── tech_stack_analysis.json  # JSON格式分析结果（运行后生成）
├── tech_stack_analysis.md    # Markdown学习路线报告（运行后生成）
└── venv/                     # 虚拟环境
```

---

## 数据字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| 职位 | 岗位名称 | AI工程师 |
| 城市 | 所在城市 | 上海 |
| 区域 | 所在区域 | 浦东新区 |
| 商圈 | 所在商圈 | 张江 |
| 公司 | 公司名称 | 某某科技 |
| 薪资 | 薪资范围（真实数据） | 25-45K·16薪 |
| 经验 | 经验要求 | 3-5年 |
| 学历 | 学历要求 | 本科 |
| 领域 | 行业领域 | 人工智能 |
| 性质 | 公司性质 | B轮 |
| 规模 | 公司规模 | 100-499人 |
| 技能标签 | 技能要求 | Python LangChain LLM |
| 福利标签 | 福利待遇 | 五险一金 股票期权 |
| 职位描述 | 完整职位描述 | 岗位职责、任职要求等 |

---

## 技术原理

### API 拦截

```python
# 监听 API 接口
dp.listen.start('zpgeek/search/joblist.json')

# 等待响应
r = dp.listen.wait()

# 获取 JSON 数据（包含真实薪资）
json_data = r.response.body
```

### 两阶段采集策略

**阶段1：快速收集职位列表**
- 专注滚动和收集职位基本信息
- 不跳转详情页，避免打断流程
- 数据暂存到内存

**阶段2：批量获取职位详情**
- 滚动完成后统一获取详情
- 提取职位描述信息
- 写入 CSV 文件

### 大模型分析

使用通义千问/OpenAI/DeepSeek 等大模型，对职位描述进行深度分析，生成：
- 核心技术栈
- 初级/中级/高级技能要求
- 完整学习路线（10步）
- 差异化竞争优势

---

## 注意事项

1. **仅供学习和研究使用**
   - 请遵守网站服务条款
   - 避免频繁请求

2. **数据采集**
   - 建议设置合理的延迟时间
   - 首次运行需要手动完成人机验证
   - 建议登录 BOSS 直聘账号

3. **大模型分析**
   - 需要配置有效的 API Key
   - 分析需要一定时间，请耐心等待
   - 可关闭大模型分析，仅使用关键词匹配

---

## 许可证

MIT License
