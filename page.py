import streamlit as st

from utils import *
import folium
from folium.plugins import Draw

st.set_page_config(
    page_title="Главная страница",
    page_icon="📚",
)

colors = ['green', 'red', 'purple', 'black', 'blue']
types = ['length', 'cost', 'time']

hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)
st.image('logo.png', width=700)
st.header('РУСАЛ')

col1, col2 = st.columns(2)
with col1:
    nodes = st.file_uploader('Загрузите таблицу с заводами', type='csv')
with col2:
    edges = st.file_uploader('Загрузите таблицу с маршрутами', type='csv')

if nodes and edges:
    nodes = file_to_df(nodes)
    edges = file_to_df(edges)

    m = folium.Map(location=[59.75968,60.19503], zoom_start=3)

    Draw(export=True).add_to(m)
    
    counter = 0
    for i in range(len(nodes)):
        text = nodes['Name'].iloc[i]
        node_type = nodes['Type'].iloc[i]
        location = [nodes['lat'].iloc[i], nodes['lon'].iloc[i]]
        if node_type == 'Склад':
            color = 'blue'
        else: 
            color = colors[counter]
            counter += 1
        icon = 'industry' if node_type == 'Склад' else 'train'
        folium.Marker(
            location=location,
            popup=folium.Popup(text, parse_html=True, max_width="100%"),
            icon=folium.Icon(color=color,  icon=icon, prefix='fa')
        ).add_to(m)
    place = []
    place.append(st.empty())
    place[-1]._html(m._repr_html_(), width=700, height=500)
    

    with st.sidebar:
        names = get_nodes(nodes)
        sups = get_sup(nodes)
        graph_dict = {}
        for sup in sups:
            graph_dict[sup] = fill_graph(nodes, edges)
            for bad_sup in [s for s in sups if s!=sup]:
                graph_dict[sup].remove_node(bad_sup)

        # G = fill_graph(nodes, edges)
        sup_lst = []
        st.subheader('Выберите поставщиков')
        for i in range(len(sups)):
            sup_lst.append(st.checkbox(sups[i], value=True))
        
        # path_type = st.radio('Выберите оптимальный маршрут', ('Самый короткий маршрут', 'Самый бюджетный маршрут', 'Самый быстрый маршрут'))
        end = st.selectbox('Выберите пункт прибытия', names)

        # length_button = st.button('Самый короткий маршрут')
        
        # cost_button = st.button('Самый бюджетный маршрут')

        # time_button = st.button('Самый быстрый маршрут')
    
    shortest_dict = {}
    sup_color = {}
    for type_ in types:
        for i in range(len(sups)):
            start = sups[i]
            if nx.has_path(graph_dict[start], start, end):
                if sup_lst[i]:
                    shortest_path = nx.shortest_path(graph_dict[start], start, end, type_)
                    shortest_path_length = nx.shortest_path_length(graph_dict[start], start, end, type_)
                    to_show, to_draw = cut_edges(nodes, edges, shortest_path)
                    sup_color[start] = colors[i]
                    # if type_ == 'length':
                    #     st.write(colors[i])
                    #     folium.vector_layers.PolyLine(get_lan_lon(nodes, to_draw), dash_array='10', color=colors[i]).add_to(m)
                    if type_ not in shortest_dict.keys():
                        shortest_dict[type_] = [shortest_path_length, shortest_path, to_show, to_draw]
                    else:
                        if shortest_path_length < shortest_dict[type_][0]:
                            shortest_dict[type_] = [shortest_path_length, shortest_path, to_show, to_draw]
            # else:
                # st.warning('Данного маршрута нет')
    place[-1]._html(m._repr_html_(), width=700, height=500)
    try:
        
        # if path_type == 'Самый короткий маршрут':
    
        shortest_path_length, shortest_path, to_show, to_draw = shortest_dict['length']
        # place[-1]._html(m._repr_html_(), width=700, height=500)
        st.subheader('Самый короткий маршрут')
        col3 , col4, col5 = st.columns([1, 1, 2])
        with col3:
            st.metric('Расстояние, км', shortest_path_length)
        with col4:
            st.metric('Стоимость, руб', to_show['Стоимость'].sum())
        with col5:
            # st.metric('Время', convert_minutes(to_show['Время'].apply(convert_time).sum()))
            st.metric('Время', str(to_show['Время'].sum())  + ' дней')
        to_show.index = range(len(to_show))
        st.dataframe(to_show, width=700)
        length_but = st.button('Показать на карте', key=1)
        if length_but: 
            folium.vector_layers.PolyLine(get_lan_lon(nodes, to_draw), dash_array='10', color=sup_color[shortest_path[0]]).add_to(m)
            place[-1]._html(m._repr_html_(), width=700, height=500)

        st.subheader('Самый бюджетный маршрут')
        col6 , col7, col8 = st.columns([1, 1, 2])
        # if path_type == 'Самый бюджетный маршрут':
        shortest_path_length, shortest_path, to_show, to_draw = shortest_dict['cost']
        # folium.vector_layers.PolyLine(get_lan_lon(nodes, to_draw), dash_array='10', color=sup_color[shortest_path[0]]).add_to(m)
        # place[-1]._html(m._repr_html_(), width=700, height=500)
        with col6:
            st.metric('Расстояние, км', to_show['Расстояние'].sum())
        with col7:
            st.metric('Стоимость, руб', shortest_path_length)
        with col8:
            # st.metric('Время', convert_minutes(to_show['Время'].apply(convert_time).sum()))
            st.metric('Время', str(to_show['Время'].sum()) + ' дней')
        to_show.index = range(len(to_show))
        st.dataframe(to_show, width=700)
        cost_but = st.button('Показать на карте', key=2)
        if cost_but: 
            folium.vector_layers.PolyLine(get_lan_lon(nodes, to_draw), dash_array='10', color=sup_color[shortest_path[0]]).add_to(m)
            place[-1]._html(m._repr_html_(), width=700, height=500)
        
        st.subheader('Самый быстрый маршрут')
        col9 , col10, col11 = st.columns([1, 1, 2])
        # if path_type == 'Самый быстрый маршрут':
        shortest_path_length, shortest_path, to_show, to_draw = shortest_dict['time']
        # folium.vector_layers.PolyLine(get_lan_lon(nodes, to_draw), dash_array='10', color=sup_color[shortest_path[0]]).add_to(m)
        # place[-1]._html(m._repr_html_(), width=700, height=500)
        with col9:
            st.metric('Расстояние, км', to_show['Расстояние'].sum())
        with col10:
            st.metric('Стоимость, руб', to_show['Стоимость'].sum())
        with col11:
            # st.metric('Время', convert_minutes(shortest_path_length))
            st.metric('Время', str(shortest_path_length) + ' дней')
        to_show.index = range(len(to_show))
        st.dataframe(to_show, width=700)
        fast_but = st.button('Показать на карте', key=3)
        if fast_but: 
            folium.vector_layers.PolyLine(get_lan_lon(nodes, to_draw), dash_array='10', color=sup_color[shortest_path[0]]).add_to(m)
            place[-1]._html(m._repr_html_(), width=700, height=500)
    except:
        st.info('Нет маршрутов')

    