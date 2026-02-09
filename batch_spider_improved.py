#!/usr/bin/env python3
# -*- coding:utf-8 -*-
"""
BOSS直聘批量数据采集脚本（改进版）
改进点：
1. 边采集边保存，Ctrl+C不会丢失数据
2. 使用API获取详情，避免跳转页面
3. 增加更长的延迟时间
4. 实时保存进度，支持断点续传
"""

from DrissionPage import ChromiumPage
from DrissionPage.common import Settings
import csv
import time
import re
import random
import os
from datetime import datetime
from collections import defaultdict
import signal
import sys

# 设置允许多对象共用标签页
Settings.set_singleton_tab_obj(False)

# ==================== 配置参数 ====================

SEARCH_CONFIGS = {
    'keywords': ['能源管理'],
    'cities': {
        '北京': '101010100',
    }
}

MAX_SCROLLS = 5

# 输出文件
OUTPUT_FILE = 'boss_jobs_progress.csv'
PROGRESS_FILE = 'progress_state.txt'

# 反检测配置
MIN_DELAY = 5
MAX_DELAY = 10
DETAIL_PAGE_DELAY = 8  # 详情页延迟更长（秒）

# ==================== 全局变量（用于断点续传）====================

all_jobs_data = []
processed_count = 0

def signal_handler(sig, frame):
    """处理Ctrl+C，保存已采集的数据"""
    print(f"\n\n检测到用户中断...")
    print(f"正在保存已采集的 {len(all_jobs_data)} 条数据...")

    save_data_immediately(all_jobs_data)
    print(f"✓ 数据已保存到: {OUTPUT_FILE}")
    print(f"✓ 共保存 {len(all_jobs_data)} 条职位数据")

    sys.exit(0)

# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)

# ==================== 工具函数 ====================

def random_delay():
    """随机延迟"""
    delay = random.uniform(MIN_DELAY, MAX_DELAY)
    time.sleep(delay)

def normalize_company_name(company_name):
    """公司名称归一化"""
    if not company_name:
        return '未知公司'
    company_name = re.sub(r'(有限公司|股份有限公司|责任有限公司|集团|科技|网络|信息技术|电子|系统|集成|发展|控股|投资|咨询|管理|服务|教育|文化|传媒|环境|能源|电力|新能源|智能|数据|软件|平台)$', '', company_name)
    company_name = re.sub(r'\([^)]*\)', '', company_name)
    company_name = re.sub(r'（[^）]*）', '', company_name)
    company_name = company_name.strip()
    return company_name if company_name else '未知公司'

def classify_company_type(company_name_raw, nature, scale):
    """判断公司性质"""
    name = company_name_raw.lower() if company_name_raw else ''

    soe_keywords = ['国家电网', '南方电网', '华能', '大唐', '华电', '国电', '中电投',
                    '中石油', '中石化', '中海油', '国家能源', '中广核', '华润',
                    '中国电信', '中国移动', '中国联通', '中铁', '中建', '中交',
                    '三峡集团', '中核', '中航', '航天科工', '航天科技',
                    '电力公司', '能源集团', '发电集团', '电网公司',
                    '研究院', '设计院', '研究所', '科学院', '大学',
                    '集团', '股份', '国投', '电投', '能源']

    foreign_keywords = ['特斯拉', '宝马', '奔驰', '大众', '西门子', '施耐德', 'abb',
                       '通用电气', '霍尼韦尔', '艾默生', '三菱', '东芝', '日立',
                       'lg', '三星', 'sk', '现代', '微软', '谷歌', '亚马逊',
                       '苹果', '英特尔', 'amd', '英伟达', '高通', '博世',
                       '（中国）', '(中国)', '（上海）', '(上海)']

    startup_keywords = ['创业', '天使', '孵化', '科技', '智能', '新能源科技',
                       '有限合伙', '工作室']

    for keyword in soe_keywords:
        if keyword in name:
            return '央国企/事业单位'

    for keyword in foreign_keywords:
        if keyword in name:
            return '外企/合资'

    for keyword in startup_keywords:
        if keyword in name:
            return '初创/创业公司'

    if nature:
        if 'A轮' in nature or 'B轮' in nature or 'C轮' in nature or 'D轮' in nature:
            return '初创/创业公司'
        elif '上市' in nature or 'IPO' in nature:
            return '民营/上市/大型企业'
        elif '不需要融资' in nature or '已上市' in nature:
            return '民营/上市/大型企业'

    if scale and ('10000人以上' in scale or '500-9999人' in scale or '1000-9999人' in scale):
        return '民营/上市/大型企业'

    return '其他/不确定'

