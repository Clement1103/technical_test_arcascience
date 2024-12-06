from ontology_helper import *
import argparse
import pandas as pd
import json
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()
class QueryRequest(BaseModel):
    dir_csv: str = 'onto_x.csv'
    label: str
    n: int = 10

@app.post('/query-ontology/')
def query_ontology(request: QueryRequest):
    df = pd.read_csv(request.dir_csv)
    df_formatted = preprocess_dataframe(df)
    empty_dict = initialize_empty_dictionary_from_df(df_formatted)
    label = request.label
    onto_dict = get_ontology(label, df_formatted)
    final_dict = sort_dictionary(fill_dictionary_with_ontology_results(empty_dict, onto_dict))

    n = request.n
    first_elements = {k: v for i, (k, v) in enumerate(final_dict.items()) if i < n}
    return first_elements

def main(args):
    df = pd.read_csv(args.dir_csv)
    df_formatted = preprocess_dataframe(df)
    empty_dict = initialize_empty_dictionary_from_df(df_formatted)
    onto_dict = get_ontology(args.label, df_formatted)
    final_dict = sort_dictionary(fill_dictionary_with_ontology_results(empty_dict, onto_dict))

    n = args.n
    first_elements = {k: v for i, (k, v) in enumerate(final_dict.items()) if i < n}
    print(json.dumps(first_elements, indent=0))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ontology API')
    parser.add_argument('--dir_csv', default='onto_x.csv', type=str, help='Path to the csv file containing the ontology')
    parser.add_argument('--label', type=str, required=True, help='Name of the entity used for the query')
    parser.add_argument('--n', default=10, type=int, help='Number of entities shown after a query. Set by default at 10')

    args = parser.parse_args()
    main(args)



