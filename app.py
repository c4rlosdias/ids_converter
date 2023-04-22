import pandas as pd
import requests
import streamlit as st
import datetime
from modules.ifctester import ids

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
                            l_prop.append(property['name'])
                            l_type.append(property['dataType'])
                            l_pset.append(property['propertySet'])
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

        my_bar.progress(1, text='Completed!')   

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


def graphql_search(domain):
    url = 'https://test.bsdd.buildingsmart.org/graphql'
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
    r = requests.post(url, json=payload)
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


st.set_page_config(
    page_title="IDS Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================================================================================
# System vars
# =========================================================================================================================

if 'mode' not in st.session_state:
    st.session_state.mode = None

if 'df' not in st.session_state:
    st.session_state.df = None

if 'file_name' not in st.session_state:
    st.session_state.file_name = None

if 'bsdd_loaded' not in st.session_state:
    st.session_state.bsdd_loaded = False

if 'bsdd_done' not in st.session_state:
    st.session_state.bsdd_done = False


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

# =========================================================================================================================
# Sidebar
# =========================================================================================================================

with st.sidebar:
    
    st.title('IDS Converter')
    st.image('./resources/img/LOGO 1X1_2.PNG', width=150)
    uploaded_file = st.file_uploader("📥 Choose a XLSX file", type=['xlsx'] )
    if uploaded_file is not None:
        st.session_state.mode='file'
    st.divider()

    submit = st.button('Connect to bSDD')
    if submit:
        st.session_state.bsdd_loaded = True
        
    if st.session_state.bsdd_loaded:
        response = requests.get('https://api.bsdd.buildingsmart.org/api/Domain/v3')
        if response.status_code == 200:
            domains = []
            for domain in response.json():
                domains.append(domain["name"] + ' ' + domain["version"])
                
            domain = st.selectbox('Select domain', domains)
            loaded = st.button('Load domain')
            if loaded:
                st.session_state.mode = 'bsdd'
                st.session_state.bsdd_done = False                   

    st.divider()
    st.image('./resources/img/github-logo.png', width=50)
    st.write('https://github.com/c4rlosdias/ids_converter')

# =========================================================================================================================
# If file loaded or bSDD connection
# =========================================================================================================================

if st.session_state.mode is not None:

    with st.container():

        # Create Dataframe

        if st.session_state.mode == 'bsdd':            
            st.session_state.df = properties_search(domain, response.json()) if not st.session_state.bsdd_done  else st.session_state.df
            st.session_state.file_name = domain + '.ids' 
            st.session_state.bsdd_done = True

        if st.session_state.mode == 'file':           
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
                        if row['have restriction'] == 'True' and row['property value'] is not '':
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

                result = my_ids.to_string()

                if result:
                    st.balloons()
                    st.download_button('Download IDS file', result, file_name=st.session_state.file_name, mime='xml')

                else:
                    st.error('ERRO : File not created!')

# =========================================================================================================================
# Introduction screen
# =========================================================================================================================
else:
    st.header("IDS Converter")
    st.write('_By Carlos Dias_') 
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
