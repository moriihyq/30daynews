import streamlit as st
import subprocess
import sys
from pathlib import Path
import json
import time

# 当用户点击按钮时触发后端代码
st.set_page_config(page_title="AI 趋势中文洞察 - last30days", page_icon="🕵️", layout="centered")

st.title("🕵️ 全网海外风向洞察 (含高阶中文提炼总结)")
st.markdown("只需输入关键词 ➡️ 后台跨国抓取 HN/Reddit 热帖 ➡️ 直接调用 **Gemini 3.0** 进行数万字材料精华高度中文整理。")

st.info("💡 **系统升级**：采用了脱机后台计算架构！即使您的网络断开或锁屏退出浏览器，云端后台仍会自动抓取，重新进入本页面即可直接查看生成结果。")

STATUS_FILE = Path("task_status.json")

def load_status():
    if STATUS_FILE.exists():
        try:
            return json.loads(STATUS_FILE.read_text(encoding="utf-8"))
        except:
            return None
    return None

topic = st.text_input("请输入你想调研的话题（中英文皆可）：", placeholder="例如：Sora 竞品, AI video tools, Cursor alternatives...")

# 当用户点按钮的时候，不再阻塞 UI 进程，而是启动一个真正的系统后台子进程
if st.button("开始调研与深度总结 🚀", type="primary"):
    if not topic.strip():
        st.warning("⚠️ 请先输入你想调研的词哦~")
    else:
        # 写入初始态
        STATUS_FILE.write_text(json.dumps({"status": "fetching", "topic": topic}), encoding="utf-8")
        
        # 启动完全后台分离的神奇子进程 (脱离 WebSocket 生命周期)
        subprocess.Popen([sys.executable, "run_backend.py", topic], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        st.success("✅ 后台任务已成功提交云端服务器！")
        time.sleep(1)
        st.rerun()

status_data = load_status()

if status_data:
    current_status = status_data.get("status")
    current_topic = status_data.get("topic", "未知")
    
    if current_status == "fetching":
        st.warning(f"⏳ 后台正在跨平台拉取 【{current_topic}】 的数百篇外网资料... (可锁屏离开，爬虫在为您打工)")
        time.sleep(3)
        st.rerun()
        
    elif current_status == "summarizing":
        st.info(f"🧠 海外原文库抓取完毕，强大的 Gemini 3 大模型正在全中文深度阅读总结提炼中... (即将出炉)")
        time.sleep(3)
        st.rerun()
        
    elif current_status == "done":
        st.success(f"🎉 您的专属情报研报 【{current_topic}】 已生成完毕！")
        
        st.markdown("---")
        st.markdown(status_data.get("summary", ""))
        
        st.markdown("---")
        with st.expander("🕵️ 附：查看原始汇总的英文参考出处 (Raw Markdown Report)"):
            st.markdown(status_data.get("raw", ""))
            
        if st.button("清空并进行下一次调研 🔄"):
            STATUS_FILE.unlink()
            st.rerun()
            
    elif current_status == "error":
        st.error(f"❌ 发生错误：{status_data.get('message')}")
        if st.button("清除错误并重试 🔄"):
            STATUS_FILE.unlink()
            st.rerun()

