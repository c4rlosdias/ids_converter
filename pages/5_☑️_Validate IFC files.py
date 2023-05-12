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

if 'ids' not in st.session_state:
    st.session_state.ids = None
 
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


    st.title('📝 Validate IFC Files')
    st.divider()

    if st.session_state.ifc_file is not None and st.session_state.ids_file is not None:
        ifc = ifcopenshell.file.from_string(st.session_state.ifc_file.getvalue().decode('utf-8'))
        my_ids = ids.open(st.session_state.ids_file)
      
        my_ids.validate(ifc)
        report = reporter.Json(my_ids).report()

        st.header('📋 Report:')
        st.write('Title : ' + report['title'])
        st.write('**:green[Specifications:]**')
      
        for r in report['specifications']:
            title1 = '✅' if r["status"] else '❌'
            title2 = f':green[Specification Name :]{r["name"]} : '
            title = title1 + title2

            with st.expander(title):
                st.write(f'Passed : {r["total_successes"]} / {r["total"]} ({r["percentage"]}%)')
                st.divider()
                for s in r['requirements']:                    
                    if s['status']:
                        st.write(f'⏺️ description : {s["description"]} : :green[PASS]')
                    else:
                        st.write(f'⏺️ description : {s["description"]} : :red[FAILED]')

                    if len(s['failed_entities']) > 0:

                        df = pd.DataFrame(s['failed_entities'])
                        st.write(df)
            


        


