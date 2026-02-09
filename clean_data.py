#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据清洗脚本
功能：
1. 重新解析 salary_text_raw 计算年薪
2. 清洗JD中的噪音文本
3. 去重（company_name_std + job_title + city）
4. 输出清洗后的CSV
"""

import csv
import re
import os

def parse_salary(salary_text):
    """解析薪资文本，计算年薪"""
    if not salary_text or salary_text == '面议':
        return {'months': 12, 'min_year': None, 'max_year': None, 'avg_year': None}

    salary_months = 12
    months_match = re.search(r'(\d+)薪', salary_text)
    if months_match:
        salary_months = int(months_match.group(1))

    # 处理 "元/天" 格式
    if '元/天' in salary_text:
        daily_match = re.search(r'(\d+\.?\d*)[-~]?(\d+\.?\d*)?元\/天', salary_text)
        if daily_match:
            min_daily = float(daily_match.group(1))
            max_daily = float(daily_match.group(2)) if daily_match.group(2) else min_daily
            # 转换为年薪：日薪 * 21.75天 * 12月
            min_year = int(min_daily * 21.75 * 12)
            max_year = int(max_daily * 21.75 * 12)
            return {
                'months': salary_months,
                'min_year': min_year,
                'max_year': max_year,
                'avg_year': (min_year + max_year) // 2
            }

    # 处理 "K" 或 "万" 格式
    # 先标准化文本：全角转半角，移除所有空格
    salary_text_normalized = salary_text.replace('－', '-').replace('～', '~').replace(' ', '')

    # 匹配各种格式
    # 1. "15-25K" 或 "15-25K·13薪"
    salary_match = re.search(r'(\d+\.?\d*)[-~](\d+\.?\d*)[kK](?:·?\d+薪)?', salary_text_normalized)

    if not salary_match:
        # 2. "15K-25K"
        salary_match = re.search(r'(\d+\.?\d*)[kK][-~](\d+\.?\d*)[kK]', salary_text_normalized)

    if not salary_match:
        # 3. "30-50万"
        salary_match = re.search(r'(\d+\.?\d*)[-~](\d+\.?\d*)万', salary_text_normalized)

    if salary_match:
        min_salary = float(salary_match.group(1))
        max_salary = float(salary_match.group(2))

        # 检查是否是"万"
        if '万' in salary_text[:salary_match.end()]:
            min_salary *= 10
            max_salary *= 10

        min_year = int(min_salary * 1000 * salary_months)
        max_year = int(max_salary * 1000 * salary_months)

        return {
            'months': salary_months,
            'min_year': min_year,
            'max_year': max_year,
            'avg_year': (min_year + max_year) // 2
        }

    return {'months': salary_months, 'min_year': None, 'max_year': None, 'avg_year': None}

def clean_jd_text(jd_text):
    """清洗JD中的噪音文本"""
    if not jd_text:
        return ''

    # 移除所有噪音模式的变体
    noise_patterns = [
        r'微信扫码.*',
        r'来自.*?直聘',
        r'BOSS直聘',
        r'boss报',
        r'boss分享',
        r'kanzhun.*',
        r'举报',
        r'分享',
        r'直聘',
        r'享举',
        r'\s+boss\s+',
        r'\s+直聘\s+',
        r'^\s+',  # 开头空白
        r'\s+$',  # 结尾空白
    ]

    cleaned = jd_text
    for pattern in noise_patterns:
        cleaned = re.sub(pattern, ' ', cleaned, flags=re.IGNORECASE)

    # 清理多余空白
    cleaned = re.sub(r'\s+', ' ', cleaned)

    return cleaned.strip()

def main():
    input_file = 'boss_jobs_progress.csv'
    output_file = 'boss_jobs_cleaned_北京2.csv'

    print(f"正在读取 {input_file}...")

    # 读取数据
    jobs = []
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            jobs.append(row)

    print(f"原始记录：{len(jobs)} 条")

    # 清洗数据
    print("正在清洗数据（前5条会显示详情）...")
    seen = set()
    cleaned_jobs = []

    for job in jobs:
        # 去重键
        dedup_key = f"{job['company_name_std']}_{job['job_title']}_{job['city']}"
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        # 解析薪资（前5条显示调试信息）
        salary_info = parse_salary(job['salary_text_raw'])
        if len(cleaned_jobs) < 5:
            print(f"\n  [{len(cleaned_jobs)+1}] 薪资文本: '{job['salary_text_raw']}'")
            print(f"      解析结果: {salary_info}")

        job['salary_months'] = salary_info['months']
        job['salary_min_year_rmb'] = salary_info['min_year']
        job['salary_max_year_rmb'] = salary_info['max_year']
        job['salary_avg_year_rmb'] = salary_info['avg_year']

        # 清洗JD（前5条显示调试信息）
        original_jd = job['jd_text'][:50] if job['jd_text'] else ''
        job['jd_text'] = clean_jd_text(job['jd_text'])
        if len(cleaned_jobs) < 5 and original_jd:
            print(f"      JD原文: '{original_jd}...'")
            print(f"      JD清洗: '{job['jd_text'][:50]}...'")

        # 更新notes
        notes = []
        if salary_info['avg_year'] is None:
            notes.append(f"无法解析薪资: {job['salary_text_raw']}")
        if not job['jd_text']:
            notes.append("无JD描述")
        job['notes'] = '; '.join(notes) if notes else ''

        cleaned_jobs.append(job)

    print(f"去重后：{len(cleaned_jobs)} 条")

    # 统计有效数据
    valid_salary = [j for j in cleaned_jobs if j['salary_avg_year_rmb']]
    valid_jd = [j for j in cleaned_jobs if j['jd_text'] and len(j['jd_text']) > 50]

    print(f"有效薪资数据：{len(valid_salary)} 条")
    print(f"有效JD数据：{len(valid_jd)} 条")

    # 保存清洗后的数据
    print(f"正在保存到 {output_file}...")
    fieldnames = [
        'keyword_group', 'search_keyword', 'city', 'job_title',
        'company_name_raw', 'company_name_std', 'company_type',
        'salary_text_raw', 'salary_months', 'salary_min_year_rmb',
        'salary_max_year_rmb', 'salary_avg_year_rmb',
        'exp_req', 'edu_req', 'jd_text', 'post_date', 'source_url',
        'collected_at', 'notes'
    ]

    with open(output_file, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(cleaned_jobs)

    print(f"✓ 清洗完成！")
    print(f"  原始数据：{len(jobs)} 条")
    print(f"  清洗后：{len(cleaned_jobs)} 条")
    print(f"  有效薪资：{len(valid_salary)} 条 ({len(valid_salary)/len(cleaned_jobs)*100:.1f}%)")
    print(f"  有效JD：{len(valid_jd)} 条 ({len(valid_jd)/len(cleaned_jobs)*100:.1f}%)")
    print(f"  输出文件：{output_file}")

if __name__ == '__main__':
    main()
