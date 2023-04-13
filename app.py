import pandas as pd
import re
import streamlit as st
import datetime
import ifcopenshell
from modules.ifctester import ids

st.set_page_config(
     page_title="IDS Converter",
     page_icon="🔄",
     layout="wide",
     initial_sidebar_state="expanded",
)

if True not in st.session_state:
    st.session_state.disabled = False

dic = {'specification name' : ['SPEC_01', 'SPEC_01', 'SPEC_02'],
       'specification description' : ['Walls needs this properties', 'Walls needs this properties', 'Slabs needs area'],
       'entity' : ['IFCWALL', 'IFCWALL', 'IFCSLAB'],
       'predefined type' : ['STANDARD', 'STANDARD', 'FLOOR'],
       'property name' : ['IsExternal', 'LoadBearing', 'GrossArea'],       
       'property type' : ['IFcBoolean', 'IFCBoolean', 'IfcAreaMeasure'],
       'property set' : ['Pset_WallCommon', 'Pset_WallCommon', 'Pset_SlabCommom'],
       'property value' : ['True', 'True', '[0-9]'],
       'restriction' : ['F', 'F', 'T'],
       'optionality' : ['Required','Optional', 'Prohibited' ]
       }

df_sample = pd.DataFrame(dic)
df_sample.set_index('specification name')
dic_sep = { 'TAB' : '\t',',' : ',', ';' : ';'}

with st.sidebar:
    st.title('IDS Converter')
    st.image('./resources/img/LOGO 1X1_2.PNG', width=150)
    st.write('_By Carlos Dias_')
    sep = st.selectbox('Choose separator:',('TAB', ',', ';'))
    st.divider()
    uploaded_file = st.file_uploader("📥 Choose a CSV file", type=['csv'])
    st.divider()
    st.image('./resources/img/github-logo.png', width=50)    
    st.write('https://github.com/c4rlosdias/ids_converter')
    

if uploaded_file is not None:

    with st.container():            
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
    st.write(ifc_version)

    with st.container():
        st.markdown(':white_check_mark: :green[check your specifications:]')
        df = pd.read_csv(uploaded_file, sep=dic_sep[sep], keep_default_na=False)
        df_group = df.groupby(['specification name', 'specification description','entity', 'predefinedType'])

        for spec, frame in df_group:
            
            with st.expander(':green[Specification Name :]' + spec[0]):
                st.markdown(f':green[Description:]{spec[1]}')
                st.markdown('**APPLICABILITY:**')
                st.write(f':green[Entity :]{spec[2]} - ', f':green[PredefinedType :]{spec[3]}')
                st.markdown('**REQUIREMENTS:**')
                st.write(frame[['property name',
                                'property type',
                                'property set',
                                'property value',
                                'restriction',
                                'optionality']]
                )

        st.divider()

        # Conversao
        submitted = st.button("Convert to IDS ▶️")    
        if submitted:
            my_ids= ids.Ids(title=title, 
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
                my_spec.applicability.append(ids.Entity(name=spec[2], predefinedType=None if spec[3] == '' else spec[2]))
                for index, row in frame.iterrows():
                    # insere requisito de propriedade
                    property = ids.Property(
                        name=row['property name'],
                        value=None if row['property value']=='' else ids.Restriction(base="string", options= {'pattern' : row['property value']}) if row['restriction']=='T' else row['property value'],
                        propertySet=row['property set'],
                        measure=row['property type'],
                        minOccurs=0 if row['optionality'].upper() in ['OPTIONAL', 'PROHIBITED'] else 1,
                        maxOccurs='unbounded' if row['optionality'].upper() in ['REQUIRED', 'OPTIONAL'] else 0 
                    )
                    
                    my_spec.requirements.append(property)
                my_ids.specifications.append(my_spec)
           
            result = my_ids.to_string()
            if result:
                st.balloons()
                st.download_button('Download IDS file', result, file_name=uploaded_file.name.split('.')[0] + '.ids', mime='xml')


     

else:
    st.image('./resources/img/ids-logo.png', width=100)
    st.markdown('™️')
    st.header("IDS Converter")
    st.write('_By Carlos Dias_')

    st.markdown('')
    st.markdown('IDS Converter converts a :green[CSV file] to :blue[IDS file].')
    st.markdown('IDs is a standard that describes information exchange requirements and has incredible potential. ' +
                'This converter, however, serves to create an ids with simple specifications, capable of indicating' + 
                ' which properties and values the model needs to have for each ifc type')
    
    st.divider()
    st.markdown('the CSV file needs to have specific columns described bellow:')
    st.markdown(':blue[_specification name_] -> Specification name or code (necessary)')
    st.markdown(':blue[_specification description_] -> Specification description (optional)')
    st.markdown(':blue[_entity_] -> ifc type of the elements to be checked (necessary)')
    st.markdown(':blue[_predefinedType_] -> predefined type of the elements to be checked (optional)')
    st.markdown(':blue[_property name_] -> requested property name (necessary)')
    st.markdown(':blue[_property type_] -> data type of the requested property (necessary)')
    st.markdown(':blue[_property set_] -> property set name (necessary)')
    st.markdown(':blue[_property value_] -> value requested in the property, when there is one (optional)')
    st.markdown(':blue[_restriction_] -> if ''T'' then the property value is a regular expression (RegExp) that needs to be matched by the property value')
    st.markdown(':blue[_optionality_] -> property optionality, which can be :green[Required], :green[Optional], '+
                ' or :green[Prohibited] (necessary)')
    st.markdown('Example:')
    st.dataframe(df_sample)
    st.markdown('⚠️ Note that the same specification can occupy more than one row of the table!')
    st.divider()

    st.markdown('☑️ Now, use the sidebar to upload your CSV file! 👊')
    


    