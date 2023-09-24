import streamlit as st
from PIL import Image
import pandas as pd

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
# Sidebar
# =========================================================================================================================

with st.sidebar:
    
    st.title('IDS Converter')
    st.image('./resources/img/LOGO 1X1_2.PNG', width=150)
    st.write('Choose a option above:')
    st.divider()
    st.image('./resources/img/github-logo.png', width=50)
    st.write('https://github.com/c4rlosdias/ids_converter')

# =========================================================================================================================
# Introduction screen
# =========================================================================================================================

st.header("IDS Converter")
st.write('By Carlos Dias') 
st.markdown('')
st.markdown('IDS Converter generates an :blue[IDS file] from an :green[Excel file] or properties in a :green[buildingsmart data dictionary (bSDD)] domain.')
st.markdown('')
st.image('./resources/img/schema.png', width=450)
st.markdown('')
st.markdown('IDs is a standard that describes information exchange requirements and has incredible potential. ' +
            'This converter, however, serves to create an ids with simple specifications, capable of indicating' +
            ' which properties and values the model needs to have for each ifc type')
st.markdown('')
st.markdown('_IDS Converter uses [IfcOpenShell](http://ifcopenshell.org/)_')
st.divider()
st.markdown('the Excel file needs to have specific columns described bellow:')
st.write('SPECIFICATION sheet:') 
st.image('./resources/img/sheet1.png', width=500)
st.write('APPLICABILITY sheet:') 
st.image('./resources/img/sheet2.png', width=1500)
st.write('REQUIREMENTS sheet:') 
st.image('./resources/img/sheet3.png', width=1500)

st.markdown('⚠️ Note that the same specification can occupy more than one row of the table!')
st.markdown('')
with open("./template/IDS_TEMPLATE.xlsx", "rb") as file:
    st.download_button('💾 Click here to download the template file!', data=file, file_name="IDS_TEMPLATE.xlsx")
st.divider()
st.markdown('☑️ Now, use the sidebar to upload your XLSX file! 👊')
