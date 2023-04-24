####################################
# CLIP - SEARCH ENGINE - APP UTILS #
####################################


# - IMPORTS -

# -- General Libraries --
import requests
import pinecone
import streamlit as st

# -- Custom Variables and Functions --
from fiftyone_datasets_models import getZoo_datasets, getZoo_models
from pinecone_manipulation import getPineconeIndexes


# - FUNCTIONS -

# -- Streamlit related Functions --

# -- Hide Streamlit Menu and Non Estethic Elements --
def hideStreamlitElements():
    """Hide Streamlit elements that are not estethic."""    
    st.markdown("""
        <style>
            div[data-testid="stToolbar"] {visibility: hidden; height: 0%; position: fixed;}
            div[data-testid="stDecoration"] {visibility: hidden; height: 0%; position: fixed;}
            div[data-testid="stStatusWidget"] {visibility: hidden; height: 0%; position: fixed;}
            #MainMenu {visibility: hidden; height: 0%;}
            header {visibility: hidden; height: 0%;}
            footer {visibility: hidden; height: 0%;}
        </style>
    """, unsafe_allow_html=True) 
     
# --- Streamlit Button Style ---
def streamlitButton(txt_col="rgb(255, 255, 255)", txth_col="rgb(0, 0, 0)", bg_col="rgb(204, 49, 49)", bgh_color="rgb(255, 255, 255)"):
    """Modify the intial style of the Streamlit Buttons
    Args:
        txt_col (str, optional): Text color . Defaults to "rgb(255, 255, 255)".
        txth_col (str, optional): Text color when hovering. Defaults to "rgb(0, 0, 0)".
        bg_col (str, optional): Background color. Defaults to "rgb(204, 49, 49)".
        bgh_color (str, optional): Backgrond color when hovering. Defaults to "rgb(255, 255, 255)".
    """
    st.markdown("""
        <style>
            div.stButton {text-align: center;}
            div.stButton > button:first-child {background-color:""" + bg_col + """;color:""" + txt_col + """;}
            div.stButton > button:first-child:hover {background-color:""" + bgh_color + """;color:""" + txth_col + """;}
        </style>
    """, unsafe_allow_html=True)



# -- PINECONE / FIFTYONE --

def automaticalyValidate(configFilePath='config.py'):
    """_summary_

    Args:
        configFilePath (str, optional): _description_. Defaults to 'config.py'.

    Returns:
        boolean: result of the verification
    """    
    lsIndexes = getPineconeIndexes(st.session_state['PINECONE_KEY'], st.session_state['PINECONE_ENV'])
    if lsIndexes != False:
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
                config_button = f"""DISABLE_CONFIG_BUTTONS= {st.session_state['DISABLE_CONFIG_BUTTONS']}\n"""
                print(config_pinecone + config_fiftyone + config_button, file=f)

            st.session_state['config_validation'] = True
            return True
    return False


def verifyParams():
    tempConfig = True
    
    # --- Verify PINECONE CONFIGURATION ---
    lsIndexes = getPineconeIndexes(st.session_state['PINECONE_KEY'], st.session_state['PINECONE_ENV'])
    if lsIndexes != False:
        st.session_state['warning_phase1'] = False
    else:
        st.session_state['warning_phase1'] = True
        tempConfig = False

    # --- Verify FIFTYONE CONFIGURATION ---
    if not st.session_state['FIFTYONE_DATASET'] in getZoo_datasets():
        tempConfig = False
    if not st.session_state['FIFTYONE_MODEL'] in getZoo_models():
        tempConfig = False

    # --- Return OUTPUT --- 
    if tempConfig:
        st.session_state['config_phase1'] = True