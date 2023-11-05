import pandas as pd
import os
import os.path
import requests
import streamlit as st
import datetime
from ifctester import ids
from PIL import Image



# =========================================================================================================================
# search namespace 
# =========================================================================================================================
def search_json(search, value, json):
    result = None
    for e in json:
        if e['name']+' '+e["version"] == search:
            result = e[value]
    return result

# =========================================================================================================================
# get bSDD data
# =========================================================================================================================
@st.cache_data
def properties_search(domain, json):
    namespaceUri = search_json(domain, "namespaceUri", json)
    params = {'namespaceUri' : namespaceUri, 'useNestedClassifications' : 'false'}
    response = requests.get('https://api.bsdd.buildingsmart.org/api/Domain/v3/Classifications', params)

    result = None
    
    if response.status_code == 200:
        l_prop, l_class, l_code, l_desc, l_mat          = [], [], [], [], []
        l_predefinetype, l_type, l_pset, l_optionality  = [], [], [], []
        l_pvalue, l_haverestriction, l_restrictionbase = [], [], []

        classifications = response.json()['classifications']
        progress_text = "Operation in progress. Please wait."
        my_bar = st.progress(0, text=progress_text)
        percent_complete = 0
        increment = 1 / len(classifications)
        #increment = 1 if increment < 1 else increment
        for classification in classifications:
            params2 = {'namespaceUri' : classification['namespaceUri'], 'includeChildClassificationReference' : 'false'}
            response2 = requests.get('https://api.bsdd.buildingsmart.org/api/Classification/v3', params2)            
            if response2.status_code == 200:
                classe = response2.json()
                if 'classificationProperties' in classe:
                    class_properties = classe['classificationProperties']
                    if len(class_properties) > 0:
                        for property in class_properties:
                            my_bar.progress(percent_complete if percent_complete < 1 else 1, text=progress_text)                            
                            material = None
                            if 'classificationRelations' in classe:
                                relations = classe['classificationRelations']
                                code = classe['referenceCode'] if 'referenceCode' in classe else  classe['code']
                                if len(relations) > 0:
                                    for relation in relations:
                                        if relation['relationType'] == 'HasMaterial':
                                            material = relation['relatedClassificationName']
                            l_mat.append(material)                        
                            l_code.append(code)
                            l_predefinetype.append(None)
                            l_prop.append(property['name'] if 'name' in property else None)
                            l_type.append(property['dataType'] if 'dataType' in property else None)
                            l_pset.append(property['propertySet'] if 'propertySet' in property else None)
                            l_pvalue.append(property['predefinedValue'] if 'predefinedValue' in property else None)
                            if 'isRequired' in property:
                                l_optionality.append('required' if property['isRequired'] == True else 'optional')
                            else:
                                l_optionality.append('required')

                            if 'relatedIfcEntityNames' in classe:
                                l_class.append(classe['relatedIfcEntityNames'][0] if len(classe['relatedIfcEntityNames']) > 0 else None)
                                l_desc.append(f'Class {code}  - {classe["definition"]}')
                            else:
                                l_class.append('WARNING : NO IFC TYPE DEFINED')
                                l_desc.append('WARNING : NO IFC TYPE DEFINED')
                            if 'pattern' in property:
                                l_haverestriction.append(True)
                                l_restrictionbase.append(property['dataType'])
                            else:
                                l_haverestriction.append(False)
                                l_restrictionbase.append(None)            
            else:
                st.error('ERRO: ' + str(response2.status_code) + ' for classification:' + classification['name'])
            
            percent_complete = percent_complete + increment

        my_bar.progress(100, text='Completed!')   

        dic = {'specification name'         : l_code,
               'specification description'  : l_desc,
               'property name'              : l_prop,
               'entity'                     : l_class,
               'material'                   : l_mat,
               'predefined type'            : l_predefinetype,
               'property name'              : l_prop,
               'property type'              : l_type,
               'property set'               : l_pset,
               'property value'             : l_pvalue,
               'have restriction'           : l_haverestriction,
               'restriction base'           : l_restrictionbase,
               'optionality'                : l_optionality
        }
        df = pd.DataFrame(dic)
        result = df    

    else:
        st.error('ERRO: ' + str(response.status_code) + 'for domain:' + domain)

    return result
            

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

