import unittest
import ZabbixManager

class ZabbixTestCase(unittest.TestCase):

    def setUp(self):
        """
        Testa conexao com API Zabbix. Primeiro metodo a ser executado.
        """
        global zm
        zm = ZabbixManager.ZabbixManager()
        zm.connect()

    def testGetUsers(self):
        """
        Testa se o metodo em questao retorna uma lista.
        """
        self.assertIsInstance(zm.getUsers(), list)

    def testGetUsergroupsList(self):
        """
        Testa se o metodo em questao retorna uma lista.
        """
        self.assertIsInstance(zm.getUsergroupsList(), list)

    def testGetHostgroupsList(self):
        """
        Testa se o metodo em questao retorna uma lista.
        """
        self.assertIsInstance(zm.getHostgroupsList(), list)

    def testGetHostgroupId(self):
        """
        Testa se o metodo em questao retorna um numero.
        """
        self.assertIsInstance(int(zm.getHostgroupId('Your HostGroup')), int)

    def testGetUsergroupId(self):
        """
        Testa se o metodo em questao retorna um numero.
        """
        self.assertIsInstance(int(zm.getUsergroupId('Your Group (AD)')), int)

    def tearDown(self):
        """
        Testa desconexao da API Zabbix. Executado por ultimo.
        """
        zm.disconnect()

if __name__ == '__main__':
    unittest.main()
