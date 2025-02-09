import ifcopenshell
import streamlit as st
from plantuml import PlantUML
import base64
import os
from PIL import Image

# =========================================================================================================================
# page config
# =========================================================================================================================

im = Image.open('./resources/img/IDS_logo.ico')
st.set_page_config(
    page_title="IFC Instance Graph",
    page_icon=im,
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================================================================================
# system variables
# =========================================================================================================================

if 'ifc_file' not in st.session_state:
    st.session_state.ifc_file = None


# =========================================================================================================================
# functions
# =========================================================================================================================

# Função para salvar a string UML em um arquivo
def salve_uml(uml_code, file_path):
    with open(file_path, 'w') as file:
        file.write(uml_code)

# Função para renderizar o código PlantUML a partir de um arquivo
def render_arq_uml(file_path):
    plantuml = PlantUML(url="http://www.plantuml.com/plantuml/img/")
    with open(file_path, 'r') as file:
        uml_code = file.read()
    #response = plantuml.processes_file(file_path)
    response = plantuml.processes(uml_code)
    return response

# Função para gerar o diagrama UML
def render_uml(uml_code):
    plantuml_url = "http://www.plantuml.com/plantuml/img/"
    plantuml = PlantUML(url=plantuml_url)
    response = plantuml.processes(uml_code)
    return response

# Generate class puml
def print_class(element : ifcopenshell.entity_instance, level:int) -> str:
    info = element.get_info() 
    str_object = f"\nmap ID{info['id']}_{element.is_a()}{{\n"
    relation = []
    restante = ''
    global count
    # for each attribute

    count += 1  
    for key, value in info.items():   
        if key not in ['id', 'type']:         
           
           # if value is a entity         
           if isinstance(value,ifcopenshell.entity_instance):
               if count < level:
                    rest, rel = print_class(value, level)
                    str_object += f"\t{key}=>\n"                    
                    restante += f"\n{rest}"
                    relation.append(f"ID{info['id']}_{element.is_a()}::{key} --> ID{value.id()}_{value.is_a()}")
                    relation.extend(rel)
               else:
                    str_object += f"\t{key}=>ID{str(value)[1:]}\n"
                
               
           # if value is a tuple
           elif isinstance(value, tuple):  
                if isinstance(value[0], ifcopenshell.entity_instance):
                   if count < level:
                        str_object += f"\t{key} =>\n"
                        for object in value:
                            rest, rel = print_class(object, level)
                            restante += f"\n{rest}"
                            relation.append(f"ID{info['id']}_{element.is_a()}::{key} --> ID{object.id()}_{object.is_a()}")
                            relation.extend(rel)    
                   else:
                        str_object += f"\t{key}=>{str(value)}\n"                            
                else:
                   str_object += f"\t{key} => {value}\n" 
                   
           # if value is a simple value
           else:
                str_object += f"\t{key} => {value}\n"
    
    str_object += f"}} {restante}" 
        
    return str_object, relation

# =========================================================================================================================
# main
# =========================================================================================================================


# Título da aplicação
st.title("IFC to UML")
  
st.session_state.ifc_file = st.file_uploader("Choose a IFC file", type=['ifc']) 

if st.session_state.ifc_file is not None: 
    try:
        global count
        model = ifcopenshell.file.from_string(st.session_state.ifc_file.getvalue().decode('utf-8')) 
        project = model.by_type('IfcProject')[0]
        site = model.by_type('IfcSite')[0]
        st.write(f"IfcProject : #{project.id()}")
        st.write(f"IfcSite    : #{site.id()}")
        ids = st.text_input("Enter the object IDs") 
        c1, c2 = st.columns(2)
        with c1: 
            level = st.selectbox(
                "Maximum number of objects",
                (
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "10",
                    "11",
                    "12",
                    "13"
                )
            )
        with c2:
            theme = st.selectbox(
                "Theme",
                (
                    "none",
                    "amiga",
                    "black-knight",
                    "hacker",
                    "bluegray",
                    "blueprint",                    
                    "cyborg",
                    "lightgray",
                    "mimeograph",
                    "reddress-darkred",
                    "sandstone",
                    "sketchy",
                    "scketchy-outline",
                    "spacelab"
                )
            )
        l_relations = []
        str_relations = """ """
        if ids != "":
            l_ids = ids.split()
            elements = [model.by_id(int(e.strip())) for e in l_ids]

            with st.container(border=True): 
                str_puml = f"@startuml\n" if theme=='none' else f"@startuml\n!theme {theme}\n"
                for element in elements:   
                    count = 0                   
                    object, l_relation = print_class(element, int(level))
                    str_puml += object
                    l_relations += l_relation

                # add relations
                for r in l_relations:
                    str_relations +=  f"\n{r}"
                str_puml += str_relations + "\n\n@enduml"
               
                # render graph                
                graph = render_uml(str_puml)
                st.image(graph)
                
                    
    except Exception as ex:
        st.error(f'ERROR: {ex}')
