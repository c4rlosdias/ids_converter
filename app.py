import pandas as pd
import streamlit as st
import datetime
import ifcopenshell

st.set_page_config(
     page_title="IDS Converter",
     page_icon="🔄",
     layout="wide",
     initial_sidebar_state="expanded",
)

if True not in st.session_state:
    st.session_state.disabled = False

dic = {'specification name' : ['specifiation 01', 'specification 01', 'specification 02'],
       'specification description' : ['description of specification 01','description of specification 01','description of specification 02'],
       'specification instructions' : ['instructions 01', 'istructions 01', 'instructions 02'],
       'entity' : ['IFCWALL', 'IFCWALL', 'IFCDOOR'],
       'predefined type' : ['WALLSTANDARDCASE', 'WALLSTANDARDCASE', 'DOORSTANDARDCASE'],
       'property' : ['IsExternal', 'IsBearing', 'ssss'],       
       'property type' : ['IFcBoolean', 'IFCBoolean', 'IfcInteger'],
       'propertyset' : ['Pset_WallCommon', 'Pset_WallCommon', 'Pset_DoorCommom'],
       'property value' : ['True', 'True', '40'],
       'minOccurs' : [0 , 0, 0],
       'maxOccurs' : ['UnBounded','UnBounded', 'UnBounded' ]
       }

df_sample = pd.DataFrame(dic)
dic_sep = { 'TAB' : '\t',',' : ',', ';' : ';'}

with st.sidebar:
    st.title('IDS Converter')
    st.image('.\img\LOGO 1X1_2.PNG', width=150)
    st.write('_By Carlos Dias_')
    sep = st.selectbox('Choose separator:',('TAB', ',', ';'))
    st.divider()
    uploaded_file = st.file_uploader("Choose a CSV file", type=['csv'])
    

if uploaded_file is not None:

    with st.container():            
        st.header('IDS Information')
        col1, col2 = st.columns(2, gap="large")
        with col1:
            title       = st.text_input('_Title:_')
            copyright   = st.text_input('_Copyright:_')
            version     = st.text_input('_Version:_')
            author      = st.text_input('_Author:_', 'xxxxx@xxxxx.xxx')
            ifc_version = st.selectbox('_IFC Version:_', ('IFC2x3', 'IFC4', 'IFC4X3'))
                        
        with col2:
            date        = st.date_input('_Date:_', datetime.date.today())
            description = st.text_input('_Description:_')
            purpose     = st.text_input('_Purpose:_')
            milestone   = st.text_input('_Milestone:_')
    
    st.divider()

    with st.container():
        st.markdown(':white_check_mark: :green[check your specification:]')
        df = pd.read_csv(uploaded_file, sep=dic_sep[sep])
        st.dataframe(df, use_container_width=False)
    
    st.divider()
    

    submitted = st.button("Convert to IDS ▶️")        
    st.write("Title", title, "version", version) 

else:
    st.header("IDS Converter")
    st.write('_By Carlos Dias_')
    st.divider()
    st.markdown('IDS Conversor is a file format conversor by :green[CSV file] to :blue[IDS file].')
    st.markdown('the CSV file needs to have specific columns and in the correct order, as in the example below:')
    st.dataframe(df_sample)
    st.divider()
    st.markdown('Columns 1, 2 and 3 correspond to the name, description and instructions for a given specification. Note that several lines can be part of the same specification.')
    st.markdown('Columns 4 and 5 correspond to the applicability of the specification. What entities does this specification refer to.')
    st.markdown('All other columns correspond to information requirements that the entity needs to meet.')
    st.markdown('Now, use the sidebar to upload your CSV file')
    


    