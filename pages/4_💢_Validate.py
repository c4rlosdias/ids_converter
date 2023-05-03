import streamlit as st
import ifcopenshell
import pandas as pd
from PIL import Image
from modules.ifctester import ids, reporter
from io import StringIO

def reload_ids():
    st.session_state.ids = None
    st.session_state.ids_file = None
    return True
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

    if st.session_state.ids is not None:
        st.session_state.ids_file  = st.session_state.ids
        st.write('IDS loaded!')
        st.button('Reload IDS', on_click=reload_ids)
    else:
        idsFile  = st.file_uploader("📥 Choose a IDS file", type=['ids'])
        if idsFile:
            st.session_state.ids_file = idsFile.getvalue().decode('utf-8')
    
# =========================================================================================================================
# main
# =========================================================================================================================

with st.container():


    st.title('Validate IFC Files')
    st.divider()

    if st.session_state.ifc_file is not None and st.session_state.ids_file is not None:
        st.write(st.session_state.ifc_file)
        ifc = ifcopenshell.file.from_string(st.session_state.ifc_file.getvalue().decode('utf-8'))
        my_ids = ids.open(st.session_state.ids_file)
      
        my_ids.validate(ifc)
        report = reporter.Json(my_ids).report()

        st.write(report)

        

        for r in report['specifications']:
            df = pd.DataFrame(r)
            st.write(df)

        
        

        


