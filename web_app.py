import streamlit as st
import subprocess
import sys
from pathlib import Path

# 配置 Streamlit 页面
st.set_page_config(page_title="AI 趋势洞察 - last30days", page_icon="🕵️", layout="centered")

st.title("🕵️ 全网过去30天风向调研")
st.markdown("只需输入关键词，自动聚合 Hacker News、Reddit、TikTok、推特、Bluesky 社区一线前沿讨论资料，秒过百篇热帖！")

topic = st.text_input("请输入你想调研的话题（中英文皆可）：", placeholder="例如：Sora 竞品, AI video tools, Cursor alternatives...")

# 当用户点击按钮时触发后端代码
if st.button("开始调研挖掘 🚀", type="primary"):
    if not topic.strip():
        st.warning("⚠️ 请先输入你想调研的词哦~")
    else:
        st.info("数据获取与大模型总结中... (可能需要1-3分钟，后台正在跨国平台搜集几百篇帖子，请不要关闭离开手机屏幕)")
        
        # 建立一个 Spinner 等待状态
        with st.spinner("⏳ 正在运行..."):
            try:
                # 调用原始命令行
                # 这里我们在你的本地直接调起刚才的 python 脚本
                result = subprocess.run(
                    [sys.executable, "scripts/last30days.py", topic],
                    capture_output=True,
                    text=True,
                    encoding='utf-8' # 防止GBK报错
                )
                
                # 输出结果到页面上的日志控制台（可选阅读）
                with st.expander("展开查看底层抓取详细日志"):
                    st.text(result.stdout)
                
                # 获取报告文件路径
                # 项目默认将生成的 markdown 输出到 " ~/.local/share/last30days/out/report.md "
                output_file = Path.home() / ".local" / "share" / "last30days" / "out" / "report.md"
                
                if output_file.exists():
                    st.success("✅ 调研报告生成完毕！")
                    # 直接渲染 Markdown 内容
                    report_content = output_file.read_text(encoding="utf-8")
                    st.markdown("---")
                    st.markdown(report_content)
                else:
                    st.error("❌ 生成失败，未找到输出文件。")
                    st.text(result.stderr)
                    
            except Exception as e:
                st.error(f"发生错误: {e}")

st.markdown("---")
st.caption("Powered by [last30days-skill](https://github.com/mvanhorn/last30days-skill) | 本地服务器端运行中")
