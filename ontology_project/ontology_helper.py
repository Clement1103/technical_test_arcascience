import networkx as nx


def check_required_columns(dataframe):
    """
    Checks if the required columns are present in the DataFrame.

    Args:
        dataframe (pandas.DataFrame): The DataFrame to check for required columns.

    Raises:
        ValueError: If any of the required columns are missing from the DataFrame.
    """

    required_columns = {'Class ID', 'Preferred Label', 'Parents'}
    missing_columns = required_columns - set(dataframe.columns)
    if missing_columns:
        raise ValueError(f'The following columns are missing in the csv file: {', '.join(missing_columns)}')


def replace_nan_values(dataframe):
    """
    Replaces NaN values in the 'Parents' column of the DataFrame with the string 'None'.

    Args:
        dataframe (pandas.DataFrame): The DataFrame in which NaN values are to be replaced.

    Returns:
        pandas.DataFrame: The DataFrame with NaN values in the 'Parents' column replaced by 'None'.
    """

    dataframe['Parents'] = dataframe['Parents'].apply(lambda x: 'None' if isinstance(x, float) else x)
    return dataframe


def rename_duplicates(column):
    """
    Renames duplicate values in a column by appending a suffix to each duplicate.

    This function iterates through a given column and appends a suffix (e.g., '_2', '_3') to each duplicate value.

    Args:
        column (pandas.Series): A pandas Series or list containing the values to be checked for duplicates.

    Returns:
        list: A list of values where duplicates have been renamed with a suffix.
    """
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
    """
    Identifies cycles in a directed graph formed from the DataFrame's 'Class ID' and 'Parents' columns.

    This function builds a directed graph where each 'Class ID' is a node and the 'Parents' represent directed edges.
    It then checks if there are any cycles in the graph. If cycles are detected, it marks the nodes involved in the cycle
    by adding a new column 'In Cycle' to the DataFrame, with `True` for nodes in a cycle and `False` otherwise.

    Args:
        dataframe (pandas.DataFrame): The DataFrame containing 'Class ID' and 'Parents' columns.

    Returns:
        pandas.DataFrame: The original DataFrame with an additional 'In Cycle' column indicating whether each node
                          is part of a cycle.

    Raises:
        ValueError: If the DataFrame does not contain the necessary columns ('Class ID', 'Parents').
    """
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
    """
    Preprocesses the input DataFrame in a standard format.

    This function applies all the previous ones in order to preprocess the input DataFrame and make it usable for the ontology operations.

    Args:
        dataframe (pandas.DataFrame): The DataFrame built from the provided csv file.

    Returns:
        pandas.DataFrame: The original DataFrame with an additional 'In Cycle' column indicating whether each node
                          is part of a cycle, duplicates removed and NaN values replaced.
    """
    check_required_columns(dataframe)
    dataframe = replace_nan_values(dataframe)
    dataframe['Preferred Label'] = rename_duplicates(dataframe['Preferred Label'])
    dataframe = identify_cycles(dataframe)
    return dataframe


def get_ontology(entity_label, dataframe, level=0, ontology=None):
    """
    Recursively deduces a parenthood relation from a DataFrame for a given label.

    This function explores an ontology represented as a DataFrame, recursively building a parent-child hierarchy.
    It starts from the given `entity_label` and explores its parent labels, incrementing the `level` for each
    level of parenthood. If a cycle is detected, it will mark the entity as being in a cyclic relationship.
    The result is a dictionary where the keys are entity labels and the values are their corresponding levels
    in the parent-child hierarchy, or a message indicating a cycle.

    Args:
    entity_label (str): The label of the entity to start the parenthood search from.
    dataframe (pandas.DataFrame): The DataFrame containing the ontology with 'Preferred Label' and 'Parents' columns.
    level (int, optional): The current level in the parent-child hierarchy, defaults to 0.
    ontology (dict, optional): A dictionary to accumulate the results, defaults to None.

    Returns:
    dict: A dictionary where the keys are entity labels and the values are their corresponding levels in the ontology
          hierarchy, or a message indicating a cycle if detected.

    """
    if ontology is None:
        ontology = {}

    if entity_label not in dataframe['Preferred Label'].values:
        raise ValueError(f"The entity label '{entity_label}' does not exist in the 'Preferred Label' column.")

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
    """
    Initializes an empty dictionary with unique 'Preferred Label' values from the DataFrame as keys and 0 as values.

    This function takes a DataFrame, extracts the unique values from the 'Preferred Label' column,
    and creates a dictionary where each unique label is a key, and the corresponding value is set to 0.

    Args:
        dataframe (pandas.DataFrame): The DataFrame containing the 'Preferred Label' column.

    Returns:
        dict: A dictionary with unique 'Preferred Label' values as keys and 0 as the initial value for each key.
    """

    list_labels = list(dataframe['Preferred Label'].unique())
    dictionary = {label: 0 for label in list_labels}
    return dictionary


def fill_dictionary_with_ontology_results(empty_dict, onto_dict):
    """
    Fills an empty dictionary with values from another one.

    This function takes a dictionary, onto_dict, extracts the values for each key, and replaces the values of the empty
    dictionary with them.

    onto_dict (dict): The dictionary containing the new key-value pairs to be added to `empty_dict`.
        empty_dict (dict): The dictionary to be updated with the key-value pairs from `onto_dict`.

    Returns:
        dict: The updated dictionary (`empty_dict`) with values from `onto_dict` assigned to the corresponding keys.
    """

    for k, v in onto_dict.items():
        empty_dict[k] = v
    return empty_dict


def sort_dictionary(dictionary):
    """
    Sorts a dictionary based on its values, placing strings at the top and sorting other values in descending order.

    Args:
        dictionary (dict): The dictionary to be sorted. The dictionary should have comparable values,
                           where strings will be prioritized over other types.

    Returns:
        dict: A new dictionary with the same keys as the original, but with values sorted such that string values
              appear first (sorted in descending order), followed by other values (also sorted in descending order).
    """
    return {k: v for k, v in sorted(dictionary.items(), key=lambda item: (isinstance(item[1], str), item[1]), reverse=True)}
