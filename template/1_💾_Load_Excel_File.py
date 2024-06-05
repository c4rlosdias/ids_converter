import pandas as pd
import streamlit as st
import datetime
from modules.ifctester import ids
from PIL import Image

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


if 'ids' not in st.session_state:
    st.session_state.ids = None

if 'df' not in st.session_state:
    st.session_state.df = None

if 'file_name' not in st.session_state:
    st.session_state.file_name = None


if 'convert' not in st.session_state:
    st.session_state.convert = False


# =========================================================================================================================
# Sidebar
# =========================================================================================================================

with st.sidebar:  

    uploaded_file = st.file_uploader("📥 Choose a XLSX file", type=['xlsx'])       

  

# =========================================================================================================================
# If file loaded 
# =========================================================================================================================

with st.container():
    
    
    # Create Dataframe

    if uploaded_file:

        st.session_state.convert = False
 
        st.session_state.df = pd.read_excel(uploaded_file, dtype=str)
        st.session_state.file_name=uploaded_file.name.split('.')[0] + '.ids'
           
        if st.session_state.df is not None:

            st.header('IDS Information')
            col1, col2 = st.columns(2, gap="large")
            with col1:
                title       = st.text_input('_Title:_')
                copyright   = st.text_input('_Copyright:_')
                version     = st.text_input('_Version:_')
                author      = st.text_input('_Author:_', 'xxxxx@xxxxx.xxx')
                ifc_version = st.selectbox('_IFC Version:_', ('IFC2X3', 'IFC4', 'IFC4X3'))

            with col2:
                date        = st.text_input('_Date:_', datetime.date.today())
                description = st.text_input('_Description:_')
                purpose     = st.text_input('_Purpose:_')
                milestone   = st.text_input('_Milestone:_')

            st.divider()
            st.markdown(':white_check_mark: :green[check your specifications:]')

            df = st.session_state.df.fillna('')
            df_group = df.groupby(['specification name', 'specification description', 'entity', 'predefined type'])

            for spec, frame in df_group:
                with st.expander(':green[Specification Name :]' + spec[0]):
                    st.markdown(f':green[Description:]{spec[1]}')
                    st.markdown('**APPLICABILITY:**')
                    st.write(f':green[Entity :]{spec[2]} - ',
                            f':green[Predefined Type :]{spec[3]}')
                    st.markdown('**REQUIREMENTS:**')
                    st.write(frame[['property name',
                                    'property type',
                                    'property set',
                                    'property value',
                                    'have restriction',
                                    'restriction base',
                                    'optionality']]
                    )

            st.divider()

            #
            # Convert dataframe to ids
            #
            submitted = st.button("Convert to IDS ▶️")
            if submitted:
                my_ids = ids.Ids(title=title,
                                copyright=copyright,
                                version=version,
                                author=author,
                                description=description,
                                date=date,
                                purpose=purpose,
                                milestone=milestone
                )
                for spec, frame in df_group:
                    my_spec = ids.Specification(name=spec[0], description=spec[1], ifcVersion=ifc_version)
                    my_spec.applicability.append(ids.Entity(name=spec[2], predefinedType=None if spec[3] == '' else spec[3]))
                    for index, row in frame.iterrows():
                        # add property requirement
                        if row['have restriction'] == 'True' and row['property value'] != '':
                            value = ids.Restriction(base=row['restriction base'], options={'pattern': row['property value']})
                        else:
                            value = None if row['property value'] == '' else row['property value']
                        property = ids.Property(
                            name=row['property name'],
                            value=value,
                            propertySet=row['property set'],
                            measure=row['property type'],
                            minOccurs=0 if row['optionality'].upper() in ['OPTIONAL', 'PROHIBITED'] else 1,
                            maxOccurs='unbounded' if row['optionality'].upper() in ['REQUIRED', 'OPTIONAL'] else 0
                        )

                        my_spec.requirements.append(property)
                        my_ids.specifications.append(my_spec)

                st.session_state.ids = my_ids.to_string()

                if st.session_state.ids:
                    st.session_state.convert = True                
                    st.balloons()
                else:
                    st.error('ERRO : File not created!')

            if st.session_state.convert and st.session_state.ids:
                st.download_button('📥 Download IDS file', st.session_state.ids, file_name=st.session_state.file_name, mime='xml')

    

