import streamlit as st
import asyncio
import edge_tts
import io

# --- កំណត់ទំព័រ ---
st.set_page_config(page_title="Khmer Text-to-Speech", page_icon="🎙️")

st.markdown("""
    <style>
    .stTextArea textarea { font-size: 18px !important; line-height: 1.6; }
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #28a745; color: white; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- មុខងារបង្កើតសំឡេង ---
async def generate_full_audio(text, voice):
    communicate = edge_tts.Communicate(text, voice)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

# --- ចំណុចប្រទាក់អ្នកប្រើ (UI) ---
st.title("🎙️ កម្មវិធីអានអត្ថបទជាភាសាខ្មែរ")
st.title("ដែលបង្កើតឡើយដោយលោកពូប៉ាវ")
st.write("បញ្ចូលអត្ថបទរបស់អ្នកខាងក្រោម ដើម្បីបំប្លែងទៅជាសំឡេង MP3")

# ជ្រើសរើសសំឡេង
col1, col2 = st.columns([1, 1])
with col1:
    voice_choice = st.selectbox("ជ្រើសរើសសំឡេងអាន:", ["ស្រីមុំ (Sreymom)", "ពិសិដ្ឋ (Piseth)"])
    voice_id = "km-KH-SreymomNeural" if "ស្រីមុំ" in voice_choice else "km-KH-PisethNeural"

with col2:
    st.info(f"សំឡេងដែលកំពុងប្រើ: **{voice_choice}**")

# ប្រអប់បញ្ចូលអត្ថបទ
text_input = st.text_area("សរសេរ ឬ បិទភ្ជាប់អត្ថបទនៅទីនេះ:", height=300, placeholder="ឧទាហរណ៍៖ សួស្តី! តើអ្នកសុខសប្បាយជាទេ?")

if st.button("🔊 ចាប់ផ្តើមបំប្លែងជាសំឡេង"):
    if text_input.strip():
        with st.spinner("កំពុងបង្កើតសំឡេង សូមរង់ចាំ..."):
            try:
                # ហៅមុខងារ Async ដើម្បីបង្កើតសំឡេង
                audio_bytes = asyncio.run(generate_full_audio(text_input, voice_id))
                
                st.success("✅ ការបំប្លែងជោគជ័យ!")
                
                # បង្ហាញ Player សម្រាប់ស្តាប់
                st.audio(audio_bytes, format="audio/mp3")
                
                # ប៊ូតុងសម្រាប់ Download
                st.download_button(
                    label="📥 ទាញយកជាឯកសារ MP3",
                    data=audio_bytes,
                    file_name="khmer_audio.mp3",
                    mime="audio/mp3"
                )
            except Exception as e:
                st.error(f"មានបញ្ហាបច្ចេកទេស៖ {e}")
    else:
        st.warning("សូមបញ្ចូលអត្ថបទជាមុនសិន!")


