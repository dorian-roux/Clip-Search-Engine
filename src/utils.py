####################################
# CLIP - SEARCH ENGINE - APP UTILS #
####################################


# - IMPORTS -

# -- General Libraries --
import requests
import pinecone
import streamlit as st
import time
import re

# -- Custom Variables and Functions --
from fiftyone_datasets_models import getZoo_datasets, getZoo_models
from pinecone_manipulation import getPineconeIndexes, createPineconeIndex, deletePineconeIndex


# - FUNCTIONS -

# -- Streamlit related Functions --

# --- Hide Streamlit Menu and Non Estethic Elements ---
# --- Streamlit Button Style ---
def stylizeStreamlitElements(txt_col="rgb(255, 255, 255)", txth_col="rgb(0, 0, 0)", bg_col="rgb(204, 49, 49)", bgh_color="rgb(255, 255, 255)"):
    """Hide Streamlit elements that are not estethic. Modify the intial style of the Streamlit Buttons.  
    Args:
        txt_col (str, optional): Text color . Defaults to "rgb(255, 255, 255)".
        txth_col (str, optional): Text color when hovering. Defaults to "rgb(0, 0, 0)".
        bg_col (str, optional): Background color. Defaults to "rgb(204, 49, 49)".
        bgh_color (str, optional): Backgrond color when hovering. Defaults to "rgb(255, 255, 255)".
    """
    st.markdown("""
        <style>
            div.block-container{padding-top:2rem;padding-bottom:2rem}
            div[data-testid="stToolbar"] {visibility: hidden; height: 0%; position: fixed;}
            div[data-testid="stDecoration"] {visibility: hidden; height: 0%; position: fixed;}
            div[data-testid="stStatusWidget"] {visibility: hidden; height: 0%; position: fixed;}
            #MainMenu {visibility: hidden; height: 0%;}
            header {visibility: hidden; height: 0%;}
            footer {visibility: hidden; height: 0%;}
            div.stButton {text-align: center;}
            div.stButton > button:first-child {background-color:""" + bg_col + """;color:""" + txt_col + """;}
            div.stButton > button:first-child:hover {background-color:""" + bgh_color + """;color:""" + txth_col + """;}
            div.row-widget.stRadio > div{flex-direction:row;justify-content: center;} 
            div.row-widget.stRadio > div > label > div.st-ag{font-weight:bold;padding-left:2px;} 
        </style>
    """, unsafe_allow_html=True) 
    
    
# -- CONFIGURATION related Functions --

# --- PHASE 1 ---
def verifyPhase1():
    # --- Verify PINECONE CONFIGURATION ---
    lsIndexes = getPineconeIndexes(st.session_state['PINECONE']['USER']['KEY']['VALUE'], st.session_state['PINECONE']['USER']['KEY']['ENVIRONMENT'])
    st.session_state['CONFIG']['PHASE_1']['WARNING'] = False
    if not lsIndexes:
        st.session_state['CONFIG']['PHASE_1']['WARNING'] = True
        return False
    # --- Return OUTPUT --- 
    st.session_state['CONFIG']['PHASE_1']['VALIDATION'] = True
    return True
    
