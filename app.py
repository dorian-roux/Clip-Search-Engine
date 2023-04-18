##############################
# CLIP - SEARCH ENGINE - APP #
##############################


# - IMPORTS -

# -- Add "src" folder to the system Paths --
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# -- General Libraries --
import time
import requests
import re 
import streamlit as st
from PIL import Image
import pinecone
import fiftyone

# -- Custom Variables and Functions --
try:
    from config import *
except:
    pass

# from utils import setupVariables
from loads_data_model import construct_data_coco, display_zoo_datasets, display_zoo_models, load_zoo_dataset, load_zoo_model
from setup_pinecone import create_pinecone_index, load_pinecone_index, upsert_Data_Coco, query_pinecone
from make_text_embedding import get_text_embedding


# -- FUNCTION --

# -- Ensure the existence of any variables --
def setupVariables(variable, exceptValue=None):
    """_summary_

    Args:
        variable (_type_): _description_
        exceptValue (_type_, optional): _description_. Defaults to None.

    Returns:
        _type_: _description_
    """    
    if variable in globals():
        return globals()[variable]
    return exceptValue


# - CORE - 
def main():
    
    # -- Setup CONFIG Variables --
    for variable in ['PINECONE_KEY', 'PINECONE_ENV', 'PINECONE_INDEX_NAME', 'FIFTYONE_DATASET', 'FIFTYONE_DATASET_SPLIT', 'FIFTYONE_MODEL']:
        globals()[variable] = setupVariables(variable, exceptValue="")
    print(PINECONE_KEY)

    # -- Setup STREAMLIT Page -- 
    config_page_title, config_page_icon, config_layout = 'CLIP - Search Engine', '', "wide"
    st.set_page_config(page_title=config_page_title, layout=config_layout)  # Set Page Configuration
    st.markdown("""<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>""", unsafe_allow_html=True) 
    st.title("CLIP - Search Engine - Text Requests to Images")
    
    st.markdown("""
        <style>
        div.stButton {
            text-align: center;
        }
        div.stButton > button:first-child {
            background-color: rgb(204, 49, 49);
        }
        div.stButton > button:first-child:hover {
            background-color: rgb(255, 255, 255);
        </style>""", unsafe_allow_html=True)


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
    def automaticalyValidate(configFilePath='config.py'):
        pinecone.init(api_key=st.session_state['PINECONE_KEY'], environment=st.session_state['PINECONE_ENV'])
        try:
            lsIndexes = pinecone.list_indexes()
            if st.session_state['PINECONE_INDEX_NAME'] in lsIndexes:
                st.session_state['PINECONE_INDEX'] = pinecone.Index(st.session_state['PINECONE_INDEX_NAME'])
                describeIndex = pinecone.describe_index(st.session_state['PINECONE_INDEX_NAME'])
                numbVectors = requests.get('https://clip-search-engine-652a509.svc.us-central1-gcp.pinecone.io/describe_index_stats', headers={"Api-Key": st.session_state['PINECONE_KEY']}).json()['totalVectorCount']
                st.session_state['config_information'] = f'''
                    <div style="text-align:center; margin-top:25px; margin-bottom:25px"> 
                        <div style="display: inline-block; vertical-align: top; border:2px solid #BDBDBD; border-radius:10px; padding:25px; text-align:center">
                            <h3>Configuration Summary</h3>
                            <div style="width:100%; display: flex; justify-content: center; margin-top:15px">
                                <table style="text-align: center; margin-right:10px">
                                    <thead>
                                        <tr>
                                            <th>PINECONE KEY</th>
                                            <th>PINECONE ENV</th>
                                            <th>INDEX NAME</th>
                                            <th>METRIC</th>
                                            <th>DIMENSION</th>
                                            <th>POD TYYPE</th>
                                            <th>TOTAL VECTORS</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>{st.session_state['PINECONE_KEY'][:-8] + '*'*8}</td>
                                            <td>{st.session_state['PINECONE_ENV']}</td>
                                            <td>{describeIndex.name}</td>
                                            <td>{describeIndex.metric}</td>
                                            <td>{describeIndex.dimension}</td>
                                            <td>{describeIndex.pod_type}</td>
                                            <td>{numbVectors}</td>
                                        </tr>
                                    </tbody>
                                    <caption style="text-align:center">Pinecone Parameters</caption>
                                </table>
                                <table style="text-align: center; margin-left:10px">
                                    <thead>
                                        <tr>
                                            <th>FIFTYONE DATASET</th>
                                            <th>FIFTYONE DATASET SPLIT</th>
                                            <th>FIFTYONE MODEL</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        <tr>
                                            <td>{st.session_state['FIFTYONE_DATASET']}</td>
                                            <td>{st.session_state['FIFTYONE_DATASET_SPLIT']}</td>
                                            <td>{st.session_state['FIFTYONE_MODEL']}</td>
                                        </tr>
                                    </tbody>
                                    <caption style="text-align:center">Fiftyone Parameters</caption>
                                </table>
                            </div>
                        </div>
                    </div>
                '''
                with open(configFilePath, "w") as f:
                    config_pinecone = f"""PINECONE_KEY = "{st.session_state['PINECONE_KEY']}"\nPINECONE_ENV = "{st.session_state['PINECONE_ENV']}"\nPINECONE_INDEX_NAME = "{st.session_state['PINECONE_INDEX_NAME']}"\n"""
                    config_fiftyone =  f"""FIFTYONE_DATASET = "{st.session_state['FIFTYONE_DATASET']}"\nFIFTYONE_DATASET_SPLIT = "{st.session_state['FIFTYONE_DATASET_SPLIT']}"\nFIFTYONE_MODEL = "{st.session_state['FIFTYONE_MODEL']}"\n"""
                    print(config_pinecone + config_fiftyone, file=f)
    
                st.session_state['config_validation'] = True
                return True
        except:
            pass
        return False
            
    if st.session_state['config_information']:
        st.write(st.session_state['config_information'], unsafe_allow_html=True)
        _, col1, _, col2, _ = st.columns([3.75, 2, 0.5, 2, 3.75]) 
        if col1.button('Modify/Update the Configuration', disabled=True):
            st.session_state['PINECONE_KEY'] = ""
            st.session_state['PINECONE_INDEX_NAME'] = ""
            st.session_state['config_validation'] = False
            st.session_state['config_information'] = None
            st.experimental_rerun()
        if col2.button('Re-Load the MODEL/DATASET', disabled=True):
            st.session_state['config_reload'] = True
            st.experimental_rerun()
            
    if not st.session_state['config_validation']:
        with st.spinner('Automatic Validation of the Configuration ...'):
            verifyValidation = automaticalyValidate()
        if verifyValidation:
            st.experimental_rerun()
        else:
            if not st.session_state['config_phase1']:
                
                def verifyParams():
                    tempConfig = True
                    
                    # --- Verify PINECONE CONFIGURATION ---
                    pinecone.init(api_key=st.session_state['PINECONE_KEY'], environment=st.session_state['PINECONE_ENV'])
                    try:
                        pinecone.list_indexes()
                        st.session_state['warning_phase1'] = False
                    except:
                        st.session_state['warning_phase1'] = True
                        tempConfig = False
 
                    # --- Verify FIFTYONE CONFIGURATION ---
                    ls_datasets_splits = list(filter(lambda val : val in ['train', 'test', 'validation'], st.session_state['FIFTYONE_DATASET_SPLIT'].split(',')))
                    if not st.session_state['FIFTYONE_DATASET'] in display_zoo_datasets():
                        tempConfig = False
                    if not ls_datasets_splits:
                        tempConfig = False
                    if not st.session_state['FIFTYONE_MODEL'] in display_zoo_models():
                        tempConfig = False

                    # --- Return OUTPUT --- 
                    if tempConfig:
                        st.session_state['config_phase1'] = True
            
            
                # --- Display the CONFIGURATION FORM ---
                with st.form("setup_form", clear_on_submit=False):
                        st.write('Insert the PINECONE KEY and ENVIRONMENT')
                        col1, _, col2 = st.columns([5.25, 0.5, 5.25])
                        st.session_state['PINECONE_KEY'] = col1.text_input(label='Insert your PINECONE KEY', value="")
                        st.session_state['PINECONE_ENV'] = col2.text_input(label='Insert your PINECONE ENVIRONMENT', value=st.session_state['PINECONE_ENV'])
                        if st.session_state['warning_phase1']:
                            st.warning(body='PINECONE KEY or PINECONE ENVIRONMENT are not valid')

                        st.markdown('</br>', unsafe_allow_html=True)
                        st.write('Insert the FIFTYONE CONFIGURATION')
                        ls_datasets_ZOO, default_dataset = display_zoo_datasets(), 'coco-2017'
                        ls_models_ZOO, default_model = display_zoo_models(), 'clip-vit-base32-torch'
                        ls_splits_option = ['train', 'test', 'validation']
                        col1, _, col2, _, col3, _  = st.columns([3, 0.25, 3, 0.25, 3, 2.75])
                        st.session_state['FIFTYONE_DATASET'] = col1.selectbox(label='Dataset Choice', options=list(map(lambda dataset : dataset.upper(), ls_datasets_ZOO)), index=ls_datasets_ZOO.index(default_dataset), label_visibility='visible')
                        st.session_state['FIFTYONE_DATASET'] = ls_datasets_ZOO[list(map(lambda dataset : dataset.upper(), ls_datasets_ZOO)).index(st.session_state['FIFTYONE_DATASET'])]
                        st.session_state['FIFTYONE_DATASET_SPLIT'] = col2.multiselect(label='Split Choice', options=ls_splits_option, default=['validation'])
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
                    pineconeIndexName = col1.selectbox(label='Pinecone Index', options=pinecone.list_indexes(), index=0, label_visibility='visible')
                    txt_pineconeIndexName = col2.text_input(label='Write your PINECONE INDEX', value="")
                    if st.session_state['warning_phase2']:
                        for content in st.session_state['warning_phase2'].split('\n'):
                            st.error(body=content)  
                        st.info(body='FIX the warning and reValidate')
                    
                    submitted = st.form_submit_button('Valiate the PINECONE INDEX')
                    if submitted:
                        if txt_pineconeIndexName:
                            pineconeIndexName = txt_pineconeIndexName
                            try:
                                pinecone.create_index(name=pineconeIndexName, dimension=512, metric='cosine', pod_type='pod1')
                                st.session_state['PINECONE_INDEX_NAME'] = pineconeIndexName
                                st.session_state['config_phase2'] = True
                            except pinecone.core.client.exceptions.ApiException as e:
                                exceptionInf = re.compile("HTTP response body:(.*)$").search(str(e)).group(1)
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
                st.session_state['LOAD_DATASET'] = load_zoo_dataset(st.session_state['FIFTYONE_DATASET'], st.session_state['FIFTYONE_DATASET_SPLIT'].split(','))   
        
        if not st.session_state['LOAD_MODEL']:
            with st.spinner(f"{st.session_state['FIFTYONE_MODEL']} model is Loading..."):
                st.session_state['LOAD_MODEL'] = load_zoo_model(modelName="clip-vit-base32-torch")

        if not st.session_state['DICT_DATASET']:
            with st.spinner(f"Embeddings and Data Construction in Progress..."):
                if not st.session_state['LOAD_DATASET_WEMBEDDINGS']:
                    st.session_state['LOAD_DATASET'].compute_embeddings(st.session_state['LOAD_MODEL'], embeddings_field="embedding")
                    st.session_state['LOAD_DATASET_WEMBEDDINGS'] = True
                st.session_state['DICT_DATASET'] = construct_data_coco(st.session_state['LOAD_DATASET'], "2017", st.session_state['FIFTYONE_DATASET_SPLIT'].split(','))
       
        st.session_state['PINECONE_INDEX'].delete(deleteAll='true')
        st.session_state['PINECONE_INDEX'] = upsert_Data_Coco(st.session_state['PINECONE_INDEX'], st.session_state['DICT_DATASET'])
        st.session_state['config_reload'] = False
        st.session_state['clipModel'] = None

    
    # -- STEP 3 - QUERY --
    st.markdown('</br></br>', unsafe_allow_html=True)
    st.markdown('<hr/>', unsafe_allow_html=True)
    st.subheader('Query Image from Text Input')
    with st.form("query_form"):  
        _, col1, _, col2, _ = st.columns([1.5, 6, 1, 2, 1.5])
        queryString = col1.text_input(label="Text Request", value="A basketball field", label_visibility="visible")
        queryNumb = col2.number_input(label='Number of Images', value=12, min_value=1, max_value=50, step=1, label_visibility='visible')
        if st.form_submit_button("Query"):
            st.session_state['QUERY_STRING'] = queryString
            st.session_state['QUERY_NUMBER'] = queryNumb
    
    if not st.session_state['QUERY_STRING'] and not st.session_state['QUERY_NUMBER']:
        return
    
    with st.spinner(f"Loading Model..."):
        if 'clipModel' not in st.session_state:
            st.session_state['clipModel'] = load_zoo_model(modelName="clip-vit-base32-torch")
        if not st.session_state['clipModel']:
            st.session_state['clipModel'] = load_zoo_model(modelName="clip-vit-base32-torch")

       
    # 3° - Query Pinecone
    textVect = get_text_embedding(st.session_state['QUERY_STRING'], st.session_state['clipModel'])
    resultQuery = query_pinecone(st.session_state['PINECONE_INDEX'], textVect, st.session_state['QUERY_NUMBER'])
 
    # DISPLAY IMAGE URL
    col1, col2, col3 = st.columns([4,4,4])
    for i in range(len(resultQuery["matches"])):     
        slct_col = [col1, col2, col3][i%3]
        slct_col.write(f"""
            <span style="text-align:center">Image {i+1} &nbsp; - &nbsp; Score : {round(resultQuery["matches"][i]["score"], 3)} &nbsp; - &nbsp;&nbsp; <a href={resultQuery["matches"][i]["id"]}>Link toward the Image</a></span>
        """, unsafe_allow_html=True)
        
        slct_col.image(Image.open(requests.get(resultQuery["matches"][i]["id"], stream=True).raw).resize((512, 512)))
        slct_col.write('</br>', unsafe_allow_html=True)


    
# -- CORE --
if __name__ == "__main__":
    main()