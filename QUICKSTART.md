# 快速开始指南

## 1. 创建虚拟环境

```bash
cd /Users/richal/Tools/boss-spider
python3 -m venv venv
```

## 2. 激活虚拟环境

```bash
source venv/bin/activate
```

## 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 4. 运行程序

```bash
python boss_spider.py
```

## 5. 操作步骤

1. 程序会自动打开浏览器
2. 在浏览器中完成人机验证（如果有）
3. 登录 BOSS 直聘账号（建议）
4. 等待页面加载完成
5. 回到终端按回车键
6. 程序自动抓取数据
7. 数据保存在 `data.csv` 文件中

## 6. 自定义配置

编辑 `boss_spider.py` 文件，修改以下参数：

```python
# 搜索关键词
SEARCH_QUERY = 'python'  # 改为你想搜索的关键词

# 城市代码
CITY_CODE = '100010000'  # 改为你想搜索的城市

# 抓取页数
MAX_PAGES = 10  # 改为你想抓取的页数
```

## 7. 城市代码对照表

| 城市 | 代码 |
|------|------|
| 北京 | 100010000 |
| 上海 | 101020100 |
| 深圳 | 101280600 |
| 杭州 | 101210100 |
| 广州 | 101280100 |
| 成都 | 101270100 |

## 8. 查看数据

```bash
# 查看前 10 行
head -10 data.csv

# 或使用 Excel/Numbers 打开 data.csv
```

## 9. 常见问题

### 无法安装 DrissionPage？

```bash
pip install DrissionPage -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 浏览器无法启动？

确保已安装 Chrome 浏览器。

### 无法获取数据？

1. 确认已完成人机验证
2. 确认已登录账号
3. 检查网络连接

## 10. 停止程序

按 `Ctrl + C` 停止程序。
