import unittest
import sync_users

class SyncUsersTestCase(unittest.TestCase):

    def setUp(self):
        """
        Testa conexao com API Zabbix e AD. Primeiro metodo a ser executado.
        """
        global zm, am
        zm = sync_users.ZabbixManager()
        zm.connect()
        sync_users.zm = zm

        am = sync_users.AdManager()
        am.connect()
        sync_users.am = am

        global ad_dic, zb_dic
        ad_dic = am.getGroupMembersDic(am.FILTER_GROUP_SEARCH_AD)	
        zb_dic = zm.getUsergroupsList(True)

    def test_zabbixUsergroupsToBeCreated(self):
        """
        Testa se o metodo em questao retorna uma lista.
        """
        self.assertIsInstance(sync_users.zabbixUsergroupsToBeCreated(), list)

    def test_zabbixHostgroupsToBeCreated(self):
        """
        Testa se o metodo em questao retorna uma lista.
        """
        self.assertIsInstance(sync_users.zabbixHostgroupsToBeCreated(), list)

    def test_getUsersListToBeCreatedZabbix(self):
        """
        Testa se o metodo em questao retorna uma lista.
        """
        self.assertIsInstance(sync_users.getUsersListToBeCreatedZabbix(zb_dic, ad_dic), list)

    def test_getUsersListToBeUpdatedZabbix(self):
        """
        Testa se o metodo em questao retorna uma lista.
        """
        self.assertIsInstance(sync_users.getUsersListToBeUpdatedZabbix(zb_dic, ad_dic), list)

    def tearDown(self):
        """
        Testa desconexao da API Zabbix e do AD. Executado por ultimo.
        """
        zm.disconnect()
        am.disconnect()

if __name__ == '__main__':
    unittest.main()
