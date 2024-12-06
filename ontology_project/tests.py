import unittest
from ontology_helper import *
import numpy as np

class MyTestCase(unittest.TestCase):
    def test_check_columns(self):
        df_with_right_labels = pd.DataFrame({'Class ID': ['A', 'B', 'C', 'D'],
                           'Preferred Label': ['a', 'b', 'c', 'd'],
                           'Parents': ['B', 'C', 'D', 'E']})

        try:
            check_required_columns(df_with_right_labels)
        except Exception as e:
            self.fail(f"check_required_columns raised an unexpected error: {e}")

        df_with_wrong_labels = pd.DataFrame({'Class ID': ['A', 'B', 'C', 'D'],
                            'Label': ['a', 'b', 'c', 'd'],
                            'Parent': ['B', 'C', 'D', 'E']})


        with self.assertRaises(ValueError) as context:
            check_required_columns(df_with_wrong_labels)
        self.assertIn("Preferred Label", str(context.exception))
        self.assertIn("Parents", str(context.exception))

    def test_nan_removal(self):
        df_with_nan = pd.DataFrame({'Class ID': [f'http://entity{i}/' for i in range(1, 4)],
                           'Preferred Label': [f'entity{i}' for i in range(1, 4)],
                           'Parents': ['http://entity2/', 'http://entity3/', np.nan]})

        target_df = pd.DataFrame({'Class ID': [f'http://entity{i}/' for i in range(1, 4)],
                           'Preferred Label': [f'entity{i}' for i in range(1, 4)],
                           'Parents': ['http://entity2/', 'http://entity3/', 'None']})

        df_with_nan_removed = replace_nan_values(df_with_nan)
        pd.testing.assert_frame_equal(target_df, df_with_nan_removed)

    def test_duplicates_renaming(self):
        df_with_duplicates = pd.DataFrame({'Class ID': ['http://entity1/', 'http://entity2/', 'http://entity3/'],
                           'Preferred Label': ['entity1', 'entity2', 'entity1'],
                           'Parents': ['http://entity2/', 'http://entity3/', 'http://entity4/']})

        target_df = pd.DataFrame({'Class ID': ['http://entity1/', 'http://entity2/', 'http://entity3/'],
                           'Preferred Label': ['entity1', 'entity2', 'entity1_2'],
                           'Parents': ['http://entity2/', 'http://entity3/', 'http://entity4/']})

        df_with_duplicates_renamed = df_with_duplicates.copy()
        df_with_duplicates_renamed['Preferred Label'] = rename_duplicates(df_with_duplicates_renamed['Preferred Label'])
        pd.testing.assert_frame_equal(target_df, df_with_duplicates_renamed)

    def test_cycles_identification(self):
        df_with_cyles = pd.DataFrame({'Class ID': ['http://entity1/', 'http://entity2/', 'http://entity3/'],
                           'Preferred Label': ['entity1', 'entity2', 'entity3'],
                           'Parents': ['http://entity2/', 'http://entity1/', 'http://entity4/']})

        target_df = pd.DataFrame({'Class ID': ['http://entity1/', 'http://entity2/', 'http://entity3/'],
                           'Preferred Label': ['entity1', 'entity2', 'entity3'],
                           'Parents': ['http://entity2/', 'http://entity1/', 'http://entity4/'],
                           'In Cycle': [True, True, False]})

        df_with_cycles_identified = identify_cycles(df_with_cyles)
        pd.testing.assert_frame_equal(target_df, df_with_cycles_identified)

    def test_whole_preprocessing(self):
        base_df = pd.DataFrame({'Class ID': ['http://entity1/', 'http://entity2/', 'http://entity3/'],
                           'Preferred Label': ['entity1', 'entity2', 'entity1'],
                           'Parents': ['http://entity2/', 'http://entity1/', np.nan]})

        target_df = pd.DataFrame({'Class ID': ['http://entity1/', 'http://entity2/', 'http://entity3/'],
                                  'Preferred Label': ['entity1', 'entity2', 'entity1_2'],
                                  'Parents': ['http://entity2/', 'http://entity1/', 'None'],
                                  'In Cycle': [True, True, False]})

        preprocessed_df = preprocess_dataframe(base_df)
        pd.testing.assert_frame_equal(target_df, preprocessed_df)

    def test_ontology_simple_case(self):
        df = pd.DataFrame({'Class ID': ['A', 'B', 'C', 'D'],
                           'Preferred Label': ['a', 'b', 'c', 'd'],
                           'Parents': ['B', 'C', 'D', 'E'],
                           'In Cycle': [False, False, False, False]})

        target_ontology = {'a':0,
                           'b':1,
                           'c':2,
                           'd':3,
                           }

        simple_ontology = get_ontology('a', df)
        self.assertDictEqual(target_ontology, simple_ontology)

    def test_ontology_several_parents(self):
        df1 = pd.DataFrame({'Class ID': ['A', 'B', 'C', 'D'],
                           'Preferred Label': ['a', 'b', 'c', 'd'],
                           'Parents': ['B', 'C|D', 'E', 'F'],
                           'In Cycle': [False, False, False, False]})

        target_ontology1 = {'a': 0,
                           'b': 1,
                           'c': 2,
                           'd': 2,
                           }

        complex_ontology1 = get_ontology('a', df1)
        self.assertDictEqual(target_ontology1, complex_ontology1)

        df2 = pd.DataFrame({'Class ID': ['A', 'B', 'C', 'D', 'E'],
                            'Preferred Label': ['a', 'b', 'c', 'd', 'e'],
                            'Parents': ['B|C', 'None', 'D|E', 'None', 'None'],
                            'In Cycle': [False, False, False, False, False]})

        target_ontology2 = {'a': 0,
                            'b': 1,
                            'c': 1,
                            'd': 2,
                            'e': 2
                            }

        complex_ontology2 = get_ontology('a', df2)
        self.assertDictEqual(target_ontology2, complex_ontology2)

    def test_ontology_cyclic_parentship(self):
        df_with_cycles = pd.DataFrame({'Class ID': ['A', 'B', 'C', 'D', 'E'],
                                       'Preferred Label': ['a', 'b', 'c', 'd', 'e'],
                                       'Parents': ['B|C', 'A', 'D|E', 'None', 'None'],
                                       'In Cycle': [True, True, False, False, False]})

        target_ontology1 = {'a': 'In a cyclic parentship (direct parents: B|C)'}
        complex_ontology1 = get_ontology('a', df_with_cycles)
        self.assertDictEqual(target_ontology1, complex_ontology1)

        target_ontology2 = {'c': 0,
                            'd': 1,
                            'e': 1}
        complex_ontology2 = get_ontology('c', df_with_cycles)
        self.assertDictEqual(target_ontology2, complex_ontology2)

    def test_dict_initialization(self):
        df = pd.DataFrame({'Class ID': ['A', 'B', 'C', 'D'],
                           'Preferred Label': ['a', 'b', 'c', 'd'],
                           'Parents': ['B', 'C', 'D', 'E']})

        target_dict = {'a':0,
                       'b':0,
                       'c':0,
                       'd':0
                       }

        dict_obtained_from_df = initialize_empty_dictionary_from_df(df)
        self.assertDictEqual(target_dict, dict_obtained_from_df)

    def test_dict_filling(self):
        dict_onto = {'b':1,
                     'c':2
                     }

        dict_empty = {'a':0,
                      'b':0,
                      'c':0,
                      'd':0
                      }

        target_dict = {'a':0,
                       'b':1,
                       'c':2,
                       'd':0
                      }

        dict_obtained_from_filling = fill_dictionary_with_ontology_results(dict_empty, dict_onto)
        self.assertDictEqual(target_dict, dict_obtained_from_filling)
        
if __name__ == '__main__':
    unittest.main()
