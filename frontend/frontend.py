import streamlit as st
import requests
import os

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
st.title("🌐 OmniResearch Assistant")

# Session state
if 'website_urls' not in st.session_state:
    st.session_state.website_urls=[]
    
if 'youtube_sources' not in st.session_state:
    st.session_state['youtube_sources']=[]    
    
# upload pdf to fastapi
st.subheader(" 📁 Upload Files")
uploaded_files = st.file_uploader("Upload files", type=[
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
    
    #Images
    "png",
    "jpg",
    "jpeg",
    "bmp",
    "webp",
    
    #Audio
    "mp3",
    "wav",
    "m4a",
    "flac",
    "ogg",
    
    #Video
    "mp4",
    "avi",
    "mov",
    "mkv",
    "webm",    ], accept_multiple_files=True)

uploaded_file_names = []

if uploaded_files:
    uploaded_file_names = [file.name for file in uploaded_files]

# upload button
if uploaded_files:

    if st.button("Upload Files"):

        try:

            files = []
            for file in uploaded_files:
                file_bytes=file.getvalue()
                files.append(("files", (file.name, file_bytes, file.type)))
                st.info(f'Uploading {len(uploaded_files)} file(s)...')
                response=requests.post(f'{API_URL}/upload',files=files,timeout=600)

        
                if response.status_code==200:
                    
                 st.success('files uploaded successfully!')
                 try:
                    st.json(response.json())
                 except:
                    st.write(response.text)
                else:
                    st.error(f'Upload Failed ({response.status_code})')
                        
                    try:
                     st.json(response.json())
                    except:
                     st.text(response.text)
                     
        except requests.exceptions.Timeout:
            st.error("Upload request timed out."
            'The backend did not finish processing in time.')  
                          
        except Exception as e:
            st.error(f'Upload error: {e}')
            
st.subheader("🌐 Add Website")

website_url = st.text_input(
    "Website URL",
    placeholder="https://example.com"
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

if st.button("Add Website"):

    if not website_url:
        st.warning("Please enter a website URL.")

    else:

        try:

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
                    f"Documents: {result.get('documents', 0)}"
                )

                st.write(
                    f"Chunks: {result.get('chunks', 0)}"
                )
                if website_url not in st.session_state.website_urls:
                    st.session_state.website_urls.append(website_url)
            else:

                st.error(
                    f"Website Error ({response.status_code})"
                )

                try:
                    st.json(response.json())
                except:
                    st.text(response.text)

        except Exception as e:

            st.error(
                f"Website upload error: {e}"
            )  
            
# Add YouTube        
st.subheader(' Add YouTube')
youtube_url=st.text_input('YouTube URL',placeholder='https://www.youtube.com/watch?v=...')   

if st.button('Add YouTube'):
    if not youtube_url:
        st.warning('please enter a Youtube url')
        
    else:
        try:
            response=requests.post(f'{API_URL}/youtube/upload',json={'url':youtube_url},timeout=300)   
            
            if response.status_code ==200:
            
                result=response.json()
                st.success(result.get('message','youtube indexed successfully'))       
                
                st.write(f'Documents:' f"{result.get('documents',0)}")
                st.write(f'chunks:'f"{result.get('chunks',0)}")
                
                if youtube_url not in st.session_state.youtube_sources:
                    st.session_state.youtube_sources.append(youtube_url)
                
            else:
                st.error(f'YouTube Error'
                         f'({response.status_code})')    
                       
                try:
                    st.json(response.json())       
                    
                except:
                    st.text(response.text) 
                    
        except Exception as e:
            st.error(f'YouTube upload error:{e}')               

#source selection
st.subheader("🔍🔎 Search IN")
source_options=[ 'All Files']

source_options.extend(uploaded_file_names)
source_options.extend(st.session_state.website_urls)

source_options.extend(st.session_state.youtube_sources)

selected_source=st.selectbox('Selected source',source_options)
st.info(f'Selected Source: {selected_source}')

# ask a question
question = st.text_input(
    "Ask a question",
    key="question_input"
)
  
  
if st.button("Ask"):
    typed_question=question.strip()
    voice_question = st.session_state.get(
    "voice_question",
    "")
    final_question=typed_question or voice_question
    
    if not final_question:
        final_question=st.session_state.get('voice_question',"").strip()
    if not final_question:    
         st.warning("Please enter or record a question.")
    else:
      try:  
        response = requests.post(
            f"{API_URL}/ask", json={"question": final_question, "selected_pdf": selected_source},timeout=300
        )
        if response.status_code == 200:
            
            result = response.json()
            
            st.subheader("🤖 Answer")
            
            st.write(result["answer"])
            
            st.subheader('🔉 Listen to answer')
            try:
                tts_response=requests.post(f'{API_URL}/tts',json={'text':result['answer']},timeout=120)
                
                if tts_response.status_code==200:
                    st.audio(tts_response.content,format='audio/wav')
                    
                else:
                    st.warning('could not generate audio')
                    
            except Exception as e:
                st.warning(f'TTS error: {e}')            

            st.success(f"Confidence: {result['confidence']}")
            st.subheader("📃 Sources")
            for source in result["sources"]:
                if source['type']=='file':
                 st.write(f"• {source['pdf']} (Page {source['page']})")
                elif source['type']=='website': 
                    st.write(f" {source['url']}")
                    
            st.caption(f"Retrieved Chunks: {result['retrieved_chunks']}")
        else:
            st.error(f"Backend Error ({response.status_code})")
            try:
                st.json(response.json())
            except:
                st.text(response.text)
      except Exception as e:
          st.error(f'Request error: {e}')

audio_input=st.audio_input('🎙️ record your question')
if audio_input:
    st.audio(audio_input)
    
    if st.button('Transcribe Voice'):
     try:
        files={"file":('voice_question.wav',audio_input.getvalue(),"audio/wav")}
        
        response=requests.post(f'{API_URL}/transcribe',files=files,timeout=300)
        
        if response.status_code ==200:
            result=response.json()
            
            st.session_state['voice_question']=result['text']
            st.success('Voice transcribed successfully')
            st.write('Transcript:',result['text'])
            
        else:
            st.error(f'Transcription error'f"({response.status_code})") 
            
     except Exception as e:
        st.error(f'Voice transcription error: {e}')        