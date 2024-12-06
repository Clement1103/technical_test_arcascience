from ontology_helper import *
import pandas as pd
from ontology_helper import sort_dictionary
import json

DIR_CSV = 'onto_x.csv'


if __name__ == '__main__':
    df = pd.read_csv(DIR_CSV)
    df_formatted = preprocess_dataframe(df)
    empty_dict = initialize_empty_dictionary_from_df(df_formatted)
    label = input('Type a label: ')
    onto_dict = get_ontology(label, df_formatted)
    final_dict = sort_dictionary(fill_dictionary_with_ontology_results(empty_dict, onto_dict))

    n = 10
    first_elements = {k: v for i, (k, v) in enumerate(final_dict.items()) if i < n}
    print(json.dumps(first_elements, indent=0))



