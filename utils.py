import pandas as pd
from io import StringIO
import networkx as nx

def convert_time(string):
    string = string.split(' ')
    total_time = 0
    for i in range(0, len(string), 2):
        if string[i+1] == 'дн.':
            total_time += 24 * 60 * int(string[i])
        elif string[i+1] == 'ч.':
            total_time += 60 * int(string[i])
        elif string[i+1] == 'мин':
            total_time += int(string[i])
    return total_time

def convert_minutes(value):
    # days = value // (24 * 60)
    # value -= days * (24 * 60)
    hours = value // 60
    value -= hours * 60
    minutes = value
    if minutes > 30: hours += 1
    # if days != 0:
    #     return f'{days} дн. {hours} ч. {minutes} мин'
    # else:
    return f'~ {hours} ч.'

def file_to_df(file):
    bytes_data = file.getvalue()
    s = str(bytes_data, 'utf-8')
    data = StringIO(s) 
    return pd.read_csv(data)

def get_nodes(nodes):
    return nodes[nodes['Type'] != 'Поставщик']['Name'].values
def get_sup(nodes):
    return nodes[nodes['Type'] == 'Поставщик']['Name'].values
    
def fill_graph(nodes, edges):
    G = nx.MultiGraph()
    names = get_nodes(nodes)
    G.add_nodes_from(names)
    keys = G.add_edges_from(get_paths(nodes, edges))
    return G

def convert_edges(nodes, edges):
    paths = edges.copy()
    paths['id_1'] = paths['id_1'].apply(lambda x: nodes['Name'].iloc[x])
    paths['id_2'] = paths['id_2'].apply(lambda x: nodes['Name'].iloc[x])
    return paths

def get_paths(nodes, edges):
    # edges_copy = convert_edges(nodes, edges)
    edges_copy = edges.copy()
    paths = []
    for i in range(len(edges)):
        paths.append([])
        paths[i].append(edges_copy['Пункт отправления'].iloc[i])
        paths[i].append(edges_copy['Пункт прибытия'].iloc[i])
        paths[i].append({'length': edges['Расстояние'].iloc[i], 'cost': edges['Стоимость'].iloc[i], 
                        'time': edges['Время'].iloc[i]})
    return paths

def get_lan_lon(nodes, edges):
    edges_copy = edges.copy()
    # edges_copy['coords_1'] = edges_copy['Пункт отправления'].apply(lambda x: [nodes['lat'].iloc[x], nodes['lon'].iloc[x]])
    # edges_copy['coords_2'] = edges_copy['Пункт прибытия'].apply(lambda x: [nodes['lat'].iloc[x], nodes['lon'].iloc[x]])
    edges_copy['coords_1'] = edges_copy['Пункт отправления'].apply(lambda x: [nodes[nodes['Name']==x]['lat'].values[0], nodes[nodes['Name']==x]['lon'].values[0]])
    edges_copy['coords_2'] = edges_copy['Пункт прибытия'].apply(lambda x: [nodes[nodes['Name']==x]['lat'].values[0], nodes[nodes['Name']==x]['lon'].values[0]])
    edges_copy['coords'] = edges_copy.apply(lambda x: [x['coords_1'], x['coords_2']], axis=1)
    return edges_copy['coords'].values

def cut_edges(nodes, edges, shortest_path):
    lst = []
    # edges_copy = convert_edges(nodes, edges)
    edges_copy = edges.copy()
    for i in range(len(shortest_path)-1):
        path = edges_copy[(edges_copy['Пункт отправления'] == shortest_path[i]) & (edges_copy['Пункт прибытия'] == shortest_path[i+1])]
        if path.empty:
            path = edges_copy[(edges_copy['Пункт отправления'] == shortest_path[i+1]) & (edges_copy['Пункт прибытия'] == shortest_path[i])]
            path['Пункт отправления'] = shortest_path[i]
            path['Пункт прибытия'] = shortest_path[i+1]
        lst.append(path)
    to_show = pd.concat(lst)
    to_draw = edges.iloc[to_show.index]
    # to_show.columns = ['Пункт отправления', 'Пункт прибытия', 'Стоимость', 'Расстояние', 'Время']
    return to_show.drop('Unnamed: 0', axis=1), to_draw.drop('Unnamed: 0', axis=1)

