import streamlit as st
import requests
import os
import streamlit.components.v1 as components

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

st.markdown("""
<style>
.main-title {
    font-size: 42px;
    font-weight: 700;
    margin-bottom: 5px;
}
.subtitle {
    font-size: 18px;
    opacity: 0.7;
    margin-bottom: 25px;
}
.section-card {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-bottom: 20px;
}
.answer-box {
    padding: 20px;
    border-radius: 12px;
    border: 1px solid rgba(128,128,128,0.25);
    margin-top: 15px;
}
.source-box {
    padding: 12px;
    border-radius: 8px;
    border: 1px solid rgba(128,128,128,0.20);
    margin-bottom: 8px;
}

</style>
""", unsafe_allow_html=True)

components.html("""
<style>

body {
    margin: 0;
    padding: 0;
    background: transparent;
    overflow: hidden;
}

/* =========================================
   MAIN HEADER
   ========================================= */

.header {
    display: flex;
    align-items: center;
    gap: 12px;
    width: 100%;
    height: 145px;
    box-sizing: border-box;
}

/* =========================================
   LEFT LOGO SECTION
   ========================================= */

.logo-section {
    width: 130px;
    height: 150px;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;

    flex-shrink: 0;
    gap: 0;
}

/* =========================================
   SMALL OMNIRESEARCH ABOVE LOGO
   ========================================= */

.logo-top-title {
     font-family: Arial, sans-serif;
    font-size: 13px;
    font-weight: 800;
    line-height: 13px;
    white-space: nowrap;
    margin: 0 0 -3px 0;   /* closer to logo */
    padding: 0;
}

.logo-top-title .logo-omni {
    color: #f5f7ff;
}

.logo-top-title .logo-research {
    color: #2864e8;
}

/* =========================================
   LOGO
   ========================================= */

.logo {
    width: 90px;
    height: 90px;
    flex-shrink: 0;
}

/* =========================================
   ROTATING CIRCLE + BLUE POINTS
   ========================================= */

.logo-main {
    transform-box: fill-box;
    transform-origin: center;
    animation: rotateLogo 8s linear infinite;
}

/* =========================================
   ROTATING ELLIPSE
   ========================================= */

.logo-ellipse {
    transform-box: fill-box;
    transform-origin: center;
    animation: rotateEllipse 5s linear infinite;
}

/* =========================================
   SMALL ASSISTANT BELOW LOGO
   ========================================= */

.logo-bottom-title {
    font-family: Arial, sans-serif;
    font-size: 13px;
    font-weight: 800;
    line-height: 13px;
    white-space: nowrap;
    margin: -3px 0 0 0;   /* closer to logo */
    padding: 0;
    color: #8fa0b8;
}

/* =========================================
   LARGE STATIC TITLE
   ========================================= */

.static-title {
    font-family: Arial, sans-serif;
    font-size: 34px;
    font-weight: 800;
    line-height: 1;

    white-space: nowrap;
}

.static-title .omni {
    color: #f5f7ff;
}

.static-title .research {
    color: #2864e8;
}

.static-title .assistant {
    color: #8fa0b8;
}

/* =========================================
   ANIMATIONS
   ========================================= */

@keyframes rotateLogo {

    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }

}

@keyframes rotateEllipse {

    from {
        transform: rotate(0deg);
    }

    to {
        transform: rotate(360deg);
    }

}

</style>

<div class="header">

    <!-- ================================= -->
    <!-- LEFT: STATIC TEXT + ROTATING LOGO -->
    <!-- ================================= -->

    <div class="logo-section">

        <!-- STATIC OmniResearch -->

        <div class="logo-top-title">

            <span class="logo-omni">Omni</span><span class="logo-research">Research</span>

        </div>

        <!-- ================================= -->
        <!-- ROTATING LOGO -->
        <!-- ================================= -->

        <svg
            class="logo"
            viewBox="0 0 200 200"
            xmlns="http://www.w3.org/2000/svg"
        >

            <!-- ================================= -->
            <!-- ROTATING OUTER CIRCLE + POINTS -->
            <!-- ================================= -->

            <g class="logo-main">

                <!-- Outer circle -->

                <circle
                    cx="100"
                    cy="100"
                    r="78"
                    fill="none"
                    stroke="#202020"
                    stroke-width="7"
                    stroke-dasharray="8 6"
                />

                <!-- Top point -->

                <circle
                    cx="100"
                    cy="22"
                    r="7"
                    fill="#2864e8"
                />

                <!-- Left point -->

                <circle
                    cx="22"
                    cy="100"
                    r="7"
                    fill="#2864e8"
                />

                <!-- Right point -->

                <circle
                    cx="178"
                    cy="100"
                    r="7"
                    fill="#2864e8"
                />

                <!-- Bottom point -->

                <circle
                    cx="100"
                    cy="178"
                    r="7"
                    fill="#2864e8"
                />


            </g>

            <!-- ================================= -->
            <!-- FIXED AXES -->
            <!-- ================================= -->

            <line
                x1="22"
                y1="100"
                x2="178"
                y2="100"
                stroke="#555555"
                stroke-width="2"
            />

            <line
                x1="100"
                y1="22"
                x2="100"
                y2="178"
                stroke="#555555"
                stroke-width="2"
            />

            <!-- ================================= -->
            <!-- ROTATING ELLIPSE -->
            <!-- ================================= -->

            <g class="logo-ellipse">

                <ellipse
                    cx="100"
                    cy="100"
                    rx="78"
                    ry="30"
                    fill="none"
                    stroke="#8fa0b8"
                    stroke-width="2"
                />

            </g>

            <!-- ================================= -->
            <!-- CENTER STAR -->
            <!-- ================================= -->

            <polygon
                points="
                    100,65
                    108,88
                    133,88
                    113,102
                    121,128
                    100,113
                    79,128
                    87,102
                    67,88
                    92,88
                "
                fill="#2864e8"
            />

        </svg>


        <!-- STATIC Assistant -->

        <div class="logo-bottom-title">

            Assistant

        </div>

    </div>

    <!-- ================================= -->
    <!-- LARGE STATIC TITLE ON RIGHT -->
    <!-- ================================= -->

    <div class="static-title">

        <span class="omni">Omni</span><span class="research">Research</span><span class="assistant"> Assistant</span>

    </div>

</div>

""", height=160, scrolling=False)


