##############################
# CLIP - SEARCH ENGINE - APP #
##############################


# - IMPORTS -

# -- Add "src" folder to the system Paths --
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# -- General Libraries --
import requests
import re 
import time
import streamlit as st
from PIL import Image

# -- Custom Variables and Functions --
from utils import stylizeStreamlitElements, automaticalyValidate, setupConfigP1, setupConfigP2
from fiftyone_datasets_models import constructDictInf, getZoo_datasets, getZoo_models, loadZoo_dataset, loadZoo_model
from pinecone_manipulation import upsert_Data, queryPinecone
from embedding import get_text_embedding


# -- FUNCTION --

# -- Ensure the existence of any variables --
def setupVariables(nameVariable, exceptValue=None):
    """Define a variable if it does not exist.
    Args:
        nameVariable (str): variable name turned into a string.
        exceptValue (_type_, optional): value to output when exception. Defaults to None.
    """    
    if nameVariable in globals():
        return globals()[nameVariable]
    return exceptValue

# -- Variables --


# - MAIN - 
def main():
    
    # -- STEP 1 - Initial the Interface + Variables --
    
    # --- Setup the Paths ---
    configPath = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
    staticPath = os.path.join(os.path.dirname(__file__), 'src', 'static')
    pathImages_logo = os.path.join(staticPath, 'images', 'iconRelease.png')
    
    # --- Setup CONFIG Variables ---
    for variable in ['PINECONE_KEY', 'PINECONE_ENV', 'PINECONE_INDEX_NAME', 'FIFTYONE_DATASET', 'FIFTYONE_DATASET_SPLIT', 'FIFTYONE_MODEL', 'DISABLE_CONFIG_BUTTONS']:
        expVal = ""
        if os.path.exists(configPath):
            if variable in st.secrets.keys():
                expVal = st.secrets[variable]
        globals()[variable] = setupVariables(variable, exceptValue=expVal)
    
    # --- Setup STREAMLIT Page --- 
    config_page_title, config_layout = 'CLIP - Search Engine', "wide"
    st.set_page_config(page_title=config_page_title, page_icon=pathImages_logo, layout=config_layout)  # Set Page Configuration
    st.markdown("<h1 style='text-align: center; color: black;'>CLIP - Search Engine - Text Requests to Images</h1>", unsafe_allow_html=True)
    stylizeStreamlitElements() # ---- Hide Streamlit Elements + Change the Streamlit Button Style ----

    # --- Setup the STREAMLIT Session State --- 
    if 'CONFIG' not in st.session_state:
        st.session_state['CONFIG'] = dict({
            'DISABLE_CONFIG_BUTTONS': False if not DISABLE_CONFIG_BUTTONS else DISABLE_CONFIG_BUTTONS,
            'INFORMATION': '',
            'STARTUP_VERIF': False,
            'VALIDATION': False,
            'LFDMIP': False,
            'CLIP_MODEL': None,
            'PHASE_1': dict({'VALIDATION': False, 'WARNING': False}),
            'PHASE_2': dict({'VALIDATION': False, 'WARNING': False}),
        })
    if 'PINECONE' not in st.session_state:
        st.session_state['PINECONE'] = dict({
            'DEFAULT': { 'DIMENSION': 512, 'METRIC': 'cosine', 'POD_TYPE': 'P1 - Faster Queries'},
            'METRICS': ['cosine', 'dotproduct', 'euclidean'],
            'POD_TYPES': ['S1 - Best Storage Capacity', 'P1 - Faster Queries', 'P2 - Lowest Latency and Highest Throughput'],
            'INDEX' : {'BUILD': False},
            'USER': dict({
                'KEY': dict({'VALUE': PINECONE_KEY, 'ENVIRONMENT': PINECONE_ENV}),
                'INDEX_NAME': PINECONE_INDEX_NAME, 'INDEX': None,
            }),
        })
    if 'FIFTYONE' not in st.session_state:
        st.session_state['FIFTYONE'] = dict({
            'DEFAULT': { 'DATASET': 'coco-2017', 'DATASET_SPLIT': '', 'MODEL': 'clip-vit-base32-torch'},
            'DATASETS': getZoo_datasets(),
            'SPLITS': ['train', 'test', 'validation'],
            'MODELS': getZoo_models(),
            'USER': dict({
                'DATASET': FIFTYONE_DATASET,
                'SPLIT': FIFTYONE_DATASET_SPLIT,
                'MODEL': FIFTYONE_MODEL
            }),
        
        })
    if 'LOAD' not in st.session_state:
        st.session_state['LOAD'] = dict({'DATASET': None, 'MODEL': None, 'DICT_DATASET': None})
    if 'QUERY' not in st.session_state:
        st.session_state['QUERY'] = dict({'VALIDATE':False, 'STRING':'', 'NUMBER':10}) 
        
    # --- Setup the STREAMLIT Area ---
    areaSpinning = st.empty()
    areaPlaceholder = st.empty()

    # -- STEP 2 - VERIFY THE PARAMETERS | LAUNCH VERIFICATION -- 
    if not st.session_state['CONFIG']['STARTUP_VERIF']:
        st.session_state['CONFIG']['STARTUP_VERIF'] = True
        with areaSpinning.container():
            with st.spinner('STARTUP VERIFICATION - Analysis of the Existing Configuration in Progress...'):
                if automaticalyValidate():
                    time.sleep(1)
                    st.experimental_rerun()
    
    
    # -- STEP 3 - VERIFY THE PARAMETERS | FOLLOWING VERIFICATION -- 
    if not st.session_state['CONFIG']['VALIDATION']:    
           
        # --- STEP 3.1 - CONFIGURATION PHASE 1 ---
        if not st.session_state['CONFIG']['PHASE_1']['VALIDATION']: 
            setupConfigP1(areaSpinning, areaPlaceholder)
            return 
        
        # --- STEP 3.2 - CONFIGURATION PHASE 2 ---
        elif st.session_state['CONFIG']['PHASE_1']['VALIDATION'] and not st.session_state['CONFIG']['PHASE_2']['VALIDATION']:
            setupConfigP2(areaSpinning, areaPlaceholder)
            return
        
        # --- STEP 3.3 - CONFIGURATION VALIDATION ---
        if automaticalyValidate(configFilePath=configPath):
            st.experimental_rerun()  
    
    
    # -- STEP 4 - LOAD/RELOAD the MODEL/DATASET and UPSERT the DATA into the PINECONE INDEX -- 
    if st.session_state['CONFIG']['LFDMIP']:
        if not st.session_state['LOAD']['DATASET']:
            with st.spinner(f"{st.session_state['FIFTYONE']['USER']['DATASET']} dataset is Loading..."):
                st.session_state['LOAD']['DATASET'] = loadZoo_dataset(st.session_state['FIFTYONE']['USER']['DATASET'], st.session_state['FIFTYONE']['USER']['SPLIT'].split(','))   
        st.write(f"""<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace"> FIFTYONE DATASET - {st.session_state['FIFTYONE']['USER']['DATASET'].upper()} | LOADED ✅</h3></div>""", unsafe_allow_html=True)
        if not st.session_state['LOAD']['MODEL']:
            with st.spinner(f"{st.session_state['FIFTYONE']['USER']['MODEL']} model is Loading..."):
                st.session_state['LOAD']['MODEL'] = loadZoo_model(modelName=st.session_state['FIFTYONE']['USER']['MODEL'])
        st.write(f"""<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace"> FIFTYONE MODEL - {st.session_state['FIFTYONE']['USER']['MODEL'].upper()} | LOADED ✅</h3></div>""", unsafe_allow_html=True)
        if not st.session_state['LOAD']['DICT_DATASET']:
            with st.spinner(f"Embeddings and Data Construction in Progress..."):
                st.session_state['LOAD']['DATASET'].compute_embeddings(st.session_state['LOAD']['MODEL'], embeddings_field="embedding")
                st.session_state['LOAD']['DICT_DATASET'] = constructDictInf(st.session_state['LOAD']['DATASET'])
        st.write(f"""<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace"> DATA EMBEDDING - {st.session_state['FIFTYONE']['USER']['MODEL'].upper()} | DONE ✅</h3></div>""", unsafe_allow_html=True)
        with st.spinner(f"Upserting Data into Pinecone Index in Progress..."):
            st.session_state['PINECONE']['USER']['INDEX'].delete(deleteAll='true')
            upsert_Data(st.session_state['PINECONE']['USER']['INDEX'], st.session_state['LOAD']['DICT_DATASET'])
        st.write(f"""<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace"> DATA UPSERT into PINECONE INDEX | DONE ✅</h3></div>""", unsafe_allow_html=True)
        time.sleep(2)
        st.session_state['CONFIG']['LFDMIP'] = False
        st.session_state['CONFIG']['CLIP_MODEL'] = st.session_state['LOAD']['MODEL']
        st.session_state['CONFIG']['PHASE_1']['VALIDATION'] = True
        st.session_state['CONFIG']['PHASE_2']['VALIDATION'] = True
        st.session_state['CONFIG']['VALIDATION'] = False
        st.experimental_rerun()
    
    
    # -- STEP 5 - DISPLAY THE CONFIGURATION INFORMATION -- 
    if st.session_state['CONFIG']['INFORMATION']:
        st.write(st.session_state['CONFIG']['INFORMATION'], unsafe_allow_html=True)
        if not st.session_state['CONFIG']['DISABLE_CONFIG_BUTTONS']:
            _, col1, _, col2, _ = st.columns([1.75, 4, 0.5, 4, 1.75]) 
            if col1.button('Modify/Update the Configuration'):
                st.session_state['PINECONE']['USER']['KEY']['VALUE'] = ""
                st.session_state['PINECONE']['USER']['INDEX_NAME'] = ""
                st.session_state['CONFIG']['VALIDATION'] = False
                st.session_state['CONFIG']['INFORMATION'] = ''
                st.session_state['CONFIG']['PHASE_1']['VALIDATION'] = False
                st.session_state['CONFIG']['PHASE_2']['VALIDATION'] = False
                st.experimental_rerun()
            if col2.button('Re-Load the MODEL/DATASET'):
                st.session_state['LFDMIP'] = True
                st.experimental_rerun()
                
            
     # -- STEP 6 - QUERY | SEGMENTIC REQUEST -- 
    st.markdown('<br>', unsafe_allow_html=True)
    st.markdown('<hr/>', unsafe_allow_html=True)
    st.subheader('Query Image from Text Input')
    with st.form("query_form"):  
        _, col1, _, col2, _ = st.columns([1.5, 6, 1, 2, 1.5])
        queryString = col1.text_input(label="Text Request", value="A plate of fruits", label_visibility="visible")
        queryNumb = col2.number_input(label='Number of Images', value=9, min_value=1, max_value=50, step=1, label_visibility='visible')
        if st.form_submit_button("Query"):
            st.session_state['QUERY']['VALIDATE'] = True
            st.session_state['QUERY']['STRING'] = queryString
            st.session_state['QUERY']['NUMBER'] = queryNumb
    
    if not st.session_state['QUERY']['VALIDATE']:
        return
    
    st.session_state['QUERY']['VALIDATE'] = False
    with st.spinner(f"Loading Model..."):
        if not st.session_state['CONFIG']['CLIP_MODEL']:
            st.session_state['CONFIG']['CLIP_MODEL'] = loadZoo_model(modelName=st.session_state['FIFTYONE']['USER']['MODEL'])

    # --- Query Pinecone ---
    textVect = get_text_embedding(st.session_state['QUERY']['STRING'], st.session_state['CONFIG']['CLIP_MODEL'])
    resultQuery = queryPinecone(st.session_state['PINECONE']['USER']['INDEX'], textVect, st.session_state['QUERY']['NUMBER'], True)

    # DISPLAY IMAGE URL
    col1, col2, col3 = st.columns([4,4,4])
    for i in range(len(resultQuery["matches"])):     
        slct_col = [col1, col2, col3][i%3]
        slct_col.write(f"""
                <div style="text-align:center">
                    <span style="text-align:center"><a href={resultQuery["matches"][i]["id"]}>Image {i+1} &nbsp; - &nbsp; Score : {round(resultQuery["matches"][i]["score"], 3)}</a></span>
                </div>
        """, unsafe_allow_html=True)
        try:
            slct_col.image(Image.open(requests.get(resultQuery["matches"][i]["id"], stream=True).raw).resize((512, 512)))
        except:
            slct_col.image(Image.open(resultQuery["matches"][i]["id"]).resize((512, 512)))

        
        slct_col.write('</br>', unsafe_allow_html=True) 


    
# -- CORE --
if __name__ == "__main__":
    main()