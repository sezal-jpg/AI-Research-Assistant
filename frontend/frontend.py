import streamlit as st
import requests
import os
API_URL=os.getenv('API_URL',"http://127.0.0.1:8000")
st.title('🔬 AI Research Assistant')

# upload pdf to fastapi
uploaded_files=st.file_uploader('Upload PDFs',type='pdf',accept_multiple_files=True)
pdf_names=[]
if uploaded_files:
    pdf_names=[
        pdf.name for pdf in uploaded_files
    ]
    
# upload button
if uploaded_files:

    if st.button("Upload PDF"):

        try:

            files=[]
            for pdf in uploaded_files:
                 files.append(

        (
            "files",
            (
                pdf.name,
                pdf,
                "application/pdf"
            )
        )

    )    
    
            response = requests.post(
                f"{API_URL}/upload",
                files=files,
                timeout=120
            )
            st.write("status code:",response.status_code)
            st.write('response text:',response.text)

        except Exception as e:
            st.error(f" upload error:{e}")  
            
selected_pdf=st.selectbox('Search In',['All PDFs']+pdf_names)  
st.info(f"Selected: {selected_pdf}")  

    
# ask a question
question = st.text_input("Ask a question")

if st.button("Ask"):
    if not question:
        st.warning("Please enter a question.")
    else:
        response = requests.post(
            f"{API_URL}/ask",
            json={
                "question": question,
                "selected_pdf": selected_pdf
            }
        )
        if response.status_code == 200:
            result = response.json()
            st.subheader("🤖 Answer")
            st.write(result["answer"])

            st.success(
                f"Confidence: {result['confidence']}"
            )
            st.subheader("📃 Sources")
            for source in result["sources"]:
                st.write(
                    f"• {source['pdf']} (Page {source['page']})"
                )
            st.caption(
                f"Retrieved Chunks: {result['retrieved_chunks']}"
            )
        else:
            st.error(
                f"Backend Error ({response.status_code})"
            )
            try:
                st.json(response.json())
            except:
                st.text(response.text) 
         