def parse_salary(salary_text):
    """解析薪资"""
    if not salary_text or salary_text == '面议':
        return (None, None, None, None, '面议')

    notes = ''
    salary_months_match = re.search(r'(\d+)薪', salary_text)
    if salary_months_match:
        salary_months = int(salary_months_match.group(1))
    else:
        salary_months = 12
        notes = '默认12薪'

    salary_pattern = r'(\d+\.?\d*)[kK万]-?(\d+\.?\d*)[kK万]?'
    salary_match = re.search(salary_pattern, salary_text)

    if not salary_match:
        return (salary_months, None, None, None, f'无法解析: {salary_text}')

    min_salary = float(salary_match.group(1))
    max_salary = float(salary_match.group(2))

    if '万' in salary_text[:salary_match.end()]:
        min_salary *= 10
        max_salary *= 10

    min_year = int(min_salary * 1000 * salary_months)
    max_year = int(max_salary * 1000 * salary_months)
    avg_year = (min_year + max_year) // 2

    return (salary_months, min_year, max_year, avg_year, notes)

def save_data_immediately(jobs_data):
    """立即保存数据（边采集边保存）"""
    if not jobs_data:
        return

    # 处理数据
    seen = set()
    unique_jobs = []

    for job in jobs_data:
        company_std = normalize_company_name(job['company_name_raw'])
        dedup_key = f"{company_std}_{job['job_title']}_{job['city']}"

        if dedup_key not in seen:
            seen.add(dedup_key)

            job['company_name_std'] = company_std
            job['company_type'] = classify_company_type(
                job['company_name_raw'],
                job.get('_raw_nature', ''),
                job.get('_raw_scale', '')
            )

            salary_months, min_year, max_year, avg_year, notes = parse_salary(job['salary_text_raw'])
            job['salary_months'] = salary_months
            job['salary_min_year_rmb'] = min_year
            job['salary_max_year_rmb'] = max_year
            job['salary_avg_year_rmb'] = avg_year

            job_notes = []
            if notes:
                job_notes.append(notes)
            if not job.get('jd_text'):
                job_notes.append('无职位描述')
            if job['company_type'] == '其他/不确定':
                job_notes.append('公司性质不确定')

            job['notes'] = '; '.join(job_notes) if job_notes else ''
            job['keyword_group'] = job['keyword']

            unique_jobs.append(job)

    # 保存到CSV
    fieldnames = [
        'keyword_group', 'search_keyword', 'city', 'job_title',
        'company_name_raw', 'company_name_std', 'company_type',
        'salary_text_raw', 'salary_months', 'salary_min_year_rmb',
        'salary_max_year_rmb', 'salary_avg_year_rmb',
        'exp_req', 'edu_req', 'jd_text', 'post_date', 'source_url',
        'collected_at', 'notes'
    ]

    # 写入临时文件
    temp_file = OUTPUT_FILE + '.tmp'
    with open(temp_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()

        for job in unique_jobs:
            writer.writerow({k: job.get(k, '') for k in fieldnames})

    # 重命名为正式文件
    if os.path.exists(temp_file):
        if os.path.exists(OUTPUT_FILE):
            os.remove(OUTPUT_FILE)
        os.rename(temp_file, OUTPUT_FILE)

# ==================== 使用API获取详情（不跳转页面）====================

import json

def get_job_detail_api(dp, job_id, security_id, lid):
    try:
        dp.listen.start('zpgeek/job/detail/info.json')

        detail_url = (
            "https://www.zhipin.com/wapi/zpgeek/job/detail/info.json"
            f"?jobId={job_id}&securityId={security_id}&lid={lid}"
        )

        dp.run_js(f'''
        fetch("{detail_url}", {{
            method: "GET",
            credentials: "include",
            headers: {{
                "accept": "application/json",
                "x-requested-with": "XMLHttpRequest"
            }}
        }});
        ''')

        r = dp.listen.wait(timeout=10)
        if not r or not r.response:
            return ''

        body = r.response.body

        # 关键：把 body 统一解析为 dict
        if isinstance(body, (bytes, bytearray)):
            body = body.decode('utf-8', errors='ignore')
        if isinstance(body, str):
            body = json.loads(body)

        if isinstance(body, dict) and body.get('code') == 0 and 'zpData' in body:
            job_detail = body['zpData']
            job_info = (job_detail or {}).get('jobInfo', {}) or {}

            jd_text = (
                job_info.get('jobDescription', '') or
                job_info.get('positionRemark', '') or
                (job_info.get('responsibility', '') + job_info.get('requirement', ''))
            )
            return jd_text.strip()

        return ''

    except Exception as e:
        print(f"    ⚠ API获取详情失败: {e}")
        return ''


def get_job_detail_click(dp, job_id, security_id, lid):
    """
    备用方案：点击职位后在右侧弹窗查看详情

    这种方式也不需要跳转页面
    """
    try:
        # 找到职位卡片并点击
        job_card = dp.ele(f'xpath://a[contains(@href, "{job_id}")]')
        if job_card:
            # 点击职位
            dp.actions.click(job_card)
            time.sleep(3)

            # 从右侧弹窗获取详情
            detail_panel = dp.ele('css:.job-detail-container') or dp.ele('css:.job-detail-box')
            if detail_panel:
                return detail_panel.text

        return ''

    except Exception as e:
        print(f"    ⚠ 点击获取详情失败: {e}")
        return ''

# ==================== 主采集函数 ====================

def collect_jobs_improved(keyword, city_name, city_code):
    """改进的采集函数"""
    global all_jobs_data

    print(f"\n{'='*70}")
    print(f"正在采集: {city_name} - {keyword}")
    print(f"{'='*70}")

    dp = ChromiumPage()

    # 先访问首页
    print("访问BOSS直聘首页...")
    dp.get('https://www.zhipin.com/')
    time.sleep(3)

    # 访问搜索页面
    search_url = f'https://www.zhipin.com/web/geek/job?query={keyword}&city={city_code}'
    print(f"访问搜索页面: {search_url}")
    dp.get(search_url)

    print("\n⏳ 等待页面加载（30秒）...")
    print("提示：请手动完成人机验证和登录")

    for i in range(30, 0, -5):
        print(f"  倒计时: {i} 秒", end='\r')
        time.sleep(5)
    print("\n")

    # 检查是否被封
    page_text = dp.html.lower()
    if '异常' in page_text or '禁止' in page_text or '账号存在异常' in page_text:
        print("❌ 检测到账号异常或被封禁")
        dp.quit()
        return []

    jobs_data = []
    processed_job_ids = set()

    # 阶段1：滚动收集职位列表
    print(f"\n开始滚动收集（最多 {MAX_SCROLLS} 次）...")

    for scroll_count in range(1, MAX_SCROLLS + 1):
        print(f'\n第 {scroll_count} 次滚动')

        try:
            dp.listen.start('zpgeek/search/joblist.json')

            # 滚动
            scroll_times = random.randint(2, 4)
            for i in range(scroll_times):
                scroll_distance = random.randint(300, 600)
                dp.scroll.down(scroll_distance)
                time.sleep(random.uniform(0.3, 0.8))

            random_delay()
            dp.scroll.to_bottom()
            time.sleep(random.uniform(2, 4))

            # 等待API
            r = dp.listen.wait(timeout=15)
            if not r:
                print("  ⚠ 未捕获到API响应")
                random_delay()
                continue

            json_data = r.response.body
            if 'zpData' not in json_data or 'jobList' not in json_data['zpData']:
                print("  ⚠ API响应格式异常")
                random_delay()
                continue

            jobList = json_data['zpData']['jobList']
            new_jobs = 0

            for job in jobList:
                job_id = job.get('encryptJobId', '')

                if job_id in processed_job_ids:
                    continue

                processed_job_ids.add(job_id)
                new_jobs += 1

                job_info = {
                    'keyword': keyword,
                    'search_keyword': keyword,
                    'city': city_name,
                    'job_title': job.get('jobName', ''),
                    'company_name_raw': job.get('brandName', ''),
                    'salary_text_raw': job.get('salaryDesc', ''),
                    'exp_req': job.get('jobExperience', ''),
                    'edu_req': job.get('jobDegree', ''),
                    'post_date': job.get('lastUpdateDate', ''),
                    'source_url': f"https://www.zhipin.com/job_detail/{job_id}.html",
                    'collected_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    '_raw_nature': job.get('brandStageName', ''),
                    '_raw_scale': job.get('brandScaleName', ''),
                    '_raw_district': job.get('areaDistrict', ''),
                    '_raw_business': job.get('businessDistrict', ''),
                    '_raw_industry': job.get('brandIndustry', ''),
                    '_raw_skills': ' '.join(job.get('skills', [])),
                    '_raw_welfare': ' '.join(job.get('welfareList', [])),
                    '_security_id': job.get('securityId', ''),
                    '_lid': json_data.get('zpData', {}).get('lid', ''),
                    '_job_id': job_id
                }

                jobs_data.append(job_info)
                print(f"  ✓ [{len(jobs_data)}] {job_info['job_title'][:25]} | {job_info['company_name_raw'][:20]}")

            print(f"  本次新增: {new_jobs}, 累计: {len(jobs_data)}")

            # 每次滚动后立即保存
            if jobs_data:
                all_jobs_data.extend(jobs_data)
                save_data_immediately(all_jobs_data)
                jobs_data = []  # 清空临时列表

            if new_jobs == 0 and scroll_count >= 2:
                print("  没有更多数据，停止滚动")
                break

            random_delay()

        except Exception as e:
            print(f"  ✗ 出错: {e}")
            random_delay()
            continue

    # 阶段2：获取职位详情（使用API，不跳转）
    print(f"\n开始获取职位详情（使用API，避免跳转）...")

    all_jobs_with_details = []

    for idx, job in enumerate(all_jobs_data):
        try:
            job_id = job.get('_job_id', '')
            security_id = job.get('_security_id', '')
            lid = job.get('_lid', '')

            # 先尝试API方式
            jd_text = get_job_detail_api(dp, job_id, security_id, lid)

            # 如果API失败，尝试点击方式
            if not jd_text:
                jd_text = get_job_detail_click(dp, job_id, security_id, lid)

            job['jd_text'] = jd_text if jd_text else ''

            all_jobs_with_details.append(job)

            status = '✓ 有描述' if jd_text else '✗ 无描述'
            print(f"  [{idx+1}/{len(all_jobs_data)}] {job['job_title'][:25]} | {status}")

            # 每获取5个详情就保存一次
            if (idx + 1) % 5 == 0:
                save_data_immediately(all_jobs_with_details)
                print(f"    💾 已保存 {len(all_jobs_with_details)} 条数据")

            # 更长的延迟，避免触发检测
            delay = random.uniform(DETAIL_PAGE_DELAY - 2, DETAIL_PAGE_DELAY + 2)
            print(f"    等待 {delay:.1f} 秒...")
            time.sleep(delay)

        except Exception as e:
            print(f"  ✗ 处理职位 {idx+1} 出错: {e}")
            all_jobs_with_details.append(job)  # 即使出错也保留
            continue

    dp.quit()
    print(f"\n✓ 采集完成，共获取 {len(all_jobs_with_details)} 条职位数据")

    return all_jobs_with_details

# ==================== 主函数 ====================

def main():
    """主函数"""
    print("="*70)
    print("BOSS直聘批量数据采集工具（改进版）")
    print("="*70)
    print(f"\n改进点：")
    print(f"  1. 边采集边保存，Ctrl+C不会丢失数据")
    print(f"  2. 使用API获取详情，避免跳转页面")
    print(f"  3. 更长的延迟时间（5-10秒）")
    print(f"  4. 实时保存进度")

    print(f"\n当前配置:")
    print(f"- 关键词: {', '.join(SEARCH_CONFIGS['keywords'])}")
    print(f"- 城市: {', '.join(SEARCH_CONFIGS['cities'].keys())}")
    print(f"- 滚动次数: {MAX_SCROLLS}")

    input("\n按Enter键开始采集...")

    for keyword in SEARCH_CONFIGS['keywords']:
        for city_name, city_code in SEARCH_CONFIGS['cities'].items():
            try:
                jobs = collect_jobs_improved(keyword, city_name, city_code)

                # 保存最终数据
                if jobs:
                    save_data_immediately(jobs)
                    print(f"\n✓ {city_name}-{keyword} 数据已保存")

                time.sleep(10)

            except Exception as e:
                print(f"✗ 采集失败: {city_name} - {keyword}, 错误: {e}")
                continue

    print(f"\n{'='*70}")
    print("全部完成！")
    print(f"{'='*70}")
    print(f"\n✓ 最终文件: {OUTPUT_FILE}")
    print(f"✓ 共保存: {len(all_jobs_data)} 条职位数据")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        signal_handler(None, None)
    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