def setupConfigP1(areaSpinning, areaPlaceholder):
    areaPlaceholder.empty()
    with areaPlaceholder.container():
        st.markdown("""<div style="text-align:center"><h3 style="font-size:25px; font-family: monospace">Phase 1 - Setup the <span style="color:#090288">PINECONE KEY</span> & <span style="color:#090288">FIFTYONE</span> Configuration</h3></div>""", unsafe_allow_html=True)
        st.markdown(f"""<div style="text-align:left; margin-bottom:-50px"><h6 style="font-size:10px; font-family: monospace; font-style:italic">User Form - Phase 1</h6></div>""", unsafe_allow_html=True)
        with st.form("setup_form"):
            st.markdown(f"""<div style="text-align:center"><h4 style="font-size:20px; font-family: monospace">User Information about the PINECONE KEY</h4></div>""", unsafe_allow_html=True)
            _, col2, _, col3, _ = st.columns([0.25, 5.25, 1, 5.25, 0.25])
            col2.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Define the PINECONE KEY <span style="color:#090288">VALUE</span></h5></div>""", unsafe_allow_html=True)                 
            col3.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Define the PINECONE KEY <span style="color:#090288">ENVIRONEMENT</span></h5></div>""", unsafe_allow_html=True)                 
            st.session_state['PINECONE']['USER']['KEY']['VALUE'] = col2.text_input(label='Insert your PINECONE KEY', label_visibility='collapsed', value="")
            st.session_state['PINECONE']['USER']['KEY']['ENVIRONMENT'] = col3.text_input(label='Insert your PINECONE ENVIRONMENT', label_visibility='collapsed', value=st.session_state['PINECONE']['USER']['KEY']['ENVIRONMENT'])
            if st.session_state['CONFIG']['PHASE_1']['WARNING']:
                _, col1, _ = st.columns([0.25, 11.5, 0.25])
                col1.markdown("""
                    <div style="text-align:center; background-color:#3E3E3E; border-radius:15px">
                        <p style="font-size:15px; font-family: monospace; color:white; padding-top:5px; padding-bottom:5px">
                            <span style="font-size:18px; font-weight:bold">INVALID <span style="color:yellow">PINECONE KEY PARAMETERS</span>!</span>
                            <br>
                            Verify the <span style="color:yellow">PINECONE KEY VALUE</span> and <span style="color:yellow">ENVIRONEMENT</span>.
                        </p>
                    </div>
                """, unsafe_allow_html=True)                 
                
            st.markdown("""<hr style="margin-top:25px; margin-bottom:20px; width:33%; margin: auto; border: 1px dashed black; border-radius:25px"> """, unsafe_allow_html=True)
            
            st.markdown(f"""<div style="text-align:center"><h4 style="font-size:20px; font-family: monospace">User Information about FIFTYONE</h4></div>""", unsafe_allow_html=True)
            _, col1, _, col2, _, col3, _ = st.columns([0.25, 3.5, 0.5, 3.5, 0.5, 3.5, 0.25])
            col1.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Decide the FIFTYONE ZOO <span style="color:#090288">DATASET</span></h5></div>""", unsafe_allow_html=True)   
            col2.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Decide the FIFTYONE ZOO <span style="color:#090288">DATASET SPLIT(S)</span></h5></div>""", unsafe_allow_html=True)   
            col3.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Decide the FIFTYONE ZOO <span style="color:#090288">MODEL</span></h5></div>""", unsafe_allow_html=True)   
            datasetsZOO_upper, datasetZOO_index = list(map(lambda dataset : dataset.upper(), st.session_state['FIFTYONE']['DATASETS'])), st.session_state['FIFTYONE']['DATASETS'].index(st.session_state['FIFTYONE']['DEFAULT']['DATASET'])
            splits_upper, split_default = list(map(lambda dataset : dataset.upper(), st.session_state['FIFTYONE']['SPLITS'])), (None if not st.session_state['FIFTYONE']['USER']['SPLIT'] else list(map(lambda split : split.upper(), st.session_state['FIFTYONE']['USER']['SPLIT'].split(','))))
            modelsZOO_upper, modelZOO_index = list(map(lambda dataset : dataset.upper(), st.session_state['FIFTYONE']['MODELS'])), st.session_state['FIFTYONE']['MODELS'].index(st.session_state['FIFTYONE']['DEFAULT']['MODEL'])
            st.session_state['FIFTYONE']['USER']['DATASET'] = col1.selectbox(label='Dataset Choice', options=datasetsZOO_upper, index=datasetZOO_index, label_visibility='collapsed')
            st.session_state['FIFTYONE']['USER']['SPLIT'] = col2.multiselect(label='Split Choice', options=splits_upper, default=split_default, label_visibility='collapsed')
            st.session_state['FIFTYONE']['USER']['MODEL'] = col3.selectbox(label='Model Choice', options=modelsZOO_upper, index=modelZOO_index, label_visibility='collapsed')   
            st.session_state['FIFTYONE']['USER']['DATASET'] = st.session_state['FIFTYONE']['DATASETS'][datasetsZOO_upper.index(st.session_state['FIFTYONE']['USER']['DATASET'])]
            st.session_state['FIFTYONE']['USER']['SPLIT'] = ",".join(list(map(lambda split : split.lower(), st.session_state['FIFTYONE']['USER']['SPLIT'])))
            st.session_state['FIFTYONE']['USER']['MODEL'] = st.session_state['FIFTYONE']['MODELS'][modelsZOO_upper.index(st.session_state['FIFTYONE']['USER']['MODEL'])]
            col2.markdown("""<div style="margin-top:-10px"><p style="font-size:8px; font-family: monospace"> <span style="text-align:center; padding:2px; border-radius:2px; background-color:#090288; font-weight:bold; font-size:10px;color:white; margin-right:2px">ℹ️</span> An empty selection results in taking <span style="font-weight:bold">ALL</span> available split(s)</p></div>""", unsafe_allow_html=True)   

            st.markdown("""<hr style="margin-top:25px; margin-bottom:20px; width:33%; margin: auto; border: 1px dashed black; border-radius:25px"> """, unsafe_allow_html=True)
            
            submit_phase1 =  st.form_submit_button('Validate the CONFIGURATION') 

    if submit_phase1:
        with areaSpinning.container():
            areaPlaceholder.empty()
            with st.spinner('PARAMETERS - PHASE 1 | Analysis in Progress...'):
                time.sleep(0.5)
                if not verifyPhase1():
                    msg1 = """<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace">⚠️ INVALID <span style="color:#090288">PINECONE Configuration</span></h3></div>"""   
                    msg2 = """<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace">⬅️ RETURN to the <span style="color:#090288">Phase 1 - Configuration Form</span> Menu</h3></div>"""  
                else:
                    msg1 = """<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace">✅ VALID <span style="color:#090288">PHASE 1 - Configuration</span></h3></div>"""
                    msg2 = """<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace">DIRECTION to the <span style="color:#090288">Phase 2 - Configuration Form</span> Menu ➡️</h3></div>"""
                st.markdown(msg1, unsafe_allow_html=True)
                time.sleep(1)
                st.markdown(msg2, unsafe_allow_html=True)
                time.sleep(2)
            areaSpinning.empty()
        st.experimental_rerun()



