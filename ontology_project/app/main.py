import argparse
import pandas as pd
import json
from fastapi import FastAPI
from pydantic import BaseModel
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from ontology_helper import *

app = FastAPI()
class QueryRequest(BaseModel):
    dir_csv: str = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'onto_x.csv')
    # dir_csv: str = 'data/onto_x.csv'
    label: str
    n: int = 9999

@app.post('/query-ontology/')
def query_ontology(request: QueryRequest):
    df = pd.read_csv(request.dir_csv)
    df_formatted = preprocess_dataframe(df)
    empty_dict = initialize_empty_dictionary_from_df(df_formatted)
    label = request.label
    if label in list(df_formatted['Preferred Label'].unique()):
        onto_dict = get_ontology(label, df_formatted)
        final_dict = sort_dictionary(fill_dictionary_with_ontology_results(empty_dict, onto_dict))

        n = request.n
        first_elements = {k: v for i, (k, v) in enumerate(final_dict.items()) if i < n}
        return first_elements
    else:
        return f"The entity '{label}' is not present in the CSV. Please, check the spelling of the label."

def main(args):
    df = pd.read_csv(args.dir_csv)
    df_formatted = preprocess_dataframe(df)
    empty_dict = initialize_empty_dictionary_from_df(df_formatted)
    label = args.label
    if label in list(df_formatted['Preferred Label'].unique()):
        onto_dict = get_ontology(label, df_formatted)
        final_dict = sort_dictionary(fill_dictionary_with_ontology_results(empty_dict, onto_dict))

        n = args.n
        first_elements = {k: v for i, (k, v) in enumerate(final_dict.items()) if i < n}
        print(json.dumps(first_elements, indent=0))
    else:
        print(f"The entity '{label}' is not present in the CSV. Please, check the spelling of the label.")

if __name__ == '__main__':
    dir_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'onto_x.csv')
    parser = argparse.ArgumentParser(description='Ontology API')
    parser.add_argument('--dir_csv', default=dir_csv, type=str, help='Path to the csv file containing the ontology')
    parser.add_argument('--label', type=str, required=True, help='Name of the entity used for the query')
    parser.add_argument('--n', default=9999, type=int, help='Number of entities shown after a query. Set by default at 10')

    args = parser.parse_args()
    main(args)



