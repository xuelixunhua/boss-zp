#!/usr/bin/python
# -*- coding:utf-8 -*-
"""
职位技术栈分析模块
从 CSV 文件读取职位描述，分析共性技术栈，输出学习建议
"""

import csv
import re
from collections import Counter
import json
import os

# ==================== 配置参数 ====================

# 输入文件（爬虫生成的数据）
INPUT_FILE = 'data.csv'

# 输出文件
OUTPUT_FILE = 'tech_stack_analysis.json'

# 大模型配置
USE_LLM = False  # 是否使用大模型分析（需要 API Key）
LLM_PROVIDER = 'qwen'  # 可选: 'qwen'(通义千问), 'openai', 'deepseek'

# API Key 配置（从环境变量读取，更安全）
# 使用方法：export QWEN_API_KEY="your_api_key"
API_KEYS = {
    'qwen': os.getenv('QWEN_API_KEY', ''),
    'openai': os.getenv('OPENAI_API_KEY', ''),
    'deepseek': os.getenv('DEEPSEEK_API_KEY', '')
}

# 技术栈关键词库
TECH_KEYWORDS = {
    '编程语言': [
        'Python', 'Java', 'JavaScript', 'TypeScript', 'Go', 'Golang',
        'C++', 'C#', 'Rust', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Scala'
    ],
    '前端框架': [
        'React', 'Vue', 'Angular', 'Next.js', 'Nuxt.js',
        'uni-app', 'Flutter', 'Electron', 'React Native'
    ],
    '后端框架': [
        'Django', 'Flask', 'FastAPI', 'Spring Boot', 'Spring Cloud',
        'Express', 'Koa', 'Egg.js', 'Gin', 'Beego', 'Laravel'
    ],
    'AI/ML框架': [
        'PyTorch', 'TensorFlow', 'Keras', 'scikit-learn', 'Pandas',
        'NumPy', 'Transformers', 'LangChain', 'OpenAI API', 'LLM',
        'Agent', 'RAG', 'Fine-tuning', 'Prompt Engineering'
    ],
    '数据库': [
        'MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'Elasticsearch',
        'ClickHouse', 'Doris', 'Hive', 'HBase', 'OceanBase'
    ],
    '中间件/工具': [
        'Kafka', 'RabbitMQ', 'RocketMQ', 'Docker', 'Kubernetes',
        'K8s', 'Jenkins', 'Git', 'GitLab', 'Linux', 'Nginx'
    ],
    '云平台': [
        'AWS', 'Azure', 'GCP', '阿里云', '腾讯云', '华为云',
        'Serverless', 'Lambda', 'Function Compute'
    ]
}

# ==================== 大模型集成 ====================

def call_llm_analysis(descriptions, tech_stats):
    """使用大模型进行深度分析"""
    if not USE_LLM:
        return None

    api_key = API_KEYS.get(LLM_PROVIDER)
    if not api_key:
        print(f"\n⚠ 未配置 {LLM_PROVIDER} 的 API Key，跳过大模型分析")
        return None

    print(f"\n🤖 使用 {LLM_PROVIDER} 进行深度分析...")

    # 准备提示词
    prompt = build_analysis_prompt(descriptions, tech_stats)

    # 调用对应的大模型
    try:
        if LLM_PROVIDER == 'qwen':
            result = call_qwen_api(prompt, api_key)
        elif LLM_PROVIDER == 'openai':
            result = call_openai_api(prompt, api_key)
        elif LLM_PROVIDER == 'deepseek':
            result = call_deepseek_api(prompt, api_key)
        else:
            print(f"⚠ 不支持的大模型: {LLM_PROVIDER}")
            return None

        print("✓ 大模型分析完成")
        return result

    except Exception as e:
        print(f"⚠ 大模型调用失败: {e}")
        return None


