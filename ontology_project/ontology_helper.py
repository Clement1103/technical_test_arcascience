import pandas as pd
import networkx as nx


def check_required_columns(dataframe):
    required_columns = {'Class ID', 'Preferred Label', 'Parents'}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(f'The following columns are missing in the csv file: {', '.join(missing_columns)}')

def replace_nan_values(dataframe):
    dataframe['Parents'] = dataframe['Parents'].apply(lambda x: 'None' if isinstance(x, float) else x)
    return dataframe

def rename_duplicates(column):
    counts = {}
    new_values = []

    for value in column:
        if value not in counts:
            counts[value] = 1
            new_values.append(value)
        else:
            counts[value] += 1
            new_values.append(f'{value}_{counts[value]}')

    return new_values

def identify_cycles(dataframe):
    graph = nx.DiGraph()
    for _, row in dataframe.iterrows():
        for parent in row['Parents'].split('|'):
            graph.add_edge(row['Class ID'], parent)

    try:
        cycle_edges = nx.find_cycle(graph, orientation="original")
        cycle_nodes = set(node for edge in cycle_edges for node in edge)
    except nx.NetworkXNoCycle:
        cycle_nodes = set()
    dataframe['In Cycle'] = dataframe['Class ID'].apply(lambda x: x in cycle_nodes)
    return dataframe

def preprocess_dataframe(dataframe):
    check_required_columns(dataframe)
    dataframe = replace_nan_values(dataframe)
    dataframe['Preferred Label'] = rename_duplicates(dataframe['Preferred Label'])
    dataframe = identify_cycles(dataframe)
    return dataframe