st.markdown(
    '<div class="subtitle">'
    'Research across documents, websites and YouTube using an AI-powered agent.'
    '</div>',
    unsafe_allow_html=True)


# Session state
if 'website_urls' not in st.session_state:
    st.session_state.website_urls=[]
    
if 'youtube_sources' not in st.session_state:
    st.session_state['youtube_sources']=[]    
if 'uploaded_file_names' not in st.session_state:
    st.session_state.uploaded_file_names = []
if 'voice_question' not in st.session_state:
    st.session_state['voice_question']=""
if 'voice_active' not in st.session_state:
    st.session_state['voice_active'] =False       
    
# SOURCE INGESTION
st.subheader("📚 Add Research Sources")
file_tab, website_tab, youtube_tab = st.tabs(
    ["📁 Files", "🌐 Website", "▶️ YouTube"]
)

# FILE UPLOAD

with file_tab:
    st.subheader('Upload Files')
    
    uploaded_files = st.file_uploader(
        "Upload files",
        type=[
            # Documents
            "pdf",
            "docx",
            "pptx",
            "xlsx",
            "xls",
            "ods",
            "csv",
            "txt",
            "md",
            "markdown",
            "json",
            "html",
            "htm",
            "xml",

            # Images
            "png",
            "jpg",
            "jpeg",
            "bmp",
            "webp",

            # Audio
            "mp3",
            "wav",
            "m4a",
            "flac",
            "ogg",

            # Video
            "mp4",
            "avi",
            "mov",
            "mkv",
            "webm",
        ],
        accept_multiple_files=True
    )

    if uploaded_files:
        st.info(
            f"{len(uploaded_files)} file(s) selected")

        if st.button(
            "Upload Files",
            key="upload_files_button"
        ):

            try:
                files = []

                for file in uploaded_files:
                    file_bytes = file.getvalue()
                    files.append(
                        (
                            "files",
                            (
                                file.name,
                                file_bytes,
                                file.type
                            )
                        )
                    )

                with st.spinner(
                    "Processing and indexing files..."
                ):

                    response = requests.post(
                        f"{API_URL}/upload",
                        files=files,
                        timeout=600
                    )

                if response.status_code == 200:
                    st.success(
                        "Files uploaded and indexed successfully!"
                    )
                    for file in uploaded_files:
                      if file.name not in st.session_state.uploaded_file_names:
                         st.session_state.uploaded_file_names.append(file.name )    

                    try:
                       st.json(response.json())
                    except:
                        st.write(response.text)

                else:

                    st.error(
                        f"Upload failed "
                        f"({response.status_code})"
                    )

                    try:
                        st.json(response.json())

                    except:
                        st.text(response.text)

            except requests.exceptions.Timeout:
                st.error(
                    "Upload request timed out. "
                    "The backend did not finish "
                    "processing in time."
                )
            except Exception as e:
                st.error(
                    f"Upload error: {e}"
                )

