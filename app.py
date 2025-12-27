import streamlit as st
import asyncio
import edge_tts
import re
import io
from pydub import AudioSegment

st.set_page_config(page_title="Khmer SRT Sync", page_icon="⏱️")
st.title("🎬 បំប្លែង SRT ឱ្យត្រូវតាមម៉ោង (ពិសិដ្ឋ & ស្រីមុំ)")

def time_to_ms(time_str):
    h, m, s_ms = time_str.split(':')
    s, ms = s_ms.split(',')
    return (int(h) * 3600 + int(m) * 60 + int(s)) * 1000 + int(ms)

def parse_srt(content):
    pattern = re.compile(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\n$|$)', re.DOTALL)
    return pattern.findall(content)

async def get_voice(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            data += chunk["data"]
    return data

voice = st.radio("ជ្រើសរើសសំឡេង:", ["km-KH-SreymomNeural", "km-KH-PisethNeural"], horizontal=True)
srt_text = st.text_area("បិទភ្ជាប់អត្ថបទ SRT ទីនេះ:", height=250, placeholder="1\n00:00:01,000 --> 00:00:03,000\nសួស្តីបងប្អូនទាំងអស់គ្នា។")

if st.button("ចាប់ផ្តើមផលិតសំឡេង Sync តាមម៉ោង"):
    if srt_text:
        segments = parse_srt(srt_text)
        if segments:
            with st.spinner('កំពុងផលិត... សូមរង់ចាំបន្តិច'):
                # បង្កើតសំឡេងទទេប្រវែង 10 នាទីជាមូលដ្ឋាន (អាចកើនតាមជាក់ស្តែង)
                full_audio = AudioSegment.silent(duration=0)
                
                for _, start_str, end_str, text in segments:
                    start_ms = time_to_ms(start_str)
                    audio_data = asyncio.run(get_voice(text.replace('\n', ' '), voice))
                    seg = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
                    
                    # ពង្រីកសំឡេងមេ ប្រសិនបើខ្លីជាងម៉ោងក្នុង SRT
                    if len(full_audio) < start_ms:
                        full_audio += AudioSegment.silent(duration=start_ms - len(full_audio))
                    
                    full_audio = full_audio.overlay(seg, position=start_ms)

                out = io.BytesIO()
                full_audio.export(out, format="mp3")
                st.audio(out.getvalue(), format="audio/mp3")
                st.download_button("📥 ទាញយក MP3", out.getvalue(), "voice_sync.mp3", "audio/mp3")
        else:
            st.error("ទម្រង់ SRT មិនត្រឹមត្រូវ!")