# --- PHASE 2 ---
def setupConfigP2(areaSpinning, areaPlaceholder):
    areaPlaceholder.empty()
    with areaPlaceholder.container():  
        st.markdown("""<div style="text-align:center; margin-top:10px; margin-bottom:10px"><h3 style="font-size:25px; font-family: monospace">Phase 2 - Setup the <span style="color:#090288">PINECONE INDEX</span> & <span style="color:#090288">DMU</span> Configuration</h3></div>""", unsafe_allow_html=True)
        lsIndexes = getPineconeIndexes(st.session_state['PINECONE']['USER']['KEY']['VALUE'], st.session_state['PINECONE']['USER']['KEY']['ENVIRONMENT'])
        lsDMU = ['Accept DMU', 'Refuse DMU']
        st.session_state['PINECONE']['USER']['DELETE_INDEXES'] = None
        if not lsIndexes:
            st.markdown(f"""<div style="text-align:left; margin-bottom:-50px"><h6 style="font-size:10px; font-family: monospace; font-style:italic">User Form - Phase 2</h6></div>""", unsafe_allow_html=True)
            with st.form("setup-pinecone-index", clear_on_submit=False):
                st.markdown(f"""<div style="text-align:center"><h4 style="font-size:20px; font-family: monospace">User Information about the PINECONE INDEX</h4></div>""", unsafe_allow_html=True)
                _, col1, _, col2, _ = st.columns([1.5, 4, 1, 4, 1.5])
                st.session_state['PINECONE']['USER']['CREATE_INDEX'] = True
                col1.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Define the PINECONE INDEX <span style="color:#090288">NAME</span></h5></div>""", unsafe_allow_html=True)   
                col2.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Select the EXISTING PINECONE  <span style="color:#090288">INDEX(ES)</span> to remove</h5></div>""", unsafe_allow_html=True)   
                st.session_state['PINECONE']['USER']['INDEX_NAME'] = col1.text_input(label='Write your PINECONE INDEX', value="", label_visibility='collapsed')
                st.session_state['PINECONE']['USER']['DELETE_INDEXES'] = col2.multiselect(label='Remove your PINECONE INDEX', options=lsIndexes, label_visibility='collapsed')
                col2.markdown("""<div style="margin-top:-10px"><p style="font-size:8px; font-family: monospace"> <span style="text-align:center; padding:2px; border-radius:2px; background-color:#090288; font-weight:bold; font-size:10px;color:white; margin-right:2px">ℹ️</span> The FREE plan in PINECONE only allows a <span style="color:#090288">Single INDEX</span></p></div>""", unsafe_allow_html=True)   

                _, col1, _, col2, _, col3, _, = st.columns([0.5, 3.5, 0.25, 3.5, 0.25, 3.5, 0.5])
                col1.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Decide the PINECONE INDEX <span style="color:#090288">DIMENSION</span></h5></div>""", unsafe_allow_html=True)   
                col2.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Decide the PINECONE INDEX <span style="color:#090288">METRIC</span></h5></div>""", unsafe_allow_html=True)   
                col3.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Decide the PINECONE INDEX <span style="color:#090288">POD TYPE</span></h5></div>""", unsafe_allow_html=True)   
                
                metrics_upper, metric_index = list(map(lambda metric : metric.upper(), st.session_state['PINECONE']['METRICS'])), st.session_state['PINECONE']['METRICS'].index(st.session_state['PINECONE']['DEFAULT']['METRIC'])
                podtypes_upper, podtype_index = list(map(lambda podtype : podtype.upper(), st.session_state['PINECONE']['POD_TYPES'])), st.session_state['PINECONE']['POD_TYPES'].index(st.session_state['PINECONE']['DEFAULT']['POD_TYPE'])
                st.session_state['PINECONE']['INDEX']['DIMENSION'] = col1.number_input(label='select the PINECONE INDEX DIMENSION', value=st.session_state['PINECONE']['DEFAULT']['DIMENSION'], disabled=True, label_visibility='collapsed')
                st.session_state['PINECONE']['INDEX']['METRIC'] = col2.selectbox(label='select the PINECONE INDEX METRIC', options=metrics_upper, index=metric_index, label_visibility='collapsed')
                st.session_state['PINECONE']['INDEX']['POD_TYPE'] = col3.selectbox(label='select the PINECONE INDEX POD TYPE', options=podtypes_upper, index=podtype_index, label_visibility='collapsed')
                
                st.session_state['PINECONE']['INDEX']['METRIC'] = st.session_state['PINECONE']['METRICS'][metrics_upper.index(st.session_state['PINECONE']['INDEX']['METRIC'])]
                st.session_state['PINECONE']['INDEX']['POD_TYPE'] = list(map(lambda ptype : ptype.split('-')[0].strip().lower(), st.session_state['PINECONE']['POD_TYPES']))[podtypes_upper.index(st.session_state['PINECONE']['INDEX']['POD_TYPE'])]
                if st.session_state['CONFIG']['PHASE_2']['WARNING']:  
                    st.markdown(st.session_state['CONFIG']['PHASE_2']['WARNING'], unsafe_allow_html=True) 
                
                st.markdown("""<hr style="margin-top:25px; margin-bottom:20px; width:33%; margin: auto; border: 1px dashed black; border-radius:25px"> """, unsafe_allow_html=True)
                st.markdown(f"""<div style="text-align:center"><h4 style="font-size:20px; font-family: monospace">User Information about the DMU</h4></div>""", unsafe_allow_html=True)
                st.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Load the FIFTYONE <span style="color:#090288">DATASET</span> / <span style="color:#090288">MODEL</span> & <span style="color:#090288">UPSERT</span> them into the PINECONE <span style="color:#090288">INDEX</span></h5></div>""", unsafe_allow_html=True)   
                _, col1, _ = st.columns([3, 6, 3])
                st.session_state['LFDMIP'] = col1.selectbox(label='Accept Loading and Upserting', options=lsDMU, index=0, label_visibility='collapsed')
                st.session_state['LFDMIP'] = True if lsDMU.index(st.session_state['LFDMIP']) == 0 else False
                col1.markdown("""<div style="margin-top:-10px"><p style="font-size:8px; font-family: monospace"> <span style="text-align:center; padding:2px; border-radius:2px; background-color:#090288; font-weight:bold; font-size:10px;color:white; margin-right:2px">ℹ️</span> This is a time-consuming process required to perform <span style="color:#090288">Segmentic Search</span></p></div>""", unsafe_allow_html=True)   
                st.markdown("""<hr style="margin-top:25px; margin-bottom:20px; width:33%; margin: auto; border: 1px dashed black; border-radius:25px"> """, unsafe_allow_html=True)
                submit_phase2 = st.form_submit_button("Validate the CONFIGURATION")

        else:     
            optionRadio = ['Use an Existing PINECONE INDEX', 'Create a New PINECONE INDEX']
            pineconeRadio = st.radio(label='Type', options=optionRadio, index=0, key='radio-create-use', label_visibility='collapsed')
            if pineconeRadio == optionRadio[1]:
                st.markdown(f"""<div style="text-align:left; margin-bottom:-50px"><h6 style="font-size:10px; font-family: monospace; font-style:italic">User Form - Phase 2</h6></div>""", unsafe_allow_html=True)
                with st.form("setup-pinecone-index", clear_on_submit=False):
                    st.markdown(f"""<div style="text-align:center"><h4 style="font-size:20px; font-family: monospace">User Information about the PINECONE INDEX</h4></div>""", unsafe_allow_html=True)
                    _, col1, _, col2, _ = st.columns([1.5, 4, 1, 4, 1.5])
                    st.session_state['PINECONE']['USER']['CREATE_INDEX'] = True
                    col1.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Define the PINECONE INDEX <span style="color:#090288">NAME</span></h5></div>""", unsafe_allow_html=True)   
                    col2.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Select the EXISTING PINECONE  <span style="color:#090288">INDEX(ES)</span> to remove</h5></div>""", unsafe_allow_html=True)   
                    st.session_state['PINECONE']['USER']['INDEX_NAME'] = col1.text_input(label='Write your PINECONE INDEX', value="", label_visibility='collapsed')
                    st.session_state['PINECONE']['USER']['DELETE_INDEXES'] = col2.multiselect(label='Remove your PINECONE INDEX', options=lsIndexes, label_visibility='collapsed')
                    col2.markdown("""<div style="margin-top:-10px"><p style="font-size:8px; font-family: monospace"> <span style="text-align:center; padding:2px; border-radius:2px; background-color:#090288; font-weight:bold; font-size:10px;color:white; margin-right:2px">ℹ️</span> The FREE plan in PINECONE only allows a <span style="color:#090288">Single INDEX</span></p></div>""", unsafe_allow_html=True)   

                    _, col1, _, col2, _, col3, _, = st.columns([0.5, 3.5, 0.25, 3.5, 0.25, 3.5, 0.5])
                    col1.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Decide the PINECONE INDEX <span style="color:#090288">DIMENSION</span></h5></div>""", unsafe_allow_html=True)   
                    col2.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Decide the PINECONE INDEX <span style="color:#090288">METRIC</span></h5></div>""", unsafe_allow_html=True)   
                    col3.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Decide the PINECONE INDEX <span style="color:#090288">POD TYPE</span></h5></div>""", unsafe_allow_html=True)   
                    
                    metrics_upper, metric_index = list(map(lambda metric : metric.upper(), st.session_state['PINECONE']['METRICS'])), st.session_state['PINECONE']['METRICS'].index(st.session_state['PINECONE']['DEFAULT']['METRIC'])
                    podtypes_upper, podtype_index = list(map(lambda podtype : podtype.upper(), st.session_state['PINECONE']['POD_TYPES'])), st.session_state['PINECONE']['POD_TYPES'].index(st.session_state['PINECONE']['DEFAULT']['POD_TYPE'])
                    st.session_state['PINECONE']['INDEX']['DIMENSION'] = col1.number_input(label='select the PINECONE INDEX DIMENSION', value=st.session_state['PINECONE']['DEFAULT']['DIMENSION'], disabled=True, label_visibility='collapsed')
                    st.session_state['PINECONE']['INDEX']['METRIC'] = col2.selectbox(label='select the PINECONE INDEX METRIC', options=metrics_upper, index=metric_index, label_visibility='collapsed')
                    st.session_state['PINECONE']['INDEX']['POD_TYPE'] = col3.selectbox(label='select the PINECONE INDEX POD TYPE', options=podtypes_upper, index=podtype_index, label_visibility='collapsed')
                    
                    st.session_state['PINECONE']['INDEX']['METRIC'] = st.session_state['PINECONE']['METRICS'][metrics_upper.index(st.session_state['PINECONE']['INDEX']['METRIC'])]
                    st.session_state['PINECONE']['INDEX']['POD_TYPE'] = list(map(lambda ptype : ptype.split('-')[0].strip().lower(), st.session_state['PINECONE']['POD_TYPES']))[podtypes_upper.index(st.session_state['PINECONE']['INDEX']['POD_TYPE'])]
                    if st.session_state['CONFIG']['PHASE_2']['WARNING']:  
                        st.markdown(st.session_state['CONFIG']['PHASE_2']['WARNING'], unsafe_allow_html=True) 
                    
                    st.markdown("""<hr style="margin-top:25px; margin-bottom:20px; width:33%; margin: auto; border: 1px dashed black; border-radius:25px"> """, unsafe_allow_html=True)
                    st.markdown(f"""<div style="text-align:center"><h4 style="font-size:20px; font-family: monospace">User Information about the DMU</h4></div>""", unsafe_allow_html=True)
                    st.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Load the FIFTYONE <span style="color:#090288">DATASET</span> / <span style="color:#090288">MODEL</span> & <span style="color:#090288">UPSERT</span> them into the PINECONE <span style="color:#090288">INDEX</span></h5></div>""", unsafe_allow_html=True)   
                    _, col1, _ = st.columns([3, 6, 3])
                    st.session_state['LFDMIP'] = col1.selectbox(label='Accept Loading and Upserting', options=lsDMU, index=0, label_visibility='collapsed')
                    st.session_state['LFDMIP'] = True if lsDMU.index(st.session_state['LFDMIP']) == 0 else False
                    col1.markdown("""<div style="margin-top:-10px"><p style="font-size:8px; font-family: monospace"> <span style="text-align:center; padding:2px; border-radius:2px; background-color:#090288; font-weight:bold; font-size:10px;color:white; margin-right:2px">ℹ️</span> This is a time-consuming process required to perform <span style="color:#090288">Segmentic Search</span></p></div>""", unsafe_allow_html=True)   
                    st.markdown("""<hr style="margin-top:25px; margin-bottom:20px; width:33%; margin: auto; border: 1px dashed black; border-radius:25px"> """, unsafe_allow_html=True)
                    submit_phase2 = st.form_submit_button("Validate the CONFIGURATION")
                
            else:
                st.session_state['PINECONE']['USER']['CREATE_INDEX'] = False
                st.markdown(f"""<div style="text-align:left; margin-bottom:-50px"><h6 style="font-size:10px; font-family: monospace; font-style:italic">User Form - Phase 2</h6></div>""", unsafe_allow_html=True)
                with st.form("setup-pinecone-index", clear_on_submit=False):
                    st.markdown(f"""<div style="text-align:center"><h4 style="font-size:20px; font-family: monospace">User Information about the PINECONE INDEX</h4></div>""", unsafe_allow_html=True)
                    _, col1, _ = st.columns([3, 6, 3])
                    col1.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Decide the PINECONE INDEX <span style="color:#090288">NAME</span></h5></div>""", unsafe_allow_html=True)   
                    st.session_state['PINECONE']['USER']['INDEX_NAME'] = col1.selectbox(label='Select your PINECONE INDEX', options=lsIndexes, index=0, label_visibility='collapsed')
                    st.markdown("""<hr style="margin-top:25px; margin-bottom:20px; width:33%; margin: auto; border: 1px dashed black; border-radius:25px"> """, unsafe_allow_html=True)
                    st.markdown(f"""<div style="text-align:center"><h4 style="font-size:20px; font-family: monospace">User Information about the DMU</h4></div>""", unsafe_allow_html=True)
                    st.markdown("""<div style="text-align:center; margin-bottom:-25px"><h5 style="font-size:15px; font-family: monospace">Load the FIFTYONE <span style="color:#090288">DATASET</span> / <span style="color:#090288">MODEL</span> & <span style="color:#090288">UPSERT</span> them into the PINECONE <span style="color:#090288">INDEX</span></h5></div>""", unsafe_allow_html=True)   
                    _, col1, _ = st.columns([3, 6, 3])
                    st.session_state['LFDMIP'] = col1.selectbox(label='Accept Loading and Upserting', options=lsDMU, index=0, label_visibility='collapsed')
                    st.session_state['LFDMIP'] = True if lsDMU.index(st.session_state['LFDMIP']) == 0 else False
                    col1.markdown("""<div style="margin-top:-10px"><p style="font-size:8px; font-family: monospace"> <span style="text-align:center; padding:2px; border-radius:2px; background-color:#090288; font-weight:bold; font-size:10px;color:white; margin-right:2px">ℹ️</span> This is a time-consuming process required to perform <span style="color:#090288">Segmentic Search</span></p></div>""", unsafe_allow_html=True)   
                    st.markdown("""<hr style="margin-top:25px; margin-bottom:20px; width:33%; margin: auto; border: 1px dashed black; border-radius:25px"> """, unsafe_allow_html=True)
                    submit_phase2 = st.form_submit_button("Validate the CONFIGURATION")

    if submit_phase2:
        with areaSpinning.container():
            areaPlaceholder.empty()
            with st.spinner('PARAMETERS - PHASE 2 | Analysis in Progress...'):
                time.sleep(0.5)
                if st.session_state['PINECONE']['USER']['CREATE_INDEX']:
                    if not st.session_state['PINECONE']['USER']['INDEX_NAME']:
                        st.session_state['CONFIG']['PHASE_2']['WARNING'] = f"""
                                <div style="text-align:center; background-color:#3E3E3E; border-radius:15px;">
                                    <p style="font-size:15px; font-family: monospace; color:white; padding-top:5px; padding-bottom:5px">
                                        <span style="font-size:18px; font-weight:bold">EMPTY <span style="color:yellow">PINECONE INDEX</span>!</span>
                                    </p>
                                </div>
                            """
                    else:
                        if st.session_state['PINECONE']['USER']['DELETE_INDEXES']:
                            for index in lsIndexes:
                                deletePineconeIndex(st.session_state['PINECONE']['USER']['KEY']['VALUE'], st.session_state['PINECONE']['USER']['KEY']['ENVIRONMENT'], index)
                        creationPIndexInf = createPineconeIndex(st.session_state['PINECONE']['USER']['KEY']['VALUE'], st.session_state['PINECONE']['USER']['KEY']['ENVIRONMENT'], st.session_state['PINECONE']['USER']['INDEX_NAME'], st.session_state['PINECONE']['INDEX']['DIMENSION'], st.session_state['PINECONE']['INDEX']['METRIC'], st.session_state['PINECONE']['INDEX']['POD_TYPE'])
                        if creationPIndexInf == True:
                            st.session_state['CONFIG']['PHASE_2']['VALIDATION'] = True
                        else:
                            exceptionInf = re.compile("HTTP response body:(.*)$").search(str(creationPIndexInf))
                            if exceptionInf:
                                st.session_state['CONFIG']['PHASE_2']['WARNING'] = f"""
                                    <div style="text-align:center; background-color:#3E3E3E; border-radius:15px;">
                                        <p style="font-size:15px; font-family: monospace; color:white; padding-top:5px; padding-bottom:5px">
                                            <span style="font-size:18px; font-weight:bold">ERROR while creating the <span style="color:yellow">PINECONE INDEX</span>!</span>
                                            <br>
                                            {exceptionInf.group(1)}.
                                        </p>
                                    </div>
                                """
                            else:
                                st.session_state['CONFIG']['PHASE_2']['WARNING'] = f"""
                                    <div style="text-align:center; background-color:#3E3E3E; border-radius:15px;">
                                        <p style="font-size:15px; font-family: monospace; color:white; padding-top:5px; padding-bottom:5px">
                                            <span style="font-size:18px; font-weight:bold">ERROR while creating the <span style="color:yellow">PINECONE INDEX</span>!</span>
                                            <br>
                                            Verify your CONFIGURATION.
                                        </p>
                                    </div>
                                """
                else:
                    st.session_state['CONFIG']['PHASE_2']['VALIDATION'] = True

                if not st.session_state['CONFIG']['PHASE_2']['VALIDATION']:
                    msg1 = """<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace">⚠️ INVALID <span style="color:#090288">PINECONE INDEX Configuration</span></h3></div>"""   
                    msg2 = """<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace">⬅️ RETURN to the <span style="color:#090288">Phase 2 - Configuration Form</span> Menu</h3></div>"""  
                else:
                    msg2 = """<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace">DIRECTION to the <span style="color:#090288">MAIN</span> Menu ➡️</h3></div>"""
                    if str(st.session_state['LFDMIP']) == 'True':
                        st.session_state['CONFIG']['LFDMIP'] = True
                        msg2 = """<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace">DIRECTION to the <span style="color:#090288">FINAL PHASE - Configuration</span> Menu ➡️</h3></div>"""
                    msg1 = """<div style="text-align:center; margin-top:10px; margin-bottom:-25px"><h3 style="font-size:25px; font-family: monospace">✅ VALID <span style="color:#090288">PHASE 2 - Configuration</span></h3></div>"""
                st.markdown(msg1, unsafe_allow_html=True)
                time.sleep(1)
                st.markdown(msg2, unsafe_allow_html=True)
                time.sleep(2)
        st.experimental_rerun()   



