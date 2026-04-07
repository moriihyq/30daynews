import sys
import json
import subprocess
from pathlib import Path
import requests

GEMINI_API_KEY = "AIzaSyCYqV0y-RuzJOwqRbP6EZVaq8fgUmlaX_Y"
GEMINI_MODEL = "gemini-3-flash-preview"

def get_chinese_summary(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    prompt = f"""你是一名资深的海外前沿科技与创投情报分析师。
我将给你一份根据特定关键词在过去30天内爬取自 HackerNews、Reddit、推特 等海外高价值社区的原始调研材料（全英文）。
请你帮我进行深度的【中文提炼与总结】，必须保证纯中文输出（专有名词保留即可）。请务必使用以下清晰的 Markdown 结构：
# 🎯 宏观趋势与行业洞察
# 🛠️ 高赞工具/项目提及榜单
# 💬 社区主流情绪与争议点
--- 
📝 以下为爬取到的外网调研生骨肉数据：
{text}
"""
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=data)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"API 请求出现问题: {str(e)}"

def main():
    if len(sys.argv) < 2:
        return
    topic = sys.argv[1]
    status_file = Path("task_status.json")
    report_file = Path.home() / ".local" / "share" / "last30days" / "out" / "report.md"
    
    try:
        # 1. 运行爬虫
        subprocess.run([sys.executable, "scripts/last30days.py", topic], capture_output=True, text=True, encoding='utf-8')
        
        # 2. 检查输出
        if report_file.exists():
            raw_text = report_file.read_text(encoding="utf-8")
            status_file.write_text(json.dumps({"status": "summarizing", "topic": topic}), encoding="utf-8")
            
            # 3. 运行大模型总结
            summary = get_chinese_summary(raw_text)
            
            # 4. 保存最终结果
            status_file.write_text(json.dumps({
                "status": "done",
                "topic": topic,
                "summary": summary,
                "raw": raw_text
            }), encoding="utf-8")
        else:
            status_file.write_text(json.dumps({"status": "error", "message": "爬虫未生成结果文件"}), encoding="utf-8")
            
    except Exception as e:
        status_file.write_text(json.dumps({"status": "error", "message": str(e)}), encoding="utf-8")

if __name__ == "__main__":
    main()