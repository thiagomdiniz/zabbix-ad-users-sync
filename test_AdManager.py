import unittest
import AdManager

class AdTestCase(unittest.TestCase):

    def setUp(self):
        """
        Testa conexao com AD. Primeiro metodo a ser executado.
        """
        global am
        am = AdManager.AdManager()
        am.connect()

    def testGetGroups(self):
        """
        Testa se o metodo em questao retorna uma lista.
        """
        self.assertIsInstance(am.getGroups(am.FILTER_GROUP_SEARCH_AD), list)

    def testGetGroupsList(self):
        """
        Testa se o metodo em questao retorna ao menos um grupos conforme filtro utilizado.
        """
        self.assertRegex(am.getGroupsList(am.FILTER_GROUP_SEARCH_AD)[0], 'Monitoracao - .*')

    def testGetUsersFromGroup(self):
        """
        Testa se o metodo em questao não retorna 'None', ou seja, testa se retorna algum resultado.
        """
        self.assertNotRegex(am.getUsersFromGroup('Monitoracao - Your Group')[0][0], 'None')

    def testGetGroupMembersDic(self):
        """
        Testa se o metodo em questao retorna um dicionario com a key 'group' conforme filtro utilizado.
        """
        self.assertRegex(am.getGroupMembersDic('cn=Monitoracao - Your Group')[0]['group'], 'Your Group')

    def tearDown(self):
        """
        Testa desconexao do AD. Executado por ultimo.
        """
        am.disconnect()


if __name__ == '__main__':
    unittest.main()
