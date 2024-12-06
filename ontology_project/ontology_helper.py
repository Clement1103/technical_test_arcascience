import pandas as pd

DIR_CSV = 'onto_x.csv'

def replace_nan_values(dataframe):
    dataframe['Parents'] = dataframe['Parents'].apply(lambda x: 'None' if isinstance(x, float) else x)
    return dataframe

