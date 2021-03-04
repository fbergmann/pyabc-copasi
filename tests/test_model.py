import unittest
import basico_forward
import pickle
import COPASI

class TestBasicoModel(unittest.TestCase):

    def setUp(self):
        model = basico_forward.BasicoModel('./data/abc_example_model1.xml')
        self.assertTrue(model.dm is not None)
        self.assertTrue(isinstance(model.dm, COPASI.CDataModel))
        self.assertEqual(model.dm.getModel().getObjectName(), 'ABC Example')
        self.model = model

    def test_pickle_working(self):
        obj = pickle.dumps(self.model)
        m2 = pickle.loads(obj)
        self.assertTrue(isinstance(m2, basico_forward.BasicoModel))
        self.assertEqual(m2.dm.getModel().getObjectName(), 'ABC Example')