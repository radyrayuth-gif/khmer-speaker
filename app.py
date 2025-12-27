import streamlit as st
import asyncio
import edge_tts
import re

st.set_page_config(page_title="Khmer SRT to Speech", page_icon="🎙️")

# រចនាស្ទីលឱ្យដូចវេបសាយអាជីព
st.markdown("""
    <style>
    .stTextArea textarea { font-size: 16px !important; }
    .stButton>button { background-color: #007bff; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🎙️ Khmer SRT Voice Generator")
st.write("បំប្លែង SRT ទៅជាសំឡេង ពិសិដ្ឋ និង ស្រីមុំ")

# មុខងារបំបែកអត្ថបទ SRT
def parse_srt(content):
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\n$|$)', re.DOTALL)
    return pattern.findall(content)

async def generate_voice(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            data += chunk["data"]
    return data

# ចំណុចជ្រើសរើសសំឡេង
voice_option = st.radio("ជ្រើសរើសសំឡេងអាន:", ["ស្រីមុំ (Sreymom)", "ពិសិដ្ឋ (Piseth)"], horizontal=True)
voice_id = "km-KH-SreymomNeural" if "ស្រីមុំ" in voice_option else "km-KH-PisethNeural"

srt_input = st.text_area("បិទភ្ជាប់អត្ថបទ SRT របស់អ្នកនៅទីនេះ:", height=300)

if st.button("ចាប់ផ្តើមបំប្លែង"):
    if srt_input:
        segments = parse_srt(srt_input)
        if segments:
            st.success(f"រកឃើញចំនួន {len(segments)} ឃ្លា")
            for idx, start, end, txt in segments:
                with st.expander(f"ឃ្លាទី {idx} [{start} -> {end}]"):
                    st.write(f"អត្ថបទ: {txt}")
                    # បង្កើតសំឡេងសម្រាប់ឃ្លានីមួយៗ
                    audio_bytes = asyncio.run(generate_voice(txt.replace('\n', ' '), voice_id))
                    st.audio(audio_bytes, format="audio/mp3")
                    st.download_button(f"ទាញយក MP3 (ឃ្លាទី {idx})", audio_bytes, f"segment_{idx}.mp3", "audio/mp3")
        else:
            st.error("ទម្រង់ SRT មិនត្រឹមត្រូវ! សូមពិនិត្យមើលម៉ោង និងលេខរៀងឡើងវិញ។")
    else:
        st.warning("សូមបញ្ចូលអត្ថបទ SRT ជាមុនសិន។")

