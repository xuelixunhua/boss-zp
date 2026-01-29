#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
BOSS 直聘数据采集脚本
使用 DrissionPage 实现自动化采集，获取真实薪资和职位描述

功能：
- 自动采集岗位数据
- 获取真实薪资（绕过字体编码）
- 获取职位描述
- 自动翻页
- 保存为 CSV 格式
"""

from DrissionPage import ChromiumPage
from DrissionPage.common import Settings
import csv
import time

# 设置允许多对象共用标签页
Settings.set_singleton_tab_obj(False)

# ==================== 配置参数 ====================

# 搜索关键词
SEARCH_QUERY = 'agent'

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
    print(f"滚动次数: {MAX_SCROLLS}")
    print(f"输出文件: {OUTPUT_FILE}\n")

    # 创建文件对象
    f = open(file=OUTPUT_FILE, mode='w', encoding='utf-8', newline='')

    # 定义CSV字段
    csv_writer = csv.DictWriter(f, fieldnames=[
        '职位', '城市', '区域', '商圈', '公司', '薪资',
        '经验', '学历', '领域', '性质', '规模',
        '技能标签', '福利标签', '职位描述',
    ])
    csv_writer.writeheader()

    print("正在启动浏览器...")
    dp = ChromiumPage()
    print("✓ 浏览器启动成功！")

    # 访问搜索页面
    search_url = f'https://www.zhipin.com/web/geek/job?query={SEARCH_QUERY}&city={CITY_CODE}'
    print(f"\n正在访问: {search_url}")
    dp.get(search_url)

    print("\n等待页面加载，请手动完成：")
    print("  1. 人机验证（如果有）")
    print("  2. 登录账号（如果需要）")
    print(f"\n⏳ 等待 20 秒后自动开始抓取...")
    time.sleep(20)

    total_jobs = 0
    processed_job_ids = set()  # 用于去重
    all_jobs_data = []  # 存储所有职位的基本信息

    print("\n" + "=" * 70)
    print("阶段 1: 快速收集职位列表")
    print("=" * 70)

    # 第一阶段：快速滚动收集所有职位基本信息
    for scroll_count in range(1, MAX_SCROLLS + 1):
        print(f'\n第 {scroll_count} 次滚动加载')

        try:
            # 重新启动API监听
            dp.listen.start('zpgeek/search/joblist.json')

            # 多次小幅度滚动，模拟真实用户行为
            print("  正在滚动页面...")
            for i in range(3):
                dp.scroll.down(500)  # 每次向下滚动500像素
                time.sleep(0.5)

            # 最后滚动到底部
            dp.scroll.to_bottom()
            time.sleep(3)  # 增加等待时间，确保数据加载

            # 等待列表API响应
            r = dp.listen.wait(timeout=10)
            if not r:
                print("  ⚠ 未捕获到 API 响应，继续滚动")
                continue

            json_data = r.response.body
            if 'zpData' not in json_data or 'jobList' not in json_data['zpData']:
                print("  ⚠ API 响应格式异常")
                continue

            jobList = json_data['zpData']['jobList']
            new_jobs = 0

            print(f"  ✓ 获取到 {len(jobList)} 个岗位数据")

            # 遍历职位列表，只收集基本信息
            for idx, job in enumerate(jobList, 1):
                try:
                    job_id = job.get('encryptJobId', '')

                    # 去重检查
                    if job_id in processed_job_ids:
                        continue

                    processed_job_ids.add(job_id)
                    new_jobs += 1

                    # 保存职位基本信息和详情页参数
                    job_data = {
                        'job': job,
                        'security_id': job.get('securityId', ''),
                        'lid': json_data.get('zpData', {}).get('lid', ''),
                        'job_id': job_id
                    }
                    all_jobs_data.append(job_data)

                    print(f"    [收集] {job.get('jobName', '')} | {job.get('brandName', '')} | {job.get('salaryDesc', '')}")
                    total_jobs += 1

                except Exception as e:
                    print(f"    ✗ 处理岗位数据出错: {e}")
                    continue

            print(f"  本次新增 {new_jobs} 个岗位，累计 {total_jobs} 个")

            # 如果连续3次没有新数据，说明已经到底
            if new_jobs == 0:
                if scroll_count >= 3:  # 至少滚动3次
                    print("\n  ℹ 没有更多新数据，停止滚动")
                    break
                else:
                    print("  继续尝试加载...")

            # 滚动间隔，避免请求过快
            time.sleep(1)

        except Exception as e:
            print(f"  ✗ 第 {scroll_count} 次滚动出错: {e}")
            continue

    # 第二阶段：批量获取职位详情
    print("\n" + "=" * 70)
    print(f"阶段 2: 获取职位详情 (共 {len(all_jobs_data)} 个)")
    print("=" * 70)

    for idx, job_data in enumerate(all_jobs_data, 1):
        try:
            job = job_data['job']
            job_id = job_data['job_id']
            security_id = job_data['security_id']
            lid = job_data['lid']
            post_desc = ''

            # 获取职位描述
            if job_id and security_id:
                try:
                    detail_url = f'https://www.zhipin.com/job_detail/{job_id}.html?securityId={security_id}&lid={lid}'
                    dp.get(detail_url)
                    time.sleep(2)

                    # 从页面提取职位描述
                    desc_element = dp.ele('css:.job-detail-section')
                    if not desc_element:
                        desc_element = dp.ele('css:.job-sec-text')

                    if desc_element:
                        post_desc = desc_element.text

                except Exception as e:
                    print(f"  ⚠ 获取详情失败: {e}")

            # 提取职位信息
            dit = {
                '职位': job.get('jobName', ''),
                '城市': job.get('cityName', ''),
                '区域': job.get('areaDistrict', ''),
                '商圈': job.get('businessDistrict', ''),
                '公司': job.get('brandName', ''),
                '薪资': job.get('salaryDesc', ''),
                '经验': job.get('jobExperience', ''),
                '学历': job.get('jobDegree', ''),
                '领域': job.get('brandIndustry', ''),
                '性质': job.get('brandStageName', ''),
                '规模': job.get('brandScaleName', ''),
                '技能标签': ' '.join(job.get('skills', [])),
                '福利标签': ' '.join(job.get('welfareList', [])),
                '职位描述': post_desc,
            }

            csv_writer.writerow(dit)
            f.flush()

            print(f"  [{idx}/{len(all_jobs_data)}] {dit['职位']} | {dit['公司']} | {'✓ 有描述' if post_desc else '✗ 无描述'}")

        except Exception as e:
            print(f"  ✗ 处理岗位 {idx} 出错: {e}")
            continue

    f.close()

    # 显示统计
    print(f"\n{'='*70}")
    print(f"数据采集完成！")
    print("=" * 70)
    print(f"\n统计信息：")
    print(f"  - 总岗位数: {total_jobs}")
    print(f"  - 输出文件: {OUTPUT_FILE}")
    print("\n" + "=" * 70)

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
