import streamlit as st
import asyncio
import edge_tts
import re
import io

# --- Page Configuration ---
st.set_page_config(page_title="Khmer SRT to Speech", page_icon="🎙️")

st.markdown("""
    <style>
    .stTextArea textarea { font-size: 16px !important; }
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #007bff; color: white; }
    </style>
    """, unsafe_allow_html=True)

## --- Logic Functions ---

def parse_srt(content):
    # Improved regex to handle various SRT line breaks and spacing
    pattern = re.compile(r'(\d+)\s*\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\s*\n(.*?)(?=\n\n|\n\d+\n|$)', re.DOTALL)
    return pattern.findall(content)

async def process_segments(segments, voice_id):
    combined_audio = io.BytesIO()
    segment_data = []
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i, (idx, start, end, txt) in enumerate(segments):
        clean_text = txt.replace('\n', ' ').strip()
        status_text.text(f"កំពុងដំណើរការឃ្លាទី {idx}...")
        
        communicate = edge_tts.Communicate(clean_text, voice_id)
        audio_chunk = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_chunk += chunk["data"]
        
        segment_data.append({"idx": idx, "audio": audio_chunk, "text": clean_text})
        combined_audio.write(audio_chunk)
        
        # Update progress
        progress_bar.progress((i + 1) / len(segments))
    
    status_text.text("ការបំប្លែងត្រូវបានបញ្ចប់!")
    return segment_data, combined_audio.getvalue()

## --- UI Layout ---

st.title("🎙️ Khmer SRT Voice Generator")
st.info("បំប្លែងឯកសារ SRT របស់អ្នកទៅជាសំឡេងអានដោយស្វ័យប្រវត្តិ")

col1, col2 = st.columns([2, 1])

with col2:
    st.subheader("កំណត់សំឡេង")
    voice_option = st.radio("ជ្រើសរើសសំឡេង:", ["ស្រីមុំ (Sreymom)", "ពិសិដ្ឋ (Piseth)"])
    voice_id = "km-KH-SreymomNeural" if "ស្រីមុំ" in voice_option else "km-KH-PisethNeural"

with col1:
    srt_input = st.text_area("បិទភ្ជាប់អត្ថបទ SRT នៅទីនេះ:", height=300, placeholder="1\n00:00:01,000 --> 00:00:04,000\nសួស្តីបងប្អូនទាំងអស់គ្នា...")

if st.button("🚀 ចាប់ផ្តើមបំប្លែង"):
    if srt_input.strip():
        segments = parse_srt(srt_input)
        if segments:
            st.success(f"រកឃើញចំនួន {len(segments)} ឃ្លា")
            
            # Run the async processing
            all_segments, full_audio = asyncio.run(process_segments(segments, voice_id))
            
            # Master Download
            st.divider()
            st.subheader("📁 ទាញយកលទ្ធផលរួម")
            st.audio(full_audio, format="audio/mp3")
            st.download_button("ទាញយក File រួម (MP3)", full_audio, "full_audio.mp3", "audio/mp3")
            
            # Individual Segments
            with st.expander("មើលលម្អិតតាមឃ្លានីមួយៗ"):
                for item in all_segments:
                    st.write(f"ឃ្លាទី {item['idx']}: {item['text']}")
                    st.audio(item['audio'], format="audio/mp3")
        else:
            st.error("ទម្រង់ SRT មិនត្រឹមត្រូវ! សូមពិនិត្យមើលទ្រង់ទ្រាយពេលវេលា (00:00:00,000)")
    else:
        st.warning("សូមបញ្ចូលអត្ថបទ SRT ជាមុនសិន។")

