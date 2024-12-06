import pandas as pd

DIR_CSV = 'onto_x.csv'

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