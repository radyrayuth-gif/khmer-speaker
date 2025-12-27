import streamlit as st
import asyncio
import edge_tts
import re
import io
# រៀបចំទម្រង់វេបសាយឱ្យស្អាត
st.set_page_config(page_title="SRT to Speech - Khmer AI", layout="wide")
st.title("🎙️ Khmer SRT to Speech Converter")
st.write("បំប្លែងហ្វាយ Subtitle (SRT) ទៅជាសំឡេង MP3 ដោយប្រើសំឡេង ពិសិដ្ឋ និង ស្រីមុំ")
# មុខងារសម្អាតអត្ថបទ SRT (ដកលេខរៀង និងពេលវេលាចេញ)
def parse_srt(srt_content):
    lines = srt_content.split('\n')
    text_only = []
    for line in lines:
        if not re.match(r'(\d+)|(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})', line.strip()) and line.strip():
            text_only.append(line.strip())
    return " ".join(text_only)
# បង្កើត Columns សម្រាប់ UI
col1, col2 = st.columns([2, 1])
with col1:
    st.subheader("បញ្ចូលអត្ថបទ SRT")
    srt_input = st.text_area("បិទភ្ជាប់ (Paste) អត្ថបទ SRT នៅទីនេះ:", height=300, placeholder="1\n00:00:00,300 --> 00:00:01,050\nសួស្តីថ្ងៃថ្មី។")
    
    uploaded_file = st.file_uploader("ឬ Upload ហ្វាយ .srt", type=["srt"])
    if uploaded_file is not None:
        srt_input = uploaded_file.read().decode("utf-8")
with col2:
    st.subheader("កំណត់សំឡេង")
    voice_choice = st.radio("ជ្រើសរើសអ្នកនិយាយ:", ["ស្រីមុំ (Sreymom)", "ពិសិដ្ឋ (Piseth)"])
    voice_id = "km-KH-SreymomNeural" if "ស្រីមុំ" in voice_choice else "km-KH-PisethNeural"
    
    speed = st.slider("ល្បឿននិយាយ:", 0.5, 1.5, 1.0)
    rate = f"{'+' if speed >= 1 else '-'}{int(abs(speed-1)*100)}%"
    if st.button("បំប្លែងទៅជាសំឡេង", use_container_width=True):
        if srt_input:
            clean_text = parse_srt(srt_input)
            
            async def generate():
                communicate = edge_tts.Communicate(clean_text, voice_id, rate=rate)
                audio_data = b""
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_data += chunk["data"]
                return audio_data
            with st.spinner('កំពុងដំណើរការ...'):
                audio_bytes = asyncio.run(generate())
                st.audio(audio_bytes, format="audio/mp3")
                
                # ប៊ូតុងទាញយក
                st.download_button(
                    label="📥 ទាញយកហ្វាយ MP3",
                    data=audio_bytes,
                    file_name="khmer_voice.mp3",
                    mime="audio/mp3",
                    use_container_width=True
                )
        else:
            st.error("សូមបញ្ចូលអត្ថបទ SRT ជាមុនសិន!")