# WEBSITE

with website_tab:

    st.subheader("Add Website")
    website_url = st.text_input(
        "Website URL",
        placeholder="https://example.com",
        key="website_url"
    )

    crawl_website = st.checkbox(
        "Research entire website"
    )
    max_pages = 10

    if crawl_website:
        max_pages = st.number_input(
            "Maximum pages to crawl",
            min_value=1,
            max_value=50,
            value=10
        )

    if st.button(
        "Add Website",
        key="add_website_button"
    ):

        if not website_url:
            st.warning(
                "Please enter a website URL."
            )

        else:

            try:

                with st.spinner( "Crawling and indexing website..." ):

                    response = requests.post(
                        f"{API_URL}/upload-website",
                        json={
                            "url": website_url,
                            "crawl": crawl_website,
                            "max_pages": max_pages
                        },
                        timeout=300
                    )

                if response.status_code == 200:
                    result = response.json()
                    st.success(
                        result.get(
                            "message",
                            "Website indexed successfully"
                        )
                    )

                    st.write(
                        f"📄 Documents: "
                        f"{result.get('documents', 0)}"
                    )

                    st.write(
                        f"🧩 Chunks: "
                        f"{result.get('chunks', 0)}"
                    )

                    if website_url not in st.session_state.website_urls:

                        st.session_state.website_urls.append(
                            website_url
                        )

                else:

                    st.error(
                        f"Website error "
                        f"({response.status_code})"
                    )

                    try:
                        st.json(response.json())
                    except:
                        st.text(response.text)

            except Exception as e:

                st.error(
                    f"Website upload error: {e}"
                )
# YOUTUBE

with youtube_tab:

    st.subheader("Add YouTube Source")
    
    st.info(
    "ℹ️ **Current YouTube limitation:** We currently index the video's "
    "transcript/spoken content. Text, images, slides, and other visual "
    "content in the video are not indexed yet. "
    "**Multimodal YouTube video analysis is coming soon.**"
)
    
    youtube_url = st.text_input(
        "YouTube URL",
        placeholder="https://www.youtube.com/watch?v=...",
        key="youtube_url"
    )

    if st.button(
        "Add YouTube",
        key="add_youtube_button"
    ):

        if not youtube_url:
            st.warning( "Please enter a YouTube URL.")

        else:

            try:
                with st.spinner(
                    "Processing youtube video..."
                ):
                    response=requests.post(f"{API_URL}/youtube/upload",
                        json={"url": youtube_url },timeout=300)
                   
                    if response.status_code == 200:
                     result = response.json()
                     
                     if result.get('documents',0)>0:
                        st.success(
                        result.get(
                            "message",
                            "YouTube indexed successfully") )

                        st.write(
                        f"📄 Documents: "
                        f"{result.get('documents', 0)}" )

                        st.write(
                        f"🧩 Chunks: "
                        f"{result.get('chunks', 0)}")

                        if (youtube_url not in st.session_state.youtube_sources):
                         st.session_state.youtube_sources.append( youtube_url )

                     else:
                      st.error(result.get('message','could not extract youtube transcript'))   
                      
                    else: 
                      st.error(
                        f"YouTube error "
                        f"({response.status_code})"
                    )

                      try:
                        st.json(response.json())
                        
                      except Exception:
                        st.text(response.text)

            except requests.exceptions.Timeout:

                st.error(
                   'youtube processing timed out.'
                )
            
            except Exception as e:
                st.error(f'Youtube uploaded error: {e}')    
             
# Research source
st.subheader("🔎 Research Source ")
source_options = ['All Files']

try:
    response=requests.get(f'{API_URL}/sources',timeout=10)
    if response.status_code==200:
        backend_sources=response.json().get('sources',[])
         
        for source in backend_sources:
            if source not in source_options:
                source_options.append(source)
except requests.exceptions.RequestException:
    pass

for source in st.session_state.uploaded_file_names:
    if source not in source_options:
        source_options.append(source)    
 
