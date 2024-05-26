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
    response = requests.get('https://api.bsdd.buildingsmart.org/api/Dictionary/v1/Classes', params)
    
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
                                l_desc.append(f'Objects with class: {code} MUST BE this properties')
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
        st.error('ERRO: ' + str(response.status_code) + 'for dictionary:' + domain)

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
    languages = requests.get(f'https://api.bsdd.buildingsmart.org/api/Language/v1')
    if languages.status_code == 200:
        l_lang = [k['name'] for k in languages.json()]
        language = st.selectbox('Select a Dictionary Language', l_lang) 



# =========================================================================================================================
# If file loaded or bSDD connection
# =========================================================================================================================

with st.container():
    # Search text    

    search_text = st.text_input('_Search Text:_')

    if search_text != '':
        response = requests.get(f'https://api.bsdd.buildingsmart.org/api/TextSearch/v1?SearchText={search_text}')

        # Show results
        if response.status_code == 200:
            response_json = response.json()
            total_count = response_json['totalCount']
            if total_count > 0:            
                classes = response_json['classes'] if 'classes' in response_json else None
                dictionaries = response_json['dictionaries'] if 'dictionaries' in response_json else None
                properties = response_json['properties'] if 'properties' in response_json else None
                st.write(dictionaries)
                df_classes = pd.DataFrame(classes)
                st.write(f'Total count: {total_count}')                
                ldic_names = [d['name'] for d in dictionaries]
                dict = st.selectbox('Select Dictionary', ldic_names)            
                uris = [d['uri'] for d in dictionaries if d['name'] == dict]
                st.write('Dictionary URI:')
                for uri in uris:
                    st.write(uri)

                if classes is not None:
                    classes = [ v for v in classes if v['dictionaryName'] == dict]
                    
                    if len(classes) > 0:
                        st.header('☑️ Classes:')
                        for classe in classes:
                            labelclass = f'{classe["name"] if "name" in classe else ""}'
                            with st.expander(labelclass): 
                                st.write(':green[Reference Code]: ' + classe["referenceCode"] if 'referenceCode' in classe else "") 
                                st.write(':green[Name]: ' + classe["name"] if 'name' in classe else "")                          
                                st.write(':green[Description]: ' + classe["description"] if 'description' in classe else "")
                                st.write(':green[Class Type]: ' + classe["classType"] if 'classType' in classe else  ""   )
                                st.write(':green[Parent Class]: ' + classe["parentClassName"] if 'parentClassName' in classe else "")
                                st.write(':green[URI]: ' + classe["uri"] if 'uri' in classe else "")


                if properties is not None:                
                    properties = [v for v in properties if v['dictionaryName'] == dict]
                    if len(properties) > 0:
                        
                        st.header('☑️ Properties:')
                        for property in properties:
                            with st.expander(property["name"]):                            
                                st.write(':green[Description]: ' + property["description"] if 'description' in property else "")
                                st.write(':green[URI]: ' + property["uri"] if 'uri' in property else "")
                                b = st.button('🔎'+ property['name'] + ' Details')
                                if b:
                                    lcode = [v['isoCode'] for v in languages.json() if v['name'] == language ]
                                    params = {'uri' : property['uri'], 'includeClasses' : True, 'languageCode' : lcode[0] }
                                    response = requests.get(f'https://api.bsdd.buildingsmart.org/api/Property/v4', params=params)
                                    
                                    details = response.json()
                                    st.write(f':blue[Name :] {details["name"]}' if 'name' in details else '')
                                    st.write(f':blue[Code :] {details["code"]}' if 'code' in details else '')
                                    st.write(f':blue[Datatype :] {details["dataType"]}' if 'datatype' in details else '')
                                    st.write(f':blue[Definition :] {details["definition"]}' if 'definition' in details else '')
                                    st.write(f':blue[Description :] {details["description"]}' if 'description' in details else '')
                                    st.write(f':blue[URI :] {details["uri"]}' if 'uri' in details else '')

                                    if 'propertyClasses' in details:
                                        st.subheader(':blue[Associated Classes:]')
                                        for prop_classes in details['propertyClasses']:    
                                            st.divider()                                    
                                            st.write(f':blue[Code :] {prop_classes["code"]}' if 'code' in prop_classes else '')
                                            st.write(f':blue[Name :] {prop_classes["name"]}' if 'name' in prop_classes else '')
                                            st.write(f':blue[URI :] {prop_classes["uri"]}' if 'uri' in prop_classes else '')
                                            st.write(f':blue[Definition :] {prop_classes["definition"]}' if 'definition' in prop_classes else '')
                                            st.write(f':blue[Description :] {prop_classes["description"]}' if 'description' in prop_classes else '')
                                            st.write(f':blue[Property Set :] {prop_classes["propertySet"]}' if 'propertySet' in prop_classes else '')
            else:
                st.info(f'⚠️ No occurrences of :blue[{search_text}] were found!')                            
                                        
                                


        else:
            st.error(f'ERRO: {str(response.status_code)} : {response.json()[""]}')
    else:
            st.write('Type a search text')




