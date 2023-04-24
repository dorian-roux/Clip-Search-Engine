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
import streamlit as st
from PIL import Image

# -- Custom Variables and Functions --
try:
    from config import *
except:
    pass

from utils import hideStreamlitElements, streamlitButton, automaticalyValidate, verifyParams
from fiftyone_datasets_models import constructDictInf, getZoo_datasets, getZoo_models, loadZoo_dataset, loadZoo_model
from pinecone_manipulation import getPineconeIndexes, createPineconeIndex, upsert_Data, queryPinecone
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
DISABLE_CONFIG_BUTTONS = setupVariables('DISABLE_CONFIG_BUTTONS', False)


# -- Core Streamlit -- 
def main():
    
    # -- Setup the Paths -- 
    staticPath = os.path.join(os.path.dirname(__file__), 'src', 'static')
    pathImages_logo = os.path.join(staticPath, 'images', 'iconCYTECH.png')
    
    # -- Setup CONFIG Variables --
    for variable in ['PINECONE_KEY', 'PINECONE_ENV', 'PINECONE_INDEX_NAME', 'FIFTYONE_DATASET', 'FIFTYONE_DATASET_SPLIT', 'FIFTYONE_MODEL']:
        globals()[variable] = setupVariables(variable, exceptValue="")

    # -- Setup STREAMLIT Page -- 
    config_page_title, config_layout = 'CLIP - Search Engine', "wide"
    st.set_page_config(page_title=config_page_title, page_icon=pathImages_logo, layout=config_layout)  # Set Page Configuration
    st.title("CLIP - Search Engine - Text Requests to Images")
    hideStreamlitElements()  # --- Hide Streamlit Elements ---
    streamlitButton() # --- Change the Streamlit Button Style ---

    # -- Setup the STREAMLIT Seassion State -- 
    if 'config' not in st.session_state:
        st.session_state['config'] = False
        st.session_state['config_information'] = ''
        st.session_state['config_reload'] = False
        st.session_state['config_validation'] = False
        st.session_state['config_phase1'] = False
        st.session_state['config_phase2'] = False
        st.session_state['warning_phase1'] = False
        st.session_state['warning_phase2'] = False

        st.session_state['DISABLE_CONFIG_BUTTONS'] = DISABLE_CONFIG_BUTTONS
        st.session_state['pinecone_config'] = False
        st.session_state['PINECONE_KEY'] = PINECONE_KEY
        st.session_state['PINECONE_ENV'] = PINECONE_ENV
        st.session_state['PINECONE_INDEX_NAME'] = PINECONE_INDEX_NAME
        st.session_state['PINECONE_INDEX'] = None
        st.session_state['FIFTYONE_DATASET'] = FIFTYONE_DATASET
        st.session_state['FIFTYONE_DATASET_SPLIT'] = FIFTYONE_DATASET_SPLIT
        st.session_state['FIFTYONE_MODEL'] = FIFTYONE_MODEL
        st.session_state['LOAD_DATASET'] = None
        st.session_state['LOAD_DATASET_WEMBEDDINGS'] = None
        st.session_state['LOAD_MODEL'] = None
        st.session_state['DICT_DATASET'] = None
        
        st.session_state['QUERY_STRING'] = None
        st.session_state['QUERY_NUMBER'] = None

    # -- STEP 2 - VERIFY THE PARAMETERS -- 
    placeholder = st.empty()
            
    if st.session_state['config_information']:
        st.write(st.session_state['config_information'], unsafe_allow_html=True)
        _, col1, _, col2, _ = st.columns([1.75, 4, 0.5, 4, 1.75]) 
        if col1.button('Modify/Update the Configuration', disabled=st.session_state['DISABLE_CONFIG_BUTTONS']):
            st.session_state['PINECONE_KEY'] = ""
            st.session_state['PINECONE_INDEX_NAME'] = ""
            st.session_state['config_validation'] = False
            st.session_state['config_information'] = None
            st.experimental_rerun()
        if col2.button('Re-Load the MODEL/DATASET', disabled=st.session_state['DISABLE_CONFIG_BUTTONS']):
            st.session_state['config_reload'] = True
            st.experimental_rerun()
            
    if not st.session_state['config_validation']:
        with st.spinner('Automatic Validation of the Configuration ...'):
            verifyValidation = automaticalyValidate()
        if verifyValidation:
            st.experimental_rerun()
        else:
            if not st.session_state['config_phase1']:     
            
                # --- Display the CONFIGURATION FORM ---
                with st.form("setup_form", clear_on_submit=False):
                        st.write('Insert the PINECONE KEY and ENVIRONMENT')
                        col1, _, col2, _, col3 = st.columns([3.25, 0.25, 4, 0.5, 4])
                        st.session_state['DISABLE_CONFIG_BUTTONS'] = col1.radio(label='Deactivate Home Config Button', options=[True, False], index=[True, False].index(st.session_state['DISABLE_CONFIG_BUTTONS']))
                        st.session_state['PINECONE_KEY'] = col2.text_input(label='Insert your PINECONE KEY', value="")
                        st.session_state['PINECONE_ENV'] = col3.text_input(label='Insert your PINECONE ENVIRONMENT', value=st.session_state['PINECONE_ENV'])
                        if st.session_state['warning_phase1']:
                            st.warning(body='PINECONE KEY or PINECONE ENVIRONMENT are not valid')

                        st.markdown('</br>', unsafe_allow_html=True)
                        st.write('Insert the FIFTYONE CONFIGURATION')
                        ls_datasets_ZOO, default_dataset = getZoo_datasets(), 'coco-2017'
                        ls_models_ZOO, default_model = getZoo_models(), 'clip-vit-base32-torch'
                        ls_splits_option = ['train', 'test', 'validation']
                        col1, _, col2, _, col3, _  = st.columns([3.5, 0.5, 3.5, 0.5, 3.5, 0.5])
                        st.session_state['FIFTYONE_DATASET'] = col1.selectbox(label='Dataset Choice', options=list(map(lambda dataset : dataset.upper(), ls_datasets_ZOO)), index=ls_datasets_ZOO.index(default_dataset), label_visibility='visible')
                        st.session_state['FIFTYONE_DATASET'] = ls_datasets_ZOO[list(map(lambda dataset : dataset.upper(), ls_datasets_ZOO)).index(st.session_state['FIFTYONE_DATASET'])]
                        st.session_state['FIFTYONE_DATASET_SPLIT'] = col2.multiselect(label='Split Choice', options=ls_splits_option, default=(None if not st.session_state['FIFTYONE_DATASET_SPLIT'] else st.session_state['FIFTYONE_DATASET_SPLIT'].split(',')), label_visibility='visible')
                        st.session_state['FIFTYONE_DATASET_SPLIT'] = ",".join(st.session_state['FIFTYONE_DATASET_SPLIT'])
                        st.session_state['FIFTYONE_MODEL'] = col3.selectbox(label='Model Choice', options=list(map(lambda dataset : dataset.upper(), ls_models_ZOO)), index=ls_models_ZOO.index(default_model), label_visibility='visible')
                        st.session_state['FIFTYONE_MODEL'] = ls_models_ZOO[list(map(lambda dataset : dataset.upper(), ls_models_ZOO)).index(st.session_state['FIFTYONE_MODEL'])]

                        submitted = st.form_submit_button("Validate Parameters")
                        if submitted:
                            verifyParams()
                            st.experimental_rerun()  
                        
            elif st.session_state['config_phase1'] and not st.session_state['config_phase2']:
                # -- PHASE 2 > LOAD PINECONE INDEX --
                with st.form("setup_pinecone_index", clear_on_submit=False):
                    st.write('Select/Insert the PINECONE INDEX')
                    col1, _, col2 = st.columns([5.25, 0.5, 5.25])
                    pineconeIndexName = col1.selectbox(label='Pinecone Index', options=getPineconeIndexes(st.session_state['PINECONE_KEY'], st.session_state['PINECONE_ENV']), index=0, label_visibility='visible')
                    txt_pineconeIndexName = col2.text_input(label='Write your PINECONE INDEX', value="")
                    if st.session_state['warning_phase2']:
                        for content in st.session_state['warning_phase2'].split('\n'):
                            st.error(body=content)  
                    
                    submitted = st.form_submit_button('Valiate the PINECONE INDEX')
                    if submitted:
                        if txt_pineconeIndexName:
                            pineconeIndexName = txt_pineconeIndexName
                            creationPIndexInf = createPineconeIndex(st.session_state['PINECONE_KEY'], st.session_state['PINECONE_ENV'], pineconeIndexName)
                            if creationPIndexInf == True:
                                st.session_state['PINECONE_INDEX_NAME'] = pineconeIndexName
                                st.session_state['config_phase2'] = True
                            else:
                                exceptionInf = re.compile("HTTP response body:(.*)$").search(str(creationPIndexInf)).group(1)
                                st.session_state['warning_phase2'] = f'''Error while creating Pinecone Index \n {exceptionInf.split('.')[0]}.\n{exceptionInf.split('.')[1]}.'''
                        else:
                            st.session_state['PINECONE_INDEX_NAME'] = pineconeIndexName
                            st.session_state['config_phase2'] = True
                        st.experimental_rerun()   
        return

    
    if st.session_state['config_reload']:
        # -- PHASE 2 > LOAD DATASETS and MODEL --       
        # # 1° - Load COCO Dataset / Load Model
        if not st.session_state['LOAD_DATASET']:
            with st.spinner(f"{st.session_state['FIFTYONE_DATASET']} dataset is Loading..."):
                st.session_state['LOAD_DATASET'] = loadZoo_dataset(st.session_state['FIFTYONE_DATASET'], st.session_state['FIFTYONE_DATASET_SPLIT'].split(','))   
        
        if not st.session_state['LOAD_MODEL']:
            with st.spinner(f"{st.session_state['FIFTYONE_MODEL']} model is Loading..."):
                st.session_state['LOAD_MODEL'] = loadZoo_model(modelName=st.session_state['FIFTYONE_MODEL'])

        if not st.session_state['DICT_DATASET']:
            with st.spinner(f"Embeddings and Data Construction in Progress..."):
                if not st.session_state['LOAD_DATASET_WEMBEDDINGS']:
                    st.session_state['LOAD_DATASET'].compute_embeddings(st.session_state['LOAD_MODEL'], embeddings_field="embedding")
                    st.session_state['LOAD_DATASET_WEMBEDDINGS'] = True
                st.session_state['DICT_DATASET'] = constructDictInf(st.session_state['LOAD_DATASET'], "2017", st.session_state['FIFTYONE_DATASET_SPLIT'].split(','))
       
        st.session_state['PINECONE_INDEX'].delete(deleteAll='true')
        upsert_Data(st.session_state['PINECONE_INDEX'], st.session_state['DICT_DATASET'])
        st.session_state['config_reload'] = False
        st.session_state['clipModel'] = None

    
    # -- STEP 3 - QUERY --
    st.markdown('</br></br>', unsafe_allow_html=True)
    st.markdown('<hr/>', unsafe_allow_html=True)
    st.subheader('Query Image from Text Input')
    with st.form("query_form"):  
        _, col1, _, col2, _ = st.columns([1.5, 6, 1, 2, 1.5])
        queryString = col1.text_input(label="Text Request", value="A plate of fruits", label_visibility="visible")
        queryNumb = col2.number_input(label='Number of Images', value=9, min_value=1, max_value=50, step=1, label_visibility='visible')
        if st.form_submit_button("Query"):
            st.session_state['QUERY_STRING'] = queryString
            st.session_state['QUERY_NUMBER'] = queryNumb
    
    if not st.session_state['QUERY_STRING'] and not st.session_state['QUERY_NUMBER']:
        return
    
    with st.spinner(f"Loading Model..."):
        if 'clipModel' not in st.session_state:
            st.session_state['clipModel'] = loadZoo_model(modelName=st.session_state['FIFTYONE_MODEL'])
        if not st.session_state['clipModel']:
            st.session_state['clipModel'] = loadZoo_model(modelName=st.session_state['FIFTYONE_MODEL'])

       
    # 3° - Query Pinecone
    textVect = get_text_embedding(st.session_state['QUERY_STRING'], st.session_state['clipModel'])
    resultQuery = queryPinecone(st.session_state['PINECONE_INDEX'], textVect, st.session_state['QUERY_NUMBER'])
 
    # DISPLAY IMAGE URL
    col1, col2, col3 = st.columns([4,4,4])
    for i in range(len(resultQuery["matches"])):     
        slct_col = [col1, col2, col3][i%3]
        slct_col.write(f"""
                <div style="text-align:center">
                    <span style="text-align:center"><a href={resultQuery["matches"][i]["id"]}>Image {i+1} &nbsp; - &nbsp; Score : {round(resultQuery["matches"][i]["score"], 3)}</a></span>
                </div>
        """, unsafe_allow_html=True)
    
        slct_col.image(Image.open(requests.get(resultQuery["matches"][i]["id"], stream=True).raw).resize((512, 512)))
        slct_col.write('</br>', unsafe_allow_html=True)


    
# -- CORE --
if __name__ == "__main__":
    main()