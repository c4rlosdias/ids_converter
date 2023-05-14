import pandas as pd
import os
import os.path
import requests
import streamlit as st
import datetime
from modules.ifctester import ids
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
        l_prop, l_class, l_code, l_desc = [], [], [], []
        l_predefinetype, l_type, l_pset = [], [], []
        l_pvalue, l_haverestriction, l_restrictionbase, l_optionality = [], [], [], []

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
                            l_code.append(classe['referenceCode'])                            
                            l_predefinetype.append(None)
                            l_prop.append(property['name'] if 'name' in property else None)
                            l_type.append(property['dataType'] if 'dataType' in property else None)
                            l_pset.append(property['propertySet'] if 'propertySet' in property else None)
                            l_pvalue.append(property['pattern'] if 'pattern' in property else None)
                            if 'isRequired' in property:
                                l_optionality.append('required' if property['isRequired'] == True else 'optional')
                            else:
                                l_optionality.append('required')

                            if 'relatedIfcEntityNames' in classe:
                                l_class.append(classe['relatedIfcEntityNames'][0] if len(classe['relatedIfcEntityNames']) > 0 else None)
                                l_desc.append(f'The entity {classe["relatedIfcEntityNames"]} needs this properties')
                            else:
                                l_class.append('WARNING : NO IFC TYPE DEFINED')
                                l_desc.append('WARNING : NO IFC TYPE DEFINED')
                            if 'pattern' in property:
                                l_haverestriction.append(True if property['pattern'] else False)
                                l_restrictionbase.append('string' if property['pattern'] else None)
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
# get bSDD data with graphql - [!] not working in production enviroment
# =========================================================================================================================

@st.cache_data
def graphql_search(domain):
    url = 'https://api.bsdd.buildingsmart.org/graphql'
    namespaceUri = search_json(domain, "namespaceUri", response.json())
    query_todo = f'''{{domain(namespaceUri: "{namespaceUri}") {{
                            name
                            namespaceUri
                            classificationSearch {{
                                code
                                name
                                namespaceUri
                                relatedIfcEntityNames
                                properties {{
                                        propertySet
                                        name
                                        namespaceUri
                                        isRequired
                                        dataType
                                        pattern
                                        units
                                }}
                            }}
                        }}
                    }}'''

    payload = {'query': query_todo}
    r = requests.post(url, json= payload)
    st.write(r.status_code)

    if r.status_code == 200:

        classifications = r.json()['data']['domain']['classificationSearch']
        l_prop, l_class, l_code, l_desc = [], [], [], []
        l_entity, l_predefinetype, l_type, l_pset = [], [], [], []
        l_pvalue, l_haverestriction, l_restrictionbase, l_optionality = [], [], [], []

        for classification in classifications:
            properties = classification['properties']
            if len(properties) > 0:
                for property in properties:
                    l_code.append(classification['code'])
                    l_desc.append(f'The entity {classification["relatedIfcEntityNames"]} needs properties')
                    l_entity.append(classification['relatedIfcEntityNames'])
                    l_predefinetype.append(None)
                    l_prop.append(property['name'])
                    l_type.append(property['dataType'])
                    l_pset.append(property['propertySet'])
                    l_pvalue.append(property['pattern'])
                    l_haverestriction.append(True if property['pattern'] else False)
                    l_restrictionbase.append('string' if property['pattern'] else None)
                    l_optionality.append('required' if property['isRequired'] == True else 'optional')
                    if len(classification['relatedIfcEntityNames']) > 0:
                        l_class.append(classification['relatedIfcEntityNames'][0])
                    else:
                        l_class.append(None)

        dic = {'specification name'         : l_code,
               'specification description'  : l_desc,
               'property name'              : l_prop,
               'entity'                     : l_class,
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
        st.error('⚠️ ERROR : Something wrong!')
        result = None

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
    st.title('IDS Converter')
    st.image('./resources/img/LOGO 1X1_2.PNG', width=150)
    st.write('Choose a option above:')
    st.divider()
    st.image('./resources/img/github-logo.png', width=50)
    st.write('https://github.com/c4rlosdias/ids_converter')    
     

# =========================================================================================================================
# If file loaded or bSDD connection
# =========================================================================================================================



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
        date        = st.date_input('_Date :_', datetime.date.today()) 
        description = st.text_input('_Description:_')
        purpose     = st.text_input('_Purpose:_')
        milestone   = st.text_input('_Milestone:_')

    st.divider()

    st.markdown(':white_check_mark: :green[Create your specifications:]')


container_specs = st.container()

facets = {'Entity'         : ['IFC Class', 'PredefinedType'],
          'Attribute'      : ['Name', 'Value'],
          'Classification' : ['System', 'Value'],
          'Property'       : ['Property Set', 'Name', 'Value'],
          'Material'       : ['Value'],
          'Parts'          : ['Entity', 'Relationship']
}

with container_specs:
    col3, col4 = st.columns(2)

    with col3:
        st.subheader('**Applicability**')
        options_app = st.multiselect('Choose the facets to applicability :', ['Entity', 'Attribute', 'Classification', 'Property', 'Material', 'Parts'], key='app')
        for facet in options_app:
            st.write(f'**{facet}**')            
            cols1 = st.columns(len(facets[facet]))
            c = 0
            for att in facets[facet]:
                with cols1[c]:
                    st.text_input(f':blue[{att}]', key='app' + facet + att)
                c += 1

    with col4:
        st.subheader('**Requirements**')
        options_req = st.multiselect('Choose facets to requirements:', ['Entity', 'Attribute', 'Classification', 'Property', 'Material', 'Parts'], key='req')
        for facet in options_req:
            st.write(f'**{facet}**')
            cols2 = st.columns(len(facets[facet]))
            c = 0
            for att in facets[facet]:
                with cols2[c]:
                    if att == 'Value':
                        op = st.radio(':green[Value]', ['Simple Value','Pattern restriction', 'Enumeration restriction'], key='req' + facet + att, horizontal=True)
                        st.text_input(op, key='breq' + facet + att)
                    else:
                        st.text_input(f':green[{att}]', key='req' + facet + att)
                c += 1

    st.divider()  





        





