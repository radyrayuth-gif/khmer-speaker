import streamlit as st
import asyncio
import edge_tts
import re
import os
# រៀបចំទម្រង់វេបសាយ
st.set_page_config(page_title="Khmer AI SRT Reader", page_icon="🎬")
st.title("🎬 កម្មវិធីអានហ្វាយ SRT (ពិសិដ្ឋ & ស្រីមុំ)")
# មុខងារជំនួយសម្រាប់សម្អាតអត្ថបទ SRT
def clean_srt(content):
    # លុបលេខរៀង និងពេលវេលាចេញ ទុកតែអត្ថបទ
    lines = re.sub(r'\d+\n\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}', '', content)
    clean_lines = [line.strip() for line in lines.split('\n') if line.strip()]
    return " ".join(clean_lines)
# មុខងារបំប្លែងសំឡេង
async def process_tts(text, voice, output_file):
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(output_file)
# ជ្រើសរើសសំឡេង
voice_dict = {
    "ស្រីមុំ (Sreymom)": "km-KH-SreymomNeural",
    "ពិសិដ្ឋ (Piseth)": "km-KH-PisethNeural"
}
selected_label = st.selectbox("ជ្រើសរើសសំឡេងអាន:", list(voice_dict.keys()))
selected_voice = voice_dict[selected_label]
# កន្លែង Upload File SRT
uploaded_file = st.file_uploader("សូមដាក់ហ្វាយ .srt នៅទីនេះ", type=["srt"])
if uploaded_file is not None:
    # អានមាតិកាក្នុងហ្វាយ
    srt_content = uploaded_file.read().decode("utf-8")
    st.text_area("មាតិកាក្នុងហ្វាយ SRT:", srt_content, height=150)
    
    if st.button("ចាប់ផ្តើមបំប្លែងទៅជាសំឡេង"):
        # សម្អាតអត្ថបទឱ្យនៅតែអក្សរសុទ្ធ
        clean_text = clean_srt(srt_content)
        
        if clean_text:
            output_path = "srt_voice_output.mp3"
            with st.spinner('កំពុងបង្កើតសំឡេង... សូមរង់ចាំ'):
                asyncio.run(process_tts(clean_text, selected_voice, output_path))
                
                # បង្ហាញលទ្ធផល
                audio_file = open(output_path, "rb")
                st.audio(audio_file.read(), format="audio/mp3")
                st.success("ការបំប្លែងបានជោគជ័យ!")
                
                # ប៊ូតុងទាញយក
                with open(output_path, "rb") as file:
                    st.download_button(
                        label="ទាញយកហ្វាយសំឡេង (MP3)",
                        data=file,
                        file_name="khmer_ai_voice.mp3",
                        mime="audio/mp3"
                    )
        else:
            st.error("ហ្វាយ SRT របស់អ្នកមិនមានអត្ថបទសម្រាប់អានទេ។")