def build_analysis_prompt(descriptions, tech_stats):
    """构建分析提示词"""
    # 提取高频技术
    all_techs = []
    for category, counter in tech_stats.items():
        for tech, count in counter.most_common(10):
            all_techs.append(f"{tech}({count}次)")

    tech_summary = ", ".join(all_techs[:30])

    # 提取部分职位描述样本
    sample_descs = [d['描述'][:200] for d in descriptions[:5]]

    prompt = f"""请分析以下 {len(descriptions)} 个 AI Agent 相关职位的技术栈需求：

高频技术统计：
{tech_summary}

职位描述样本：
{chr(10).join([f"{i+1}. {desc}..." for i, desc in enumerate(sample_descs)])}

请从以下角度分析：
1. 核心技术栈（必须掌握的技术，按重要性排序）
2. 技能等级要求（初级/中级/高级分别需要掌握什么）
3. 学习路线建议（从零开始的学习顺序）
4. 差异化竞争力（哪些技术能让你脱颖而出）

请以 JSON 格式输出，包含以下字段：
{{
  "核心技术栈": ["技术1", "技术2", ...],
  "技能等级": {{"初级": [...], "中级": [...], "高级": [...]}},
  "学习路线": ["步骤1", "步骤2", ...],
  "差异化技术": ["技术1", "技术2", ...]
}}
"""
    return prompt


def call_qwen_api(prompt, api_key):
    """调用通义千问 API"""
    try:
        import dashscope
        from dashscope import Generation
    except ImportError:
        print("⚠ 请先安装 dashscope: pip install dashscope")
        return None

    dashscope.api_key = api_key

    response = Generation.call(
        model='qwen-plus',  # 或 'qwen-max' 效果更好但更贵
        prompt=prompt,
        result_format='message'
    )

    if response.status_code == 200:
        content = response.output.choices[0].message.content
        # 尝试解析 JSON
        try:
            return json.loads(content)
        except:
            return {"分析结果": content}
    else:
        raise Exception(f"API 调用失败: {response.message}")


