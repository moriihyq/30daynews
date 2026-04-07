import streamlit as st
import subprocess
import sys
from pathlib import Path
import requests

# 当用户点击按钮时触发后端代码
# Gemini API 配置
GEMINI_API_KEY = "AIzaSyCYqV0y-RuzJOwqRbP6EZVaq8fgUmlaX_Y"
GEMINI_MODEL = "gemini-3-flash-preview"

st.set_page_config(page_title="AI 趋势中文洞察 - last30days", page_icon="🕵️", layout="centered")

def get_chinese_summary(text):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    
    prompt = f"""你是一名资深的海外前沿科技与创投情报分析师。
我将给你一份根据特定关键词在过去30天内爬取自 HackerNews、Reddit、推特 等海外高价值社区的原始调研材料（全英文）。

请你帮我进行深度的【中文提炼与总结】，必须保证纯中文输出（专有名词保留即可），帮助我不用看原始英文也能光速掌握全网风向脉络。请务必使用以下清晰的 Markdown 结构：

# 🎯 宏观趋势与行业洞察
（一针见血总结这份数据反映出的最重要 3 个风向或目前最大的行业痛点）

# 🛠️ 高赞工具/项目提及榜单
（提取帖子和评论中被网友反复推荐或高赞具体的 工具/项目/产品名称。对每一个注明网友为什么推荐它，或是它被痛骂的核心理由）

# 💬 社区主流情绪与争议点
（网友们具体在讨论什么？争论什么？列举1-2个令人深省的优质评论或观点剖析）

--- 
📝 以下为爬取到的外网调研生骨肉数据：
{text}
"""
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(url, headers={'Content-Type': 'application/json'}, json=data)
        response.raise_for_status()
        return response.json()['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        error_msg = f"API 结构发生错误: {str(e)}"
        return error_msg

st.title("🕵️ 全网海外风向洞察 (含高阶中文提炼总结)")
st.markdown("只需输入关键词 ➡️ 后台跨国抓取 HN/Reddit 热帖 ➡️ 直接调用 **Gemini 3.0** 进行数万字材料精华高度中文整理。")

topic = st.text_input("请输入你想调研的话题（中英文皆可）：", placeholder="例如：Sora 竞品, AI video tools, Cursor alternatives...")

# 当用户点击按钮时触发后端代码
if st.button("开始调研与深度总结 🚀", type="primary"):
    if not topic.strip():
        st.warning("⚠️ 请先输入你想调研的词哦~")
    else:
        st.info("步骤 1/2：正在海外各大技术社区拉取近30天数百篇新鲜数据... (这需要大约1.5-3分钟的时间，随时为您播报后台进度)")
        
        # 建立一个 Spinner 等待状态
        with st.spinner("⏳ 底层爬虫跨平台抓取、打分与去重清洗中..."):
            try:
                # 建立一个日志容器，实时滚动流式输出，防止 WebSocket 断连导致手机掉线
                log_expander = st.expander("🕵️ 展开查看后台爬虫实时进度 (防止锁屏掉线)", expanded=True)
                log_container = log_expander.empty()
                logs = ""
                
                # 使用 Popen 实时流式读取 stdout
                process = subprocess.Popen(
                    [sys.executable, "scripts/last30days.py", topic],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    bufsize=1 # Line buffered
                )
                
                # 实时刷新防止手机端 WebSocket 超时断开连接
                for line in iter(process.stdout.readline, ''):
                    logs += line
                    # 只保留最后两千个字符以免造成手机卡顿
                    log_container.text(logs[-2000:])
                
                process.stdout.close()
                process.wait()
                
                log_expander.update(expanded=False)
                
                output_file = Path.home() / ".local" / "share" / "last30days" / "out" / "report.md"
                
                if output_file.exists():
                    report_content = output_file.read_text(encoding="utf-8")
                    
                    st.success("✅ 步骤一完成！数据抓取与去重完毕，立刻提交大模型进行重构...")
                    
                    st.info("步骤 2/2：正在调用强大的 Gemini-3-Flash 进行大流量语义解析与纯中文高维总结提炼...")
                    
                    with st.spinner("🧠 大模型阅读成千上万字的高价值跟帖中..."):
                        chinese_summary = get_chinese_summary(report_content)
                        
                        st.markdown("---")
                        st.markdown(chinese_summary)
                        
                        st.markdown("---")
                        with st.expander("🕵️ 附：查看原始汇总的英文参考出处 (Raw Markdown Report)"):
                            st.markdown(report_content)
                else:
                    st.error("❌ 生成失败，未找到输出文件。")
                    st.text(result.stderr)
                    
            except Exception as e:
                st.error(f"发生系统错误: {e}")

st.markdown("---")
st.caption("Powered by [last30days-skill](https://github.com/mvanhorn/last30days-skill) + **Gemini-3-Flash** | 全面中文增强出炉")
