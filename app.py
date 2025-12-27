import streamlit as st
import asyncio
import edge_tts
import re
from pydub import AudioSegment
import io

st.set_page_config(page_title="Khmer AI Timed SRT", page_icon="⏱️")
st.title("⏱️ កម្មវិធីបំប្លែង SRT ឱ្យត្រូវតាមម៉ោង")

# មុខងារបំប្លែងម៉ោង SRT (00:00:01,000) ទៅជា មីលីវិនាទី (ms)
def time_to_ms(time_str):
    h, m, s = time_str.split(':')
    s, ms = s.split(',')
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)

# មុខងារទាញយកទិន្នន័យពី SRT
def parse_srt(content):
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\n$|$)', re.DOTALL)
    return pattern.findall(content)

async def generate_segment_audio(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

st.subheader("បញ្ចូលហ្វាយ SRT របស់អ្នក")
srt_input = st.text_area("បិទភ្ជាប់អត្ថបទ SRT ទីនេះ:", height=200)
voice_choice = st.selectbox("ជ្រើសរើសសំឡេង:", ["km-KH-SreymomNeural", "km-KH-PisethNeural"])

if st.button("ចាប់ផ្តើមផលិតសំឡេងតាមម៉ោង"):
    if srt_input:
        segments = parse_srt(srt_input)
        if not segments:
            st.error("ទម្រង់ SRT មិនត្រឹមត្រូវ!")
        else:
            with st.spinner('កំពុងបញ្ចូលសំឡេងតាមម៉ោង... សូមរង់ចាំ'):
                # បង្កើតសំឡេងទទេ (Silence) ជាមេ
                last_end_time = time_to_ms(segments[-1][2])
                combined_audio = AudioSegment.silent(duration=last_end_time + 1000)

                for index, start_str, end_str, text in segments:
                    start_ms = time_to_ms(start_str)
                    
                    # បង្កើតសំឡេង AI សម្រាប់ឃ្លានីមួយៗ
                    raw_audio = asyncio.run(generate_segment_audio(text.replace('\n', ' '), voice_choice))
                    seg_audio = AudioSegment.from_file(io.BytesIO(raw_audio), format="mp3")
                    
                    # បញ្ចូលសំឡេងទៅក្នុងម៉ោងដែលបានកំណត់
                    combined_audio = combined_audio.overlay(seg_audio, position=start_ms)

                # រក្សាទុកលទ្ធផល
                buffer = io.BytesIO()
                combined_audio.export(buffer, format="mp3")
                st.audio(buffer.getvalue(), format="audio/mp3")
                st.success("ការបញ្ចូលសំឡេងតាមម៉ោងបានជោគជ័យ!")
    else:
        st.error("សូមបញ្ចូលអត្ថបទ!")
