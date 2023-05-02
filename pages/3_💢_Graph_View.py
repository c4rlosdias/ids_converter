import pandas as pd
import streamlit as st
import networkx as nx
import streamlit.components.v1 as components
from pyvis.network import Network
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

if 'df' not in st.session_state:
    st.session_state.df = None

  

# =========================================================================================================================
# If file loaded or bSDD connection
# =========================================================================================================================

with st.container():

    # Create Dataframe

    st.title('Network Graph Visualization of Specifications')
    st.divider()

    if st.session_state.df is not None:
        
        df = st.session_state.df.reset_index(drop=True)
        st.session_state.df = None

        #G = nx.from_pandas_edgelist(df, 'specification name', 'entity', 'property set')
        G = nx.Graph()
        for index, row in df.iterrows():

            specification = row['specification name']
            entity = specification + '.' + row['entity']
            pset = entity + '.' + row['property set']
            prop = pset + '.' + row['property name']

            G.add_edge('Specifications', specification)
            G.add_edge(specification, entity)
            G.add_edge(entity, pset)
            G.add_edge(pset, prop)

        prop_net = Network(height='800px', bgcolor='#222222', font_color='white')

        prop_net.from_nx(G)
        prop_net.repulsion(node_distance=420, central_gravity=0.33,
                            spring_length=110, spring_strength=0.10,
                            damping=0.95)
        path = './resources/html/'
        prop_net.save_graph(f'{path}pyvis_graph.html')
        HtmlFile = open(f'{path}pyvis_graph.html', 'r', encoding='utf-8')
        components.html(HtmlFile.read(), height=800)
    else:
        st.write('No specifications readed')

        


