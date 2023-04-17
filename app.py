import pandas as pd
import requests
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

if 'bsdd_loaded' not in st.session_state:
    st.session_state.bsdd_loaded = False

dic = {'specification name'        : ['My_spec_01', 'My_spec_01', 'My_spec_02'],
       'specification description' : ['Walls needs this properties', 'Walls needs this properties', 'Slabs needs area'],
       'entity'                    : ['IFCWALL', 'IFCWALL', 'IFCSLAB'],
       'predefined type'           : ['STANDARD', 'STANDARD', 'FLOOR'],
       'property name'             : ['IsExternal', 'LoadBearing', 'GrossArea'],       
       'property type'             : ['IFcBoolean', 'IfcBoolean', 'IfcAreaMeasure'],
       'property set'              : ['Pset_WallCommon', 'Pset_WallCommon', 'Pset_SlabCommom'],
       'property value'            : ['True', 'True', '[0-9]'],
       'have restriction'          : ['False', 'False', 'True'],
       'restriction base'          : ['string', 'string', 'string'],
       'optionality'               : ['required','optional', 'required']
       }

df_sample = pd.DataFrame(dic)
df_sample.set_index('specification name')

with st.sidebar:
    st.title('IDS Converter')
    st.image('./resources/img/LOGO 1X1_2.PNG', width=150)
    uploaded_file = st.file_uploader("📥 Choose a XLSX file", type=['xlsx'])
    st.divider()
    bsdd = st.button('Connect to bSDD')
    if bsdd:
        st.session_state.bsdd_loaded = True
    if st.session_state.bsdd_loaded:
        response = requests.get('https://test.bsdd.buildingsmart.org/api/Domain/v3')
        if response.status_code == 200:
            domains = []
            for domain in response.json():
                domains.append(domain["name"])

            domain = st.selectbox('Select domain', domains)
            

    st.divider()
    st.image('./resources/img/github-logo.png', width=50)    
    st.write('https://github.com/c4rlosdias/ids_converter')
    
#
# Se foi carregado um arquivo excel para conversão
#
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
        # Cria o DataFrame
        df = pd.read_excel(uploaded_file, dtype= str)
        df = df.fillna('')
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
                                'have restriction',
                                'restriction base',
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
                my_spec.applicability.append(ids.Entity(name=spec[2], predefinedType=None if spec[3] == '' else spec[3]))
                for index, row in frame.iterrows():
                    # insere requisito de propriedade
                    if row['have restriction'] == 'True' and row['property value'] is not '':
                        value = ids.Restriction(base=row['restriction base'], options={'pattern' : row['property value']})              
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
            
            result = my_ids.to_string()
            if result:
                st.balloons()
                st.download_button('Download IDS file', result, file_name=uploaded_file.name.split('.')[0] + '.ids', mime='xml')

#
# Se foi escolhido um domínio no bSDD
#
if st.session_state.bsdd_loaded:
    with st.container():
        st.write(domain)
     

else:
    st.image('./resources/img/ids-logo.png', width=100)
    st.markdown('™️')
    st.header("IDS Converter")
    st.write('_By Carlos Dias_')

    st.markdown('')
    st.markdown('IDS Converter converts a :green[Excel file] to :blue[IDS file].')
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
    st.markdown(':blue[_predefinedType_]            : predefined type of the elements to be checked (optional)')
    st.markdown(':blue[_property name_]             : requested property name (necessary)')
    st.markdown(':blue[_property type_]             : data type of the requested property (necessary)')
    st.markdown(':blue[_property set_]              : property set name (necessary)')
    st.markdown(':blue[_property value_]            : value requested in the property, when there is one (optional)')
    st.markdown(':blue[_have restriction_]          : if ''True'' then the property value is a pattern regular expression (RegExp) that needs to be matched by the property value (optional)')
    st.markdown(':blue[_restriction base_]          : data type of property value on restriction (optional)')
    st.markdown(':blue[_optionality_]               : property optionality, which can be :green[Required], :green[Optional], '+
                ' or :green[Prohibited] (necessary)')
 
    st.markdown('Example:')
    st.dataframe(df_sample)
    st.markdown('⚠️ Note that the same specification can occupy more than one row of the table!')
    st.markdown('')
    with open("./template/IDS_TEMPLATE.xlsx", "rb") as file:
        st.download_button('💾 Click here to download the template file!', data=file, file_name="IDS_TEMPLATE.xlsx")
    st.divider()

    st.markdown('☑️ Now, use the sidebar to upload your XLSX file! 👊')
    


    
