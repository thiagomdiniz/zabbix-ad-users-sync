import ldap
from Logging import LogManager
import configparser

class AdManager:
	"""
	Classe para gerenciar a conexao e extracao de dados do AD.
	"""

	def __init__(self):
		"""
		Metodo construtor.
		Pega configuracoes iniciais do arquivo conexao.ini.
		"""
		cp = configparser.ConfigParser()
		cp.read('conexao.ini', encoding='utf-8')
		if cp.has_section('ad'):
			self._log_level = cp['ad']['log_level']
			self._log = LogManager(self._log_level, __name__)
			self._server_url = cp['ad']['host']
			self._bind_dn = cp['ad']['bind_dn']
			self._bind_pass = cp['ad']['bind_pw']
			self._users_ou = cp['ad']['users_ou']
			self._groups_ou = cp['ad']['groups_ou']
			self._group_filter = '(&(objectClass=user)(memberof:1.2.840.113556.1.4.1941:=cn={group_name},%s)(!(userAccountControl:1.2.840.113556.1.4.803:=2)))' % self._groups_ou
			self._log.logger.debug("Pegou configuracoes do arquivo conexao.ini.")
			self.FILTER_GROUP_SEARCH_ZB = cp['ad']['filter_group_search_zb'].replace("'", '')
			self.FILTER_GROUP_SUFFIX_ZB = cp['ad']['filter_group_suffix_zb'].replace("'", '')
			# Monta filtro com grupos do AD informados no conexao.ini
			self.FILTER_GROUP_SEARCH_AD = '(|'
			cp_groups = cp['ad']['filter_group_search'].split('\n')
			for group in list(filter(None, cp_groups)): # o filter elimina possiveis itens vazios na lista
				self.FILTER_GROUP_SEARCH_AD += '(cn=' + group + ')'
			self.FILTER_GROUP_SEARCH_AD += ')'

	def connect(self):
		"""
		Metodo para conexao ao AD.
		"""
		self.ldap = ldap.initialize(self._server_url)
		#self.ldap.set_option(ldap.OPT_X_TLS_CACERTFILE , '/path/to/saved.cert') # ldaps://
		self.ldap.set_option(ldap.OPT_REFERRALS, 0)
		self.ldap.bind_s(self._bind_dn, self._bind_pass)
		self._log.logger.debug("Conectou no AD.")

	def disconnect(self):
		"""
		Metodo para desconectar do AD.
		"""
		self.ldap.unbind()
		self._log.logger.debug("Desconectou do AD.")

	def convertAdGroupNameToZabbix(self, group):
		"""
		Metodo estatico para conversao do nome do grupo do AD para uso no Zabbix:
		'Monitoracao - Your Group 1' -> 'Your Group 1 (AD)'.
		"""
		return group.replace(self.FILTER_GROUP_SEARCH_ZB, '') + self.FILTER_GROUP_SUFFIX_ZB

	def getGroups(self, filter):
		"""
		Metodo que retorna grupos do AD.

		Parameters
		----------
		filter : str
			Filtro a ser utilizado na consulta ao AD.
			Ex: 'cn=Monitoracao - *'

		Returns
		-------
		list
			Lista contendo as informacoes retornadas pela consulta ao AD.
			Ex:
			[('CN=Monitoracao - Acesso de leitura,OU=Grupos,DC=yourdomain,DC=com', 
			{'objectClass': [b'top', b'group'], 'cn': [b'Monitoracao - Acesso de leitura'], 
			'member': [b'CN=EntryOne,OU=Groups,DC=yourdomain,DC=com'], 
			'distinguishedName': [b'CN=Monitoracao - Acesso de leitura,OU=Grupos,DC=yourdomain,DC=com'], 
			'instanceType': [b'4'], 'whenCreated': [b'20180625183748.0Z'], 'whenChanged': [b'20180628202053.0Z'], 'uSNCreated': [b'14221245'], 
			'uSNChanged': [b'14286213'], 'name': [b'Monitoracao - Acesso de leitura'], 
			'objectGUID': [b'\x83\xd1\xd2*Q\x11\xbfO\x84=\xa9\xf1m\x91\xc2\xba'], 
			'objectSid': [b'\x01\x05\x00\x00\x00\x00\x00\x05\x15\x00\x00\x00\xfa\xd0IY\xc3\xbf\xf7\xce\xd4\x879\x7fm!\xb0\x00'], 
			'sAMAccountName': [b'Monitoracao - Acesso de leitura'], 'sAMAccountType': [b'536870912'], 'groupType': [b'-2147483644'], 
			'objectCategory': [b'CN=Group,CN=Schema,CN=Configuration,DC=yourdomain,DC=com'], 'dSCorePropagationData': [b'16010101000000.0Z']})]
		"""
		result = self.ldap.search_s(self._groups_ou, ldap.SCOPE_ONELEVEL, filter)
		return result

	def getGroupsList(self, filter):
		"""
		Metodo que retorna lista contendo apenas os nomes dos grupos.

		Parameters
		----------
		filter : str
			Filtro a ser utilizado na consulta dos grupos no AD.
			Ex: 'cn=Monitoracao - *'

		Returns
		-------
		list
			Lista contendo nomes dos grupos retornados pelo AD.
			Ex:
			['Monitoracao - Acesso de leitura', 'Monitoracao - Your Group 1']
		"""
		group_list = []
		query = self.getGroups(filter)
		
		for group in query:
			group_list.append(group[1]['cn'][0].decode('utf-8'))

		return group_list

	def getUsersFromGroup(self, group_name):
		"""
		Metodo que retorna usuarios membros de um grupo no AD.

		Parameters
		----------
		group_name : str
			Grupo do AD a ser utilizado no filtro para buscar os usuarios membros.
			Ex: 'Monitoracao - Your Group 1'

		Returns
		-------
		list
			Lista contendo os usuarios membros do grupo usado no filtro.
			Ex:
			[('CN=FULANO OLIVEIRA,OU=STI,OU=IT Admins,DC=yourdomain,DC=com', 
			{'sAMAccountName': [b'fulano']}), 
			('CN=CICLANO COSTA,OU=ITI,OU=IT Admins,DC=yourdomain,DC=com', 
			{'sAMAccountName': [b'ciclano']})]
		"""
		filter = self._group_filter.replace('{group_name}', group_name)
		result = self.ldap.search_s(self._users_ou, ldap.SCOPE_SUBTREE, filter, ['samaccountname'])
		return result

	def getGroupMembersDic(self, group_filter):
		"""
		Metodo que retorna dicionario com grupo e seus respectivos membros do AD.

		Parameters
		----------
		group_filter : str
			Filtro a ser utilizado no AD para buscar os usuarios membros do grupo/filtro repassdo.
			Ex: 'cn=Monitoracao - *'
		
		Returns
		-------
		dict
			Dicionario contendo o nome do grupo (key 'group'), e membros (key 'members') contendo uma 
			lista com as informções de 'alias' (login do usuario no AD) e 'name' (Nome do usuario no AD).
			Ex:
			[{'group': 'Acesso de leitura', 'members': [{'alias': 'thiago', 'name': 'THIAGO MURILO DINIZ'}, 
			{'alias': 'fulano', 'name': 'FULANO OLIVEIRA'}]}, {'group': 'Your Group', 
			'members': [{'alias': 'thiago', 'name': 'THIAGO MURILO DINIZ'}, {'alias': '´fulano', 'name': 'FULANO OLIVEIRA'}]}]
		"""
		groups_members = []
		for ad_group in self.getGroupsList(group_filter):
			zb_group = self.convertAdGroupNameToZabbix(ad_group)
			members = []

			for member in self.getUsersFromGroup(ad_group):
				if 'sAMAccountName' in member[1]:
					members.append({
									'alias': member[1]['sAMAccountName'][0].decode('utf-8'),
									'name': member[0].split(',')[0].replace('CN=','')
									})

			groups_members.append({'group': zb_group, 'members': members})
		return groups_members
