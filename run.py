#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
BOSS 直聘职位分析一键运行脚本

使用方法：
1. 修改下面的 SEARCH_QUERY 和 CITY_CODE
2. 运行: python3 run.py
3. 等待生成 tech_stack_analysis.md 报告
"""

import os
import sys
import subprocess

# ==================== 配置参数 ====================

# 搜索关键词
SEARCH_QUERY = 'AI工程师'

# 城市代码
# 100010000 - 北京
# 101020100 - 上海
# 101280600 - 深圳
# 101210100 - 杭州
# 101280100 - 广州
# 101270100 - 成都
CITY_CODE = '101020100'

# 滚动次数（每次滚动会加载约15条数据）
MAX_SCROLLS = 20

# 是否启用大模型深度分析
USE_LLM_ANALYSIS = True

# ==================================================


def print_banner():
    """打印横幅"""
    print("\n" + "=" * 70)
    print(" BOSS 直聘职位分析工具".center(70))
    print("=" * 70)
    print(f"\n📋 配置信息:")
    print(f"  搜索关键词: {SEARCH_QUERY}")
    print(f"  城市: {get_city_name(CITY_CODE)}")
    print(f"  滚动次数: {MAX_SCROLLS}")
    print(f"  大模型分析: {'✓ 启用' if USE_LLM_ANALYSIS else '✗ 禁用'}")
    print("\n" + "=" * 70)


def get_city_name(code):
    """获取城市名称"""
    city_map = {
        '100010000': '北京',
        '101020100': '上海',
        '101280600': '深圳',
        '101210100': '杭州',
        '101280100': '广州',
        '101270100': '成都'
    }
    return city_map.get(code, code)


def update_config():
    """更新配置文件"""
    print("\n📝 正在更新配置...")

    # 更新 boss_spider.py 的配置
    with open('boss_spider.py', 'r', encoding='utf-8') as f:
        content = f.read()

    # 替换搜索关键词
    content = replace_config(content, "SEARCH_QUERY = .*", f"SEARCH_QUERY = '{SEARCH_QUERY}'")
    content = replace_config(content, "CITY_CODE = .*", f"CITY_CODE = '{CITY_CODE}'")
    content = replace_config(content, "MAX_SCROLLS = .*", f"MAX_SCROLLS = {MAX_SCROLLS}")

    with open('boss_spider.py', 'w', encoding='utf-8') as f:
        f.write(content)

    # 更新 analyze_tech_stack.py 的配置
    with open('analyze_tech_stack.py', 'r', encoding='utf-8') as f:
        content = f.read()

    content = replace_config(content, "USE_LLM = .*", f"USE_LLM = {USE_LLM_ANALYSIS}")

    with open('analyze_tech_stack.py', 'w', encoding='utf-8') as f:
        f.write(content)

    print("  ✓ 配置已更新")


def replace_config(content, pattern, replacement):
    """替换配置"""
    import re
    return re.sub(pattern, replacement, content)


def run_spider():
    """运行爬虫"""
    print("\n" + "=" * 70)
    print(" 阶段 1: 数据采集".center(70))
    print("=" * 70)

    print("\n🕷️  正在启动爬虫...")
    print("⚠️  请在浏览器中完成以下操作:")
    print("  1. 完成人机验证（如果有）")
    print("  2. 登录账号（如果需要）")
    print("\n⏳ 爬虫将自动运行，请勿关闭浏览器...\n")

    try:
        result = subprocess.run(
            [sys.executable, 'boss_spider.py'],
            check=True,
            capture_output=False
        )
        print("\n✓ 数据采集完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 数据采集失败: {e}")
        return False


def run_analysis():
    """运行分析"""
    print("\n" + "=" * 70)
    print(" 阶段 2: 技术栈分析".center(70))
    print("=" * 70)

    print("\n🔬 正在分析技术栈...")

    try:
        result = subprocess.run(
            [sys.executable, 'analyze_tech_stack.py'],
            check=True,
            capture_output=False
        )
        print("\n✓ 技术栈分析完成")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ 技术栈分析失败: {e}")
        return False


def show_result():
    """显示结果"""
    print("\n" + "=" * 70)
    print(" 分析完成".center(70))
    print("=" * 70)

    # 检查文件是否存在
    json_file = 'tech_stack_analysis.json'
    md_file = 'tech_stack_analysis.md'
    csv_file = 'data.csv'

    print("\n📁 生成的文件:")

    if os.path.exists(md_file):
        print(f"  ✓ {md_file} (人类可读的学习路线报告)")
    if os.path.exists(json_file):
        print(f"  ✓ {json_file} (JSON格式详细数据)")
    if os.path.exists(csv_file):
        print(f"  ✓ {csv_file} (原始职位数据)")

    print("\n" + "=" * 70)

    # 尝试在默认浏览器中打开 Markdown 文件
    if os.path.exists(md_file):
        try:
            import subprocess
            if sys.platform == 'darwin':  # macOS
                subprocess.run(['open', md_file], check=True)
            elif sys.platform == 'win32':  # Windows
                os.startfile(md_file)
            else:  # Linux
                subprocess.run(['xdg-open', md_file], check=True)
            print(f"💡 已在浏览器中打开 {md_file}")
        except:
            print(f"\n💡 请手动打开 {md_file} 查看学习路线")

    print("\n" + "=" * 70)


def main():
    """主函数"""
    print_banner()

    # 1. 更新配置
    update_config()

    # 2. 运行爬虫
    if not run_spider():
        print("\n✗ 流程中断")
        return

    # 3. 运行分析
    if not run_analysis():
        print("\n✗ 流程中断")
        return

    # 4. 显示结果
    show_result()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
