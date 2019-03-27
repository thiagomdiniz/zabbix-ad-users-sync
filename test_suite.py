import unittest
import sys
import test_AdManager
import test_ZabbixManager
import test_sync_users

def createSuite():
    """
    Metodo que carrega testes dos arquivos importados.

    Returns
    -------
    unittest.suite.TestSuite
        Objeto com suite de testes a serem executados.
    """
    loader = unittest.TestLoader()
    test_suite = unittest.TestSuite()
    test_suite.addTests(loader.loadTestsFromModule(test_AdManager))
    test_suite.addTests(loader.loadTestsFromModule(test_ZabbixManager))
    test_suite.addTests(loader.loadTestsFromModule(test_sync_users))
    return test_suite

if __name__ == '__main__':
    suite = createSuite()
    ret = unittest.TextTestRunner().run(suite)
    if not ret.wasSuccessful():
        sys.exit(1)