if 'df' not in st.session_state:
    st.session_state.df = None

if 'ids' not in st.session_state:
    st.session_state.ids = None

if 'file_name' not in st.session_state:
    st.session_state.file_name = None

if 'domains' not in st.session_state:
    st.session_state.domains = []

if 'response' not in st.session_state:
    st.session_state.response = None

if 'loaded' not in st.session_state:
    st.session_state.loaded = None

if 'domain_active' not in st.session_state:
    st.session_state.domain_active = ''


# =========================================================================================================================
# Sidebar
# =========================================================================================================================

with st.sidebar:
    if not st.session_state.response:
        response = requests.get('https://api.bsdd.buildingsmart.org/api/Domain/v3')
        if response.status_code == 200:
            st.session_state.response = response.json()
            domains = []
            for domain in st.session_state.response:
                if domain['status'] != 'Inactive':
                    domains.append(domain["name"] + ' ' + domain["version"]) 
            domains.sort()
            st.session_state.domains = domains
            
                    
    domain = st.selectbox('Select domain', st.session_state.domains)
    loaded = st.button('Load domain')
    if loaded:
        st.session_state.loaded = True
        st.session_state.domain_active = domain
     

# =========================================================================================================================
# If file loaded or bSDD connection
# =========================================================================================================================

if st.session_state.loaded:
    with st.container():

        # Create Dataframe

        if loaded:
            st.session_state.df = properties_search(domain, st.session_state.response)

        st.session_state.file_name = domain + '.ids' 
        
        if st.session_state.df is not None:
            st.title('Domain: ' + st.session_state.domain_active)
            st.divider()
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
            df_group = df.groupby(['specification name', 'specification description', 'entity', 'predefined type', 'material'])
            
            for spec, frame in df_group:
                with st.expander(':green[Specification Name : ]' + spec[0]):
                    st.markdown(f':green[Description: ]{spec[1]}')
                    st.markdown('**APPLICABILITY:**')
                    st.write(f':green[Entity :]{spec[2]}')
                    if spec[3] != '':
                        st.write(f':green[with Predefined Type : ]{spec[3]}')
                    if spec[4] is not None:
                        st.write(f':green[with material : ]{spec[4]}')
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
                my_spec = ids.Specification(name=spec[0], description=spec[0], ifcVersion=ifc_version)
                my_spec.applicability.append(ids.Entity(name=spec[2], predefinedType=None if spec[3] == '' else spec[3]))
                my_spec.applicability.append(ids.Classification(value=spec[0]))
                my_spec.applicability.append(ids.Material(value=spec[4]))                
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
                        datatype=row['property type'],
                        minOccurs=0 if row['optionality'].upper() in ['OPTIONAL', 'PROHIBITED'] else 1,
                        maxOccurs='unbounded' if row['optionality'].upper() in ['REQUIRED', 'OPTIONAL'] else 0
                    )

                    my_spec.requirements.append(property)
                    my_ids.specifications.append(my_spec)

            st.session_state.ids = my_ids.to_string()
            if st.session_state.ids is not None:       
                st.download_button('📥 Download :blue[IDS file]', st.session_state.ids, file_name=st.session_state.file_name, mime='xml')
                st.session_state.df.to_excel('temp.xlsx', index=False)
                if os.path.isfile('temp.xlsx'):
                    with open('temp.xlsx', 'rb') as file:
                        st.download_button('📥 Download :blue[XLSX file]', file, file_name=st.session_state.file_name.split('.')[0].strip() + '.xlsx', mime='xlsx' )
            else:
                st.error('ERRO : File not created!')

