import unittest
from ontology_helper import *
import numpy as np

class MyTestCase(unittest.TestCase):
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



if __name__ == '__main__':
    unittest.main()