# -- PINECONE / FIFTYONE --

def automaticalyValidate(configFilePath='.streamlit/secrets.toml'):
    """_summary_

    Args:
        configFilePath (str, optional): _description_. Defaults to 'config.py'.

    Returns:
        boolean: result of the verification
    """    
    lsIndexes = getPineconeIndexes(st.session_state['PINECONE']['USER']['KEY']['VALUE'], st.session_state['PINECONE']['USER']['KEY']['ENVIRONMENT'])
    if lsIndexes != False:
        if st.session_state['PINECONE']['USER']['INDEX_NAME'] in lsIndexes:
            st.session_state['PINECONE']['USER']['INDEX'] = pinecone.Index(st.session_state['PINECONE']['USER']['INDEX_NAME'])
            describeIndex = pinecone.describe_index(st.session_state['PINECONE']['USER']['INDEX_NAME'])
            try:
                numbVectors = requests.get(f"https://{st.session_state['PINECONE']['USER']['INDEX_NAME']}-{pinecone.whoami().projectname}.svc.{st.session_state['PINECONE']['USER']['KEY']['ENVIRONMENT']}.pinecone.io/describe_index_stats", headers={"Api-Key": st.session_state['PINECONE']['USER']['KEY']['VALUE']}).json()['totalVectorCount']
            except:
                numbVectors = 'Not Found'
                
            st.session_state['CONFIG']['INFORMATION'] = f'''
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
                                        <td>{st.session_state['PINECONE']['USER']['KEY']['VALUE'][:-8] + '*'*8}</td>
                                        <td>{st.session_state['PINECONE']['USER']['KEY']['ENVIRONMENT']}</td>
                                        <td>{describeIndex.name}</td>
                                        <td>{describeIndex.metric}</td>
                                        <td>{describeIndex.dimension}</td>
                                        <td>{describeIndex.pod_type}</td>
                                        <td>{numbVectors}{'<p style="font-size:8px">No vectors stored. <br> Load the Model/Dataset</p> ' if numbVectors == 0 else ''}</td>
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
                                        <td>{st.session_state['FIFTYONE']['USER']['DATASET']}</td>
                                        <td>{st.session_state['FIFTYONE']['USER']['SPLIT']}</td>
                                        <td>{st.session_state['FIFTYONE']['USER']['MODEL']}</td>
                                    </tr>
                                </tbody>
                                <caption style="text-align:center">Fiftyone Parameters</caption>
                            </table>
                        </div>
                    </div>
                </div>
            '''
            try:
                with open(configFilePath, "w") as f:
                    config_pinecone = f"""PINECONE_KEY = "{st.session_state['PINECONE']['USER']['KEY']['VALUE']}"\nPINECONE_ENV = "{st.session_state['PINECONE']['USER']['KEY']['ENVIRONMENT']}"\nPINECONE_INDEX_NAME = "{st.session_state['PINECONE']['USER']['INDEX_NAME']}"\n"""
                    config_fiftyone =  f"""FIFTYONE_DATASET = "{st.session_state['FIFTYONE']['USER']['DATASET']}"\nFIFTYONE_DATASET_SPLIT = "{st.session_state['FIFTYONE']['USER']['SPLIT']}"\nFIFTYONE_MODEL = "{st.session_state['FIFTYONE']['USER']['MODEL']}"\n"""
                    config_button = f"""DISABLE_CONFIG_BUTTONS = {str(st.session_state['CONFIG']['DISABLE_CONFIG_BUTTONS']).lower()}\n"""
                    print(config_pinecone + config_fiftyone + config_button, file=f)
            except:
                pass
            st.session_state['CONFIG']['VALIDATION'] = True
            return True
    return False