def call_openai_api(prompt, api_key):
    """调用 OpenAI API"""
    try:
        from openai import OpenAI
    except ImportError:
        print("⚠ 请先安装 openai: pip install openai")
        return None

    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4",  # 或 'gpt-3.5-turbo' 更便宜
        messages=[
            {"role": "system", "content": "你是一个技术招聘和职业规划专家。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except:
        return {"分析结果": content}


def call_deepseek_api(prompt, api_key):
    """调用 DeepSeek API（兼容 OpenAI 格式）"""
    try:
        from openai import OpenAI
    except ImportError:
        print("⚠ 请先安装 openai: pip install openai")
        return None

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个技术招聘和职业规划专家。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7
    )

    content = response.choices[0].message.content
    try:
        return json.loads(content)
    except:
        return {"分析结果": content}


# ==================== 核心功能 ====================

def load_job_descriptions(csv_file):
    """从CSV文件加载职位描述"""
    descriptions = []

    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            desc = row.get('职位描述', '').strip()
            if desc and len(desc) > 10:
                descriptions.append({
                    '职位': row.get('职位', ''),
                    '公司': row.get('公司', ''),
                    '薪资': row.get('薪资', ''),
                    '描述': desc
                })

    print(f"✓ 加载了 {len(descriptions)} 个职位描述")
    return descriptions


def extract_tech_stack(descriptions):
    """从职位描述中提取技术栈关键词"""
    print("\n开始分析技术栈...")

    tech_stats = {category: Counter() for category in TECH_KEYWORDS}
    total_jobs = len(descriptions)

    for idx, job in enumerate(descriptions, 1):
        desc = job['描述']

        # 遍历所有技术类别
        for category, keywords in TECH_KEYWORDS.items():
            for keyword in keywords:
                # 不区分大小写匹配
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                if pattern.search(desc):
                    tech_stats[category][keyword] += 1

        if idx % 10 == 0:
            print(f"  已分析 {idx}/{total_jobs} 个职位...")

    return tech_stats


def generate_analysis_report(tech_stats, total_jobs):
    """生成分析报告"""
    report = {
        '总职位数': total_jobs,
        '分析时间': None,
        '技术栈统计': {},
        '高频技术': {},
        '学习建议': []
    }

    # 统计每个技术类别
    for category, counter in tech_stats.items():
        if counter:
            # 计算出现频率
            freq = {tech: {'出现次数': count, '占比': f"{count/total_jobs*100:.1f}%"}
                   for tech, count in counter.most_common()}

            report['技术栈统计'][category] = {
                '技术列表': freq,
                '总计': len(counter),
                '最常用': counter.most_common(1)[0][0] if counter else None
            }

    # 提取高频技术（出现次数 >= 3）
    high_freq_techs = []
    for category, counter in tech_stats.items():
        for tech, count in counter.items():
            if count >= 3:
                high_freq_techs.append({
                    '技术': tech,
                    '类别': category,
                    '出现次数': count,
                    '占比': f"{count/total_jobs*100:.1f}%"
                })

    # 按出现次数排序
    high_freq_techs.sort(key=lambda x: x['出现次数'], reverse=True)
    report['高频技术'] = high_freq_techs[:20]  # 取前20个

    # 生成学习建议
    report['学习建议'] = generate_learning_recommendations(report['高频技术'])

    return report


def generate_learning_recommendations(high_freq_techs):
    """根据高频技术生成学习建议"""
    recommendations = []

    if not high_freq_techs:
        return ["暂无足够数据生成学习建议"]

    # 分类统计
    tech_by_category = {}
    for item in high_freq_techs:
        category = item['类别']
        if category not in tech_by_category:
            tech_by_category[category] = []
        tech_by_category[category].append(item)

    # 生成建议
    for category, techs in tech_by_category.items():
        tech_names = [t['技术'] for t in techs[:5]]  # 取前5个
        recommendations.append({
            '类别': category,
            '核心技术': tech_names,
            '重要性': '⭐⭐⭐⭐⭐' if len(techs) >= 5 else '⭐⭐⭐⭐',
            '建议': f"重点掌握 {', '.join(tech_names[:3])}"
        })

    return recommendations


def save_report(report, output_file):
    """保存分析报告"""
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n✓ 分析报告已保存到: {output_file}")


def print_summary(report):
    """打印摘要信息"""
    print("\n" + "="*70)
    print("技术栈分析报告")
    print("="*70)

    print(f"\n📊 数据统计")
    print(f"  分析职位数: {report['总职位数']}")

    print(f"\n🔥 高频技术 (Top 10)")
    for idx, tech in enumerate(report['高频技术'][:10], 1):
        print(f"  {idx}. {tech['技术']} ({tech['类别']}) - 出现 {tech['出现次数']} 次，占比 {tech['占比']}")

    print(f"\n💡 学习建议")
    for rec in report['学习建议'][:5]:
        print(f"  【{rec['类别']}】{rec['重要性']}")
        print(f"    核心技术: {', '.join(rec['核心技术'])}")
        print(f"    建议: {rec['建议']}")
        print()

    print("="*70)


# ==================== 主程序 ====================

def main():
    """主函数"""
    print("="*70)
    print("职位技术栈分析工具")
    print("="*70)

    # 1. 加载职位描述
    descriptions = load_job_descriptions(INPUT_FILE)

    if not descriptions:
        print("\n⚠ 没有找到有效的职位描述数据")
        print("请先运行爬虫采集数据: python boss_spider.py")
        return

    # 2. 提取技术栈
    tech_stats = extract_tech_stack(descriptions)

    # 3. 使用大模型深度分析（可选）
    llm_analysis = call_llm_analysis(descriptions, tech_stats)

    # 4. 生成分析报告
    report = generate_analysis_report(tech_stats, len(descriptions))

    # 5. 合并大模型分析结果
    if llm_analysis:
        report['大模型分析'] = llm_analysis

    # 6. 保存报告
    save_report(report, OUTPUT_FILE)

    # 7. 打印摘要
    print_summary(report)

    print("\n✓ 分析完成！")


if __name__ == '__main__':
    main()
