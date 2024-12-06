import unittest
from ontology_helper import *
import numpy as np

class MyTestCase(unittest.TestCase):
    def test_nan_removal(self):
        df_with_nan = pd.DataFrame({'Class ID': [f'http://entity{i}/' for i in range(1, 4)],
                           'Preferred Label': [f'entity{i}' for i in range(1, 4)],
                           'Parents': ['http://entity2/', 'http://entity3/', np.nan]})

        df_without_nan = pd.DataFrame({'Class ID': [f'http://entity{i}/' for i in range(1, 4)],
                           'Preferred Label': [f'entity{i}' for i in range(1, 4)],
                           'Parents': ['http://entity2/', 'http://entity3/', 'None']})

        df_with_nan_removed = replace_nan_values(df_with_nan)
        pd.testing.assert_frame_equal(df_without_nan, df_with_nan_removed)


if __name__ == '__main__':
    unittest.main()