for source in st.session_state.website_urls:
    if source not in source_options:
        source_options.append(source) 
        
for source in st.session_state.youtube_sources:
    if source not in source_options:
        source_options.append(source)  
                    
selected_source=st.selectbox('Search Within ',source_options)
st.caption(f'📌 current source: {selected_source}')                


def clear_voice_question():
    st.session_state['voice_active']=False
    st.session_state['voice_question']=""

# ask a question
st.subheader("💭 Ask the Research Agent")
question=st.text_input('Your research question',
                       placeholder='Ask something about your selected source...',
                       key='question_input',
                       on_change=clear_voice_question)

ask_col,clear_col=st.columns([3,1])

with ask_col:
    ask_button=st.button("🔎 Ask Agent",use_container_width=True)
    
with clear_col:
    clear_button=st.button("🗑️ clear",use_container_width=True)   
    
if clear_button:
    st.session_state.voice_question = ""
    st.session_state.voice_active = False
    st.session_state.last_answer = ""
    st.rerun()   
  
if ask_button:
    typed_question=question.strip()
    voice_question = st.session_state.get(
    "voice_question",
    "").strip()
    
    if st.session_state.get('voice_active',False):
        final_question=voice_question
    else:
        final_question=typed_question    
    
    if not final_question:    
         st.warning("Please enter or record a question.")
    else:
      try:  
        with st.spinner('🧠 Agent is researching...'):
         response = requests.post(
            f"{API_URL}/agent/ask", params={"question": final_question, "selected_file": selected_source},timeout=300
        )
         
        if response.status_code == 200:
            
            result = response.json()
            answer=result.get('answer','No answer returned by the agent')
            st.session_state['last_answer']=answer
            
        else:
            st.error(f'Backend error'
                     f"({response.status_code})")
            try:
                st.json(response.json())
                
            except Exception:
                st.text(response.text) 
      
      except requests.exceptions.Timeout:
          st.error('The agent request timed out') 
           
      except Exception as e:
          st.error(f'Request error: {e}')
          
          # Agent response
          
if 'last_answer' in st.session_state:
    answer=st.session_state['last_answer']
    st.caption(f"🔎 Source: {selected_source}")
                         
    st.markdown(
    '<div class="answer-box">',
    unsafe_allow_html=True)
    st.write(answer)
            
    st.subheader('🔉 Listen to answer')
    if st.button("▶️ Generate Audio",use_container_width=True):
        try:

            with st.spinner("🔊 Generating audio..."):
                tts_response = requests.post(
                    f"{API_URL}/tts",
                    json={
                        "text": answer
                    },
                    timeout=120
                )

            if tts_response.status_code == 200:
                st.audio(
                    tts_response.content,
                    format="audio/wav")

            else:

                st.warning("Could not generate audio." )

        except requests.exceptions.Timeout:
            st.warning(
                "Audio generation timed out." )
        except Exception as e:

            st.warning(  f"TTS error: {e}")     
                
    st.markdown(
    '</div>',
    unsafe_allow_html=True)                     
                
# VOICE INPUT
st.subheader("🎙️ Voice Question")
audio_input = st.audio_input(
    "Record your question"
)

if audio_input:
    st.audio(audio_input)
    if st.button(
        "🎤 Transcribe Voice",
        use_container_width=True
    ):

        try:
            with st.spinner(
                "🎧 Transcribing your question..."
            ):

                files = {
                    "file": (
                        "voice_question.wav",
                        audio_input.getvalue(),
                        "audio/wav"
                    )
                }
                response = requests.post(
                    f"{API_URL}/transcribe",
                    files=files,
                    timeout=300
                )

            if response.status_code == 200:
                result = response.json()
                transcript = result.get(
                    "text",
                    ""
                ).strip()

                if transcript:
                    st.session_state[
                        "voice_question"
                    ] = transcript
                    st.session_state['voice_active']=True

                    st.success(
                        "Voice transcribed successfully." )
                    st.info(
                        f"📝 Transcript: {transcript}")

                else:

                    st.warning(
                        "No speech was detected."
                    )

            else:

                st.error(
                    f"Transcription error "
                    f"({response.status_code})"
                )

                try:
                    st.json(response.json())
                except Exception:
                    st.text(response.text)

        except requests.exceptions.Timeout:
            st.error(
                "Voice transcription timed out."
            )

        except Exception as e:
            st.error(
                f"Voice transcription error: {e}"
            )       