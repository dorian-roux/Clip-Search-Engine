import streamlit as st
import os

# -- Setup the Paths -- 
staticPath = os.path.join(os.path.dirname(__file__), 'src', 'static')
pathImages_logo = os.path.join(staticPath, 'images', 'iconCYTECH.png')

# -- Setup CONFIG Variables --
# for variable in ['PINECONE_KEY', 'PINECONE_ENV', 'PINECONE_INDEX_NAME', 'FIFTYONE_DATASET', 'FIFTYONE_DATASET_SPLIT', 'FIFTYONE_MODEL']:
#     # globals()[variable] = setupVariables(variable, exceptValue="")

# -- Setup STREAMLIT Page -- 
config_page_title, config_layout = 'CLIP - Search Engine', "wide"
st.set_page_config(page_title=config_page_title, page_icon=pathImages_logo, layout=config_layout)  # Set Page Configuration
st.title("CLIP - Search Engine - Text Requests to Images")
# hideStreamlitElements()  # --- Hide Streamlit Elements ---
# streamlitButton() # --- Change the Streamlit Button Style ---
import time

def main():
        
    if 'not_in' not in st.session_state:
        st.session_state.not_in = True
    placeholder = st.empty()


    if st.session_state.not_in:
        placeholder.empty()
        with placeholder.container():
            st.write("Hello World")
            but = st.button("Click me")
        
    if but:
        placeholder.empty()
        time.sleep(5)
        st.experimental_rerun()
        
main()
    
    