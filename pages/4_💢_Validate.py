import streamlit as st
import ifcopenshell
from PIL import Image
from modules.ifctester import ids, reporter

# =========================================================================================================================
# page config
# =========================================================================================================================

im = Image.open('./resources/img/IDS_logo.ico')
st.set_page_config(
    page_title="IDS Converter",
    page_icon=im,
    layout="wide",
    initial_sidebar_state="expanded",
)


# =========================================================================================================================
# System vars
# =========================================================================================================================

if 'ifc_file' not in st.session_state:
    st.session_state.ifc_file = None

if 'ids_file' not in st.session_state:
    st.session_state.ids_file = None
 
# =========================================================================================================================
# Sidebar
# =========================================================================================================================

with st.sidebar:  

    st.session_state.ifc_file  = st.file_uploader("📥 Choose a IFC file", type=['ifc'])

    if st.session_state.ids is None:
        st.session_state.ids_file  = st.file_uploader("📥 Choose a IDS file", type=['ids']) 
    else:
        st.write('IDS file :' + st.session_state.ids)
# =========================================================================================================================
# main
# =========================================================================================================================

with st.container():


    st.title('Validate IFC Files')
    st.divider()

    if st.session_state.ifc_file is not None:
        
        ifc = ifcopenshell.open(st.session_state.ifc_file)
        my_ids = ids.open(st.session_state.ids_file, validate=True)
        report = reporter.Json(my_ids)
        st.write(report)
        
        #ids.Ids.validate()

        

        


