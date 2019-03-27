from zabbix.api import ZabbixAPI
from Logging import LogManager
import string
from random import randint, choice
import configparser

class ZabbixManager:
	"""
	Classe para gerenciar a conexao e operacoes via API Zabbix.
	"""

	def __init__(self):
		"""
		Metodo construtor.
		Pega configuracoes iniciais do arquivo conexao.ini.
		"""
		cp = configparser.ConfigParser()
		cp.read('conexao.ini')
		if cp.has_section('zabbix'):
			self._log_level = cp['zabbix']['log_level']
			self._log = LogManager(self._log_level, __name__)
			self._server_url = cp['zabbix']['host']
			self._user = cp['zabbix']['username']
			self._password = cp['zabbix']['password']
			self.DEFAULT_GROUP = cp['zabbix']['default_group']
			#self.ADMIN_GROUPS = cp['zabbix']['admin_groups']
			#self.SUPERADMIN_GROUPS = cp['zabbix']['superadmin_groups']
			self._log.logger.debug("Pegou configuracoes do arquivo conexao.ini.")

	def connect(self):
		"""
		Metodo para conexao ao Zabbix via API
		"""
		self.zapi = ZabbixAPI(url=self._server_url, user=self._user, password=self._password)
		self._log.logger.debug("Conectou na API Zabbix.")

	def disconnect(self):
		"""
		Metodo para desconectar o usuario conectado na API Zabbix
		"""
		self.zapi.user.logout()
		self._log.logger.debug("Desconectou da API Zabbix.")

	def getUsers(self):
		"""
		Metodo que retorna usuarios Zabbix.

		Returns
		-------
		list
			Lista contendo os usuarios Zabbix.
			Ex:
			['Admin', 'guest', 'thiago']
		"""
		list_users = []
		#for user in self.zapi.user.get(selectUsrgrps=1):
		for user in self.zapi.user.get(output=['alias']):
			list_users.append(user['alias'])
		
		return list_users

	def getUsergroupsList(self, with_members=False):
		"""
		Metodo que retorna lista com dicionarios contendo o nome do grupo 
		de usuario, seu id e lista de membros caso parametro seja True.

		Parameters
		----------
		with_members : bool
			Filtro que determina se retorna ou nao os membros dos grupos.

		Returns
		-------
		list
			Lista contendo nome dos grupos de usuario existentes no Zabbix.
			Ex:
			[{'group': 'Zabbix administrators', 'id': '7'}, {'group': 'Guests', 'id': '8'}]
			
			Ex:
			[{'group': 'Zabbix administrators', 'id': '7', 'members': [{'id': '1', 'alias': 'Admin'}, {'id': '3', 'alias': 'thiago'}]}]
		"""
		usergroup_list = []
		query = self.zapi.usergroup.get(selectUsers=1)
		user_query = self.zapi.user.get(output=['id','alias'])
		userid_map_alias = {}

		# Monta dicionario chave/valor -> id/alias
		for user in user_query:
			userid_map_alias[user['userid']] = user['alias']

		for usergroup in query:
			group_dic = {}
			group_dic['group'] = usergroup['name']
			group_dic['id'] = usergroup['usrgrpid']
			member_list = []
			if with_members:
				for member in usergroup['users']:
					member_dic = {}
					member_dic['id'] = member['userid']
					member_dic['alias'] = userid_map_alias[member['userid']]
					member_list.append(member_dic)
				group_dic['members'] = member_list
			usergroup_list.append(group_dic)
		return usergroup_list

	def getHostgroupsList(self):
		"""
		Metodo que retorna lista com nomes dos grupos de host do Zabbix.

		Returns
		-------
		list
			Lista contendo nome dos grupos de host existentes no Zabbix.
			Ex:
			['Templates', 'Linux Servers', 'Datacenter/Zabbix servers']
		"""
		hostgroup_list = []
		query = self.zapi.hostgroup.get()

		for hostgroup in query:
			hostgroup_list.append(hostgroup['name'])

		return hostgroup_list

	def getHostgroupId(self, hostgroup_name):
		"""
		Metodo que recebe nome de um grupo de host e retorna o seu ID.

		Parameters
		----------
		hostgroup_name : str
			Nome do grupo de host
			Ex: 'Templates'

		Returns
		-------
		str
			ID do grupo de host.
			Ex:
			1
		"""
		#result = 'ID nao encontrado.'
		if hostgroup_name:
			result = self.zapi.do_request('hostgroup.get',
										{
											'filter': {
												'name': hostgroup_name
											}
										})

		return result['result'][0]['groupid']

	def getUsergroupId(self, usergroup_name):
		"""
		Metodo que recebe nome de um grupo de usuario e retorna o seu ID.

		Parameters
		----------
		hostgroup_name : str
			Nome do grupo de usuario.
			Ex: 'Your Group'

		Returns
		-------
		str
			ID do grupo de usuario.
			Ex:
			128
		"""
		#result = 'ID nao encontrado.'
		if usergroup_name:
			result = self.zapi.do_request('usergroup.get',
										{
											'filter': {
												'name': usergroup_name
											}
										})
			grpid = False
			try:
				grpid = result['result'][0]['usrgrpid']
			except IndexError:
				self._log.logger.debug("Nao encontrou ID do usergroup " + usergroup_name)
			return grpid

	def createUsergroups(self, usergroup_list):
		"""
		Metodo que cria grupos de usuario no Zabbix.

		Parameters
		----------
		usergroup_list : list
			Lista contendo os nomes dos grupos a serem criados no Zabbix.
			Ex:
			['Your Group']
		"""
		if usergroup_list:
			for usergroup in usergroup_list:
				self.zapi.do_request('usergroup.create',
									{
										'name': usergroup#,
										#'rights': {
										#	'permission': 2,
										#	'id': self.getHostgroupId(usergroup)
										#}
									})
				self._log.logger.info('Criou o usergroup ' + usergroup)

	def createHostgroups(self, hostgroup_list):
		"""
		Metodo que cria grupos de host no Zabbix.

		Parameters
		----------
		hostgroup_list : list
			Lista contendo nome dos grupos de host a serem criados.
			Ex:
			['Your Group']
		"""
		if hostgroup_list:
			for hostgroup in hostgroup_list:
				self.zapi.hostgroup.create(name=hostgroup)
				self._log.logger.info('Criou o hostgroup ' + hostgroup)

	def createUsers(self, user_list):
		"""
		Metodo que cria usuarios no Zabbix.

		Parameters
		----------
		user_list : list
			Lista contendo lista com detalhes dos usuarios a serem criados.
			Ex:
			[{'alias': 'fulano', 'groups': [{'usrgrpid': '127'}], 'name': 'FULANO DE ARAUJO'}, 
			{'alias': 'ciclano', 'groups': [{'usrgrpid': '134'}], 'name': 'CICLANO OLIVEIRA'}]
		"""
		allchar = string.ascii_letters + string.punctuation + string.digits
		if user_list:
			default_group = {}
			default_group['usrgrpid'] = self.getUsergroupId(self.DEFAULT_GROUP)
			if not default_group['usrgrpid']:
				self.createUsergroups([self.DEFAULT_GROUP])
				default_group['usrgrpid'] = self.getUsergroupId(self.DEFAULT_GROUP)

			for user in user_list:
				user['groups'].append(default_group)
				result = self.zapi.user.create(alias=user['alias'],
											name=user['name'],
											passwd="".join(choice(allchar) for x in range(randint(8, 12))),
											usrgrps=user['groups'],
											refresh='60s',
											rows_per_page='100',
											lang='pt_BR'
											)
				self._log.logger.info('Criou o usuario ' + user['alias'] + ' nos usergroups ' + str(user['groups']))
				self._log.logger.debug(result)
		else:
			self._log.logger.info('Nenhum usuario criado.')

	def updateUsers(self, user_list):
		"""
		Metodo que atualiza usuarios no Zabbix ajustando os usergroups nos quais fazem parte.

		Parameters
		----------
		user_list : list
			Lista contendo dicionario com lista de usergroups a serem atualizados,
			contendo os usuarios a serem adicionados e removidos dos grupos.
			Ex:
			[{'group': 'Your Group', 'id': '55', 'add': ['8'], 'remove': []}]
		"""
		if user_list:
			for item in user_list:
				zb_usergroup = self.zapi.usergroup.get(selectUsers=1, filter={'name' : item['group']})

				users_list = []

				for user in zb_usergroup[0]['users']:
					users_list.append(user['userid'])

				if item['add']:
					users_list.extend(item['add'])

				if item['remove']:
					users_list = [n for n in users_list if n not in item['remove']]

				self.zapi.usergroup.update(usrgrpid=item['id'], userids=users_list)
				self._log.logger.info('Atualizou o usergroup ' + item['group'] + ' com os userids ' + str(users_list))
		else:
			self._log.logger.info('Nenhum usergroup atualizado.')
		
	def serviceExists(self, name, parent):
		"""
		Metodo que verifica se um servico existe na arvore de SLAs.

		Parameters
		----------
		name : str
			Nome do servico que sera procurado na arvore.
		parent: int
			ID do servico pai no qual o nome do servico sera procurado. Opcional.
		
		Returns
		-------
		int
			ID do servico caso encontrado.
		bool
			False caso nao encontre o servico.
		"""
		result = False
		if name and parent:
			service = self.zapi.service.get(output=['serviceid'],
										filter={'name': name},
										parentids=parent)
		elif name:
			service = self.zapi.service.get(output=['serviceid'],
										filter={'name': name})
		if service:
			result = service[0]['serviceid']
		return result

	def serviceCreate(self, name, parent, triggerid):
		"""
		Metodo que cria um servico na arvore de SLAs.

		Parameters
		----------
		name : str
			Nome do servico que sera criado na arvore.
		parent: int
			ID do servico pai no qual o servico sera criado. Opcional.
		triggerid : int
			ID da trigger que sera vinculada ao SLA do servico. Opcional.
		
		Returns
		-------
		int
			ID do servico criado.
		bool
			False caso nao encontre o servico.
		"""
		result = False
		if name and parent and triggerid:
			result = self.zapi.service.create(name=name,
										algorithm=1,
										showsla=1,
										goodsla=97,
										sortorder=0,
										parentid=parent,
										triggerid=triggerid)
			self._log.logger.info("Servico '" + name + "' criado. ID: " + result['serviceids'][0])
		elif name and parent:
			result = self.zapi.service.create(name=name,
										algorithm=1,
										showsla=1,
										goodsla=97,
										sortorder=0,
										parentid=parent)
			self._log.logger.info("Servico '" + name + "' criado. ID: " + result['serviceids'][0])
		elif name:
			result = self.zapi.service.create(name=name,
										algorithm=1,
										showsla=1,
										goodsla=97,
										sortorder=0)
			self._log.logger.info("Servico '" + name + "' criado. ID: " + result['serviceids'][0])
		return result['serviceids'][0]

	def serviceAddSoftDependency(self, name, svc_trigger, parent):
		"""
		Metodo que cria um servico dependente na arvore de SLAs.

		Parameters
		----------
		name : str
			Nome do servico dependente que sera criado na arvore.
		parent: int
			ID do servico pai no qual o servico dependente sera criado.
		svc_trigger : int
			ID do servico no qual o servico criado ficara dependente.
		"""
		dependencies = self.zapi.service.get(selectDependencies="extend",
										serviceids=parent)
		add = True
		for dep in dependencies[0]['dependencies']:
			if dep['serviceid'] == svc_trigger:
				add = False
		if add:
			self.zapi.service.adddependencies(serviceid=parent,
										dependsOnServiceid=svc_trigger,
										soft=1)
			self._log.logger.info('Adicionou dependencia "' + name + '". ParentID: ' + parent + '. ServiceID vinculado: ' + svc_trigger)
