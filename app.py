import streamlit as st
import asyncio
import edge_tts
import re

st.set_page_config(page_title="Khmer SRT Sync Tool", page_icon="🎙️", layout="wide")

st.title("🎙️ Khmer SRT to Voice (Sync Mode)")
st.write("បំប្លែង SRT ទៅជាសំឡេង ពិសិដ្ឋ ឬ ស្រីមុំ")

# មុខងារបំបែកអត្ថបទ SRT
def parse_srt(content):
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\n$|$)', re.DOTALL)
    return pattern.findall(content)

async def get_voice_bytes(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            data += chunk["data"]
    return data

# UI ដូច Voicertool
col1, col2 = st.columns([2, 1])

with col1:
    srt_input = st.text_area("បិទភ្ជាប់អត្ថបទ SRT របស់អ្នក:", height=300, placeholder="1\n00:00:01,000 --> 00:00:04,000\nសួស្តីបងប្អូន។")

with col2:
    voice = st.selectbox("ជ្រើសរើសសំឡេង:", ["km-KH-SreymomNeural", "km-KH-PisethNeural"])
    if st.button("ចាប់ផ្តើមបំប្លែង", use_container_width=True):
        if srt_input:
            segments = parse_srt(srt_input)
            if segments:
                for idx, start, end, txt in segments:
                    with st.expander(f"ឃ្លាទី {idx} ({start} -> {end})"):
                        st.write(f"អត្ថបទ: {txt}")
                        audio_data = asyncio.run(get_voice_bytes(txt.replace('\n', ' '), voice))
                        st.audio(audio_data, format="audio/mp3")
                        st.download_button(f"ទាញយកឃ្លាទី {idx}", audio_data, f"part_{idx}.mp3", "audio/mp3")
                st.success("បំប្លែងរួចរាល់!")
            else:
                st.error("ទម្រង់ SRT មិនត្រឹមត្រូវ!")

