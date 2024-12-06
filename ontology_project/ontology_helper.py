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


def get_ontology(entity_label, dataframe, level=0, ontology=None):
    if ontology is None:
        ontology = {}

    df_tmp = dataframe[dataframe['Preferred Label'] == entity_label]
    if df_tmp.empty:
        return ontology

    if df_tmp['In Cycle'].iloc[0]:
        ontology[entity_label] = f'In a cyclic parentship (direct parents: {df_tmp['Parents'].iloc[0]})'
        return ontology

    ontology[entity_label] = level

    parent_ids = df_tmp['Parents'].iloc[0]

    for parent_id in parent_ids.split('|'):
        parent_row = dataframe[dataframe['Class ID'] == parent_id]
        if not parent_row.empty:
            parent_label = parent_row['Preferred Label'].iloc[0]
            get_ontology(parent_label, dataframe, level + 1, ontology)

    return ontology


def initialize_empty_dictionary_from_df(dataframe):
    list_labels = list(dataframe['Preferred Label'].unique())
    dictionary = {label: 0 for label in list_labels}
    return dictionary


def fill_dictionary_with_ontology_results(empty_dict, onto_dict):
    for k, v in onto_dict.items():
        empty_dict[k] = v
    return empty_dict


def sort_dictionary(dictionary):
    return {k: v for k, v in sorted(dictionary.items(), key=lambda item: (isinstance(item[1], str), item[1]), reverse=True)}
