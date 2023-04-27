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
dic = {'specification name'       : ['My_spec_01', 'My_spec_01', 'My_spec_02'],
       'specification description': ['Walls needs this properties', 'Walls needs this properties', 'Slabs needs area'],
       'entity'                   : ['IFCWALL', 'IFCWALL', 'IFCSLAB'],
       'predefined type'          : ['STANDARD', 'STANDARD', 'FLOOR'],
       'property name'            : ['IsExternal', 'LoadBearing', 'GrossArea'],
       'property type'            : ['IFcBoolean', 'IfcBoolean', 'IfcAreaMeasure'],
       'property set'             : ['Pset_WallCommon', 'Pset_WallCommon', 'Pset_SlabCommom'],
       'property value'           : ['True', 'True', '[0-9]'],
       'have restriction'         : ['False', 'False', 'True'],
       'restriction base'         : ['string', 'string', 'string'],
       'optionality'              : ['required', 'optional', 'required']
       }

df_sample = pd.DataFrame(dic)
df_sample.set_index('specification name')

st.header("IDS Converter")
st.write('🇧🇷_By Carlos Dias_🇧🇷') 
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
st.markdown(':blue[_specification name_]        : Specification name or code (necessary)')
st.markdown(':blue[_specification description_] : Specification description (optional)')
st.markdown(':blue[_entity_]                    : ifc type of the elements to be checked (necessary)')
st.markdown(':blue[_predefined type_]           : predefined type of the elements to be checked (optional)')
st.markdown(':blue[_property name_]             : requested property name (necessary)')
st.markdown(':blue[_property type_]             : data type of the requested property (necessary)')
st.markdown(':blue[_property set_]              : property set name (necessary)')
st.markdown(':blue[_property value_]            : value requested in the property, when there is one (optional)')
st.markdown(':blue[_have restriction_]          : if ''True'' then the property value is a pattern regular expression (RegExp) that needs to be matched by the property value (optional)')
st.markdown(':blue[_restriction base_]          : data type of property value on restriction (optional)')
st.markdown(':blue[_optionality_]               : property optionality, which can be :green[Required], :green[Optional], or :green[Prohibited] (necessary)')
st.markdown('Example:')
st.dataframe(df_sample)
st.markdown('⚠️ Note that the same specification can occupy more than one row of the table!')
st.markdown('')
with open("./template/IDS_TEMPLATE.xlsx", "rb") as file:
    st.download_button('💾 Click here to download the template file!', data=file, file_name="IDS_TEMPLATE.xlsx")
st.divider()
st.markdown('☑️ Now, use the sidebar to upload your XLSX file! 👊')
