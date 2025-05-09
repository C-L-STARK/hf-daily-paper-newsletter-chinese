import os
import json
from datetime import datetime
import markdown
from jinja2 import Template
from utils import get_logger
import re

logger = get_logger()

class NewsletterGenerator:
    def __init__(self):
        self.template = """
# <img src="https://huggingface.co/datasets/huggingface/brand-assets/resolve/main/hf-logo.png" width="30"/> Hugging Face {{ date }} 论文日报

## 📊 今日论文统计
- 总论文数：{{ total_papers }}
- 热门领域：{{ hot_topics }}

## 📝 论文详情

{% for paper in papers %}
### {{ loop.index }}. {{ paper.title }}

**原文标题：** {{ paper.original_title }}

**摘要：**
{{ paper.summary }}

**论文链接：** [HuggingFace]({{ paper.paper_url }}) | [arXiv]({{ paper.arxiv_url }})

{% if paper.code_url %}
**代码链接：** [GitHub]({{ paper.code_url }})
{% endif %}

---
{% endfor %}

## 🔍 关键词云图
![关键词云图]({{ wordcloud_path }})

## 📈 近期论文趋势
![论文趋势]({{ trend_path }})

## 🎙️ 语音播报
- [收听今日论文解读]({{ audio_path }})

## 📱 订阅渠道
- GitHub: [hf-daily-paper-newsletter-chinese](https://github.com/2404589803/hf-daily-paper-newsletter-chinese)
"""

    def extract_paper_info(self, paper_data):
        """从论文数据中提取关键信息"""
        translation = paper_data.get('translation', '')
        
        # 使用更严格的正则表达式提取标题和摘要
        title_match = re.search(r"标题[:：]\s*([^\n]+)(?=\s*\n\s*摘要[:：]|\Z)", translation, re.DOTALL)
        summary_match = re.search(r"摘要[:：]\s*([^\n].+?)(?=\s*(?:\n\s*[^：\n]+[:：]|\Z))", translation, re.DOTALL)
        
        # 如果匹配失败，尝试使用备用模式
        if not title_match:
            title_match = re.search(r"^([^\n]+)\n\s*摘要[:：]", translation, re.MULTILINE)
        
        title = (title_match.group(1) if title_match else paper_data.get('title', '')).strip()
        summary = (summary_match.group(1) if summary_match else '').strip()
        
        # 如果摘要为空，尝试获取剩余的所有文本作为摘要
        if not summary and '摘要：' in translation:
            summary = translation.split('摘要：', 1)[1].strip()
        
        return {
            'title': title,
            'original_title': paper_data.get('title', ''),
            'summary': summary,
            'paper_url': paper_data.get('url', ''),
            'arxiv_url': paper_data.get('arxiv_url', ''),
            'code_url': paper_data.get('paper', {}).get('code', '')
        }

    def get_hot_topics(self, papers):
        """分析热门研究领域"""
        topics = []
        keywords = ['LLM', 'Vision', 'Audio', 'MultiModal', 'NLP', 'RL', 
                   'Transformer', 'GPT', 'AIGC', 'Diffusion']
        for paper in papers:
            title = paper.get('title', '').lower()
            summary = paper.get('summary', '').lower()
            content = title + ' ' + summary
            for keyword in keywords:
                if keyword.lower() in content and keyword not in topics:
                    topics.append(keyword)
        return ', '.join(topics) if topics else '综合领域'

    def generate_newsletter(self, date_str=None):
        """生成每日论文简报"""
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')
            
        try:
            # 读取论文数据
            json_file = os.path.join('HF-day-paper-deepseek', f"{date_str}_HF_deepseek_clean.json")
            if not os.path.exists(json_file):
                logger.error(f"未找到{date_str}的论文数据文件")
                return False
                
            with open(json_file, 'r', encoding='utf-8') as f:
                papers_data = json.load(f)
                
            # 检查是否有有效数据
            if not isinstance(papers_data, list) or len(papers_data) == 0:
                logger.info(f"{date_str} 没有论文数据，跳过生成日报")
                return False
                
            # 处理论文信息
            papers = [self.extract_paper_info(paper) for paper in papers_data]
            if not papers:
                logger.warning("没有提取到有效的论文信息")
                return False
                
            # 检查是否存在统计数据
            stats_file = os.path.join('stats', 'stats_report.json')
            if not os.path.exists(stats_file):
                logger.warning("未找到统计数据文件，将使用简化版模板")
                template_data = {
                    'date': date_str,
                    'total_papers': len(papers),
                    'hot_topics': self.get_hot_topics(papers),
                    'papers': papers,
                    'wordcloud_path': None,
                    'trend_path': None,
                    'audio_path': f'audio/{date_str}_daily_papers.mp3'
                }
            else:
                # 准备模板数据
                template_data = {
                    'date': date_str,
                    'total_papers': len(papers),
                    'hot_topics': self.get_hot_topics(papers),
                    'papers': papers,
                    'wordcloud_path': f'images/keywords_wordcloud.png',
                    'trend_path': f'images/daily_papers.png',
                    'audio_path': f'audio/{date_str}_daily_papers.mp3'
                }
            
            # 渲染模板
            template = Template(self.template)
            newsletter_md = template.render(**template_data)
            
            # 转换为HTML
            newsletter_html = markdown.markdown(newsletter_md)
            
            # 保存文件
            output_dir = 'newsletters'  # 日报保存在 newsletters 目录
            os.makedirs(output_dir, exist_ok=True)
            
            # 保存Markdown版本
            md_path = os.path.join(output_dir, f"{date_str}_daily_paper.md")
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(newsletter_md)
                
            # 保存HTML版本
            html_path = os.path.join(output_dir, f"{date_str}_daily_paper.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(newsletter_html)
                
            logger.info(f"日报已生成：{md_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成日报时出错：{str(e)}")
            return False

if __name__ == "__main__":
    generator = NewsletterGenerator()
    generator.generate_newsletter() 