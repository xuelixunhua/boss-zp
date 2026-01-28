#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
BOSS 直聘数据采集脚本
使用 DrissionPage 实现自动化采集，通过 API 拦截获取真实薪资数据

功能：
- 自动采集岗位数据
- 获取真实薪资（绕过字体编码）
- 自动翻页
- 保存为 CSV 格式

作者：参考青灯教育课程
日期：2026-01-27
"""

# 导入自动化模块
from DrissionPage import ChromiumPage
# 导入格式化输出模块
from pprint import pprint
# 导入csv模块
import csv
import time

# ==================== 配置参数 ====================

# 搜索关键词
SEARCH_QUERY = 'python'

# 城市代码
# 100010000 - 北京
# 101020100 - 上海
# 101280600 - 深圳
# 101210100 - 杭州
# 101280100 - 广州
# 101270100 - 成都
CITY_CODE = '100010000'

# 抓取页数
MAX_PAGES = 10

# 输出文件名
OUTPUT_FILE = 'data.csv'

# ==================== 主程序 ====================

def main():
    """主函数"""
    print("=" * 70)
    print("BOSS 直聘数据采集工具")
    print("=" * 70)
    print(f"\n搜索关键词: {SEARCH_QUERY}")
    print(f"城市代码: {CITY_CODE}")
    print(f"抓取页数: {MAX_PAGES}")
    print(f"输出文件: {OUTPUT_FILE}\n")

    # 创建文件对象
    f = open(file=OUTPUT_FILE, mode='w', encoding='utf-8', newline='')

    # 字典写入的方法
    csv_writer = csv.DictWriter(f, fieldnames=[
        '职位',
        '城市',
        '区域',
        '商圈',
        '公司',
        '薪资',
        '经验',
        '学历',
        '领域',
        '性质',
        '规模',
        '技能标签',
        '福利标签',
    ])

    # 写入表头
    csv_writer.writeheader()

    print("正在启动浏览器...")

    # 打开浏览器 (实例化浏览器对象)
    dp = ChromiumPage()

    print("✓ 浏览器启动成功！")

    # 监听数据包
    print("✓ 开始监听 API 请求...")
    dp.listen.start('zpgeek/search/joblist.json')

    # 构建搜索 URL
    search_url = f'https://www.zhipin.com/web/geek/job?query={SEARCH_QUERY}&city={CITY_CODE}'

    # 访问网站
    print(f"\n正在访问: {search_url}")
    dp.get(search_url)

    print("\n请在浏览器中：")
    print("  1. 完成人机验证（如果有）")
    print("  2. 登录账号（如果需要）")
    print("  3. 等待页面加载完成")

    input("\n完成后按回车键开始抓取数据...")

    # 统计数据
    total_jobs = 0

    # 构建循环翻页
    for page in range(1, MAX_PAGES + 1):
        print(f'\n{"="*70}')
        print(f'正在采集第 {page} 页的数据内容')
        print("=" * 70)

        try:
            # 下滑页面到底部
            dp.scroll.to_bottom()
            time.sleep(1)  # 等待页面加载

            # 等待数据包加载
            print("  等待 API 响应...")
            r = dp.listen.wait(timeout=10)

            if not r:
                print("  ⚠ 未捕获到 API 响应，跳过此页")
                continue

            # 获取响应数据 -> 字典数据
            json_data = r.response.body

            # 字典取值: 键值对取值 提取职位信息所在列表
            if 'zpData' not in json_data or 'jobList' not in json_data['zpData']:
                print("  ⚠ API 响应格式异常")
                continue

            jobList = json_data['zpData']['jobList']

            print(f"  ✓ 成功获取 {len(jobList)} 个岗位")

            # for循环遍历, 提取列表里面的元素
            for idx, job in enumerate(jobList, 1):
                try:
                    """循环中提取具体每条职位信息, 保存字典中"""
                    dit = {
                        '职位': job.get('jobName', ''),
                        '城市': job.get('cityName', ''),
                        '区域': job.get('areaDistrict', ''),
                        '商圈': job.get('businessDistrict', ''),
                        '公司': job.get('brandName', ''),
                        '薪资': job.get('salaryDesc', ''),  # ⭐ 真实薪资！
                        '经验': job.get('jobExperience', ''),
                        '学历': job.get('jobDegree', ''),
                        '领域': job.get('brandIndustry', ''),
                        '性质': job.get('brandStageName', ''),
                        '规模': job.get('brandScaleName', ''),
                        '技能标签': ' '.join(job.get('skills', [])),
                        '福利标签': ' '.join(job.get('welfareList', [])),
                    }

                    # 写入数据
                    csv_writer.writerow(dit)

                    # 打印数据
                    print(f"    [{idx}] {dit['职位']} | {dit['公司']} | {dit['薪资']}")

                    total_jobs += 1

                except Exception as e:
                    print(f"    ✗ 处理岗位数据出错: {e}")
                    continue

            # 点击下一页按钮
            if page < MAX_PAGES:
                print(f"\n  点击下一页...")
                try:
                    next_button = dp.ele('css:.ui-icon-arrow-right')
                    if next_button:
                        next_button.click()
                        time.sleep(2)  # 等待页面加载
                    else:
                        print("  ⚠ 未找到下一页按钮，停止抓取")
                        break
                except Exception as e:
                    print(f"  ⚠ 点击下一页失败: {e}")
                    break

        except Exception as e:
            print(f"  ✗ 抓取第 {page} 页出错: {e}")
            continue

    # 关闭文件
    f.close()

    # 显示统计
    print(f"\n{'='*70}")
    print(f"数据采集完成！")
    print("=" * 70)
    print(f"\n统计信息：")
    print(f"  - 抓取页数: {page}")
    print(f"  - 总岗位数: {total_jobs}")
    print(f"  - 输出文件: {OUTPUT_FILE}")

    print("\n" + "=" * 70)
    print("🎉 恭喜！成功获取真实薪资数据！")
    print("=" * 70)

    # 关闭浏览器
    print("\n关闭浏览器...")
    dp.quit()
    print("完成！")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n用户中断")
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
