from AdManager import AdManager
from ZabbixManager import ZabbixManager
from collections import Counter

_dic_users_ad = None
zm = am = None

def zabbixUsergroupsToBeCreated():
	"""
	Metodo que retorna nome dos grupos de usuario a serem criados no Zabbix, ou seja,
	que existem no AD e ainda nao existem no Zabbix.

	Returns
	-------
	list
		Lista contendo grupos de usuario que existem no AD nao existem no Zabbix.
		Ex:
		['Your Group']
	"""
	group_list = []
	zb_groups = zm.getUsergroupsList()
	group_name_zb_list = []
	
	#converte lista de dicionarios {name: value, id: value} do zabbix
	#para lista contendo somente nomes do Usergroup
	for item in zb_groups:
		group_name_zb_list.append(item['group'])

	for ad_group in am.getGroupsList(am.FILTER_GROUP_SEARCH_AD):
		zb_group = AdManager().convertAdGroupNameToZabbix(ad_group)

		if zb_group not in group_name_zb_list:
			group_list.append(zb_group)

	return group_list

def zabbixHostgroupsToBeCreated():
	"""
	Metodo que retorna nome dos grupos de host a serem criados no Zabbix, ou seja,
	que existem no AD e ainda nao existem no Zabbix.

	Returns
	-------
	list
		Lista contendo grupos de host que existem no AD nao existem no Zabbix.
		Ex:
		['Your Group']
	"""
	hostgroup_list = []
	zb_hostgroups = zm.getHostgroupsList()
			
	for ad_group in am.getGroupsList(am.FILTER_GROUP_SEARCH_AD):
		ad_hostgroup = AdManager().convertAdGroupNameToZabbix(ad_group)

		if ad_hostgroup not in zb_hostgroups:
			hostgroup_list.append(ad_hostgroup)
		
	return hostgroup_list

def getUsersListToBeCreatedZabbix(zabbix_list, ad_list):
	"""
	Metodo que retorna lista de dicionarios contendo usuarios que existem no AD
	e que ainda nao existem no Zabbix.

	Parameters
	----------
	zabbix_list : list
		Ex:
		[{'group': 'Zabbix administrators', 'id': '7', 'members': [{'id': '1', 'alias': 'Admin'}, {'id': '3', 'alias': 'thiago'}]}]
	ad_list : list
		Ex:
		[{'group': 'Acesso de leitura', 'members': [{'alias': 'thiago', 'name': 'THIAGO MURILO DINIZ'}, 
		{'alias': 'fulano', 'name': 'FULANO OLIVEIRA'}]}]

	Returns
	-------
	list
		Lista contendo dicionarios de usuarios que existem no AD nao existem no Zabbix.
		Ex:
		[{'alias': 'ciclano', 'groups': [{'usrgrpid': '127'}], 'name': 'CICLANO PIRES'}, 
		{'alias': 'robson', 'groups': [{'usrgrpid': '134'}], 'name': 'ROBSON RANDOM'}]
	"""
	zb_users = set()
	for item in zabbix_list:
		for member in item['members']:
			zb_users.add(member['alias'])

	zb_groupid_map = {}
	for ad_item in ad_list:
		ad_group = ad_item['group']
		for zb_item in zabbix_list:
			zb_group = zb_item['group']
			if zb_group == ad_group:
				zb_groupid_map[ad_group] = zb_item['id']

	alias_list = set()
	for ad_item in ad_list:
		ad_group = ad_item['group']
		for member_ad in ad_item['members']:
			for zb_item in zabbix_list:
				zb_group = zb_item['group']
				if member_ad['alias'] not in zb_users:
					alias_list.add(member_ad['alias']) # lista de users a serem criados
				#if zb_group == ad_group and member_ad['alias'] not in zb_item['members']:
					#alias_list.add(zb_item['id']+"-"+member_ad['alias'])

	tobe_created = []
	for alias in alias_list:
		tobe_user = {}
		tobe_user['alias'] = alias
		tobe_user['groups'] = []
		for ad_item in ad_list:
			for member in ad_item['members']:
				if alias == member['alias']:
					member_group = {}
					tobe_user['name'] = member['name']
					member_group['usrgrpid'] = zb_groupid_map[ad_item['group']]
					tobe_user['groups'].append(member_group)
		tobe_created.append(tobe_user)

	return list(tobe_created)
		

def getUsersListToBeUpdatedZabbix(zabbix_list, ad_list):
	"""
	Metodo que retorna lista de dicionarios de grupos e usuarios membros do AD que devem ser atualiza
	dos no Zabbix

	Parameters
	----------
	zabbix_list : list
		Ex:
		[{'group': 'Zabbix administrators', 'id': '7', 'members': [{'id': '1', 'alias': 'Admin'}, {'id': '3', 'alias': 'thiago'}]}]
	ad_list : list
		Ex:
		[{'group': 'Acesso de leitura', 'members': [{'alias': 'thiago', 'name': 'THIAGO MURILO DINIZ'}, 
		{'alias': 'fulano', 'name': 'FULANO OLIVEIRA'}]}]

	Returns
	-------
	list
		Lista contendo dicionarios de grupos e membros do AD que devem ser atualizados no Zabbix.
		Ex:
		[{'group': 'Acesso de leitura', 'id': '127', 'add': ['1463'], 'remove': []}]
	"""
	zb_userid_map = {}
	for item in zabbix_list:
		for member in item['members']:
			zb_userid_map[member['alias']] = member['id']

	update_list = []
	for ad_item in ad_list:
		ad_group = ad_item['group']

		ad_members = []
		for member in ad_item['members']:
			ad_members.append(member['alias'])

		for zb_item in zabbix_list:
			zb_group = zb_item['group']

			zb_members = []
			for member in zb_item['members']:
				zb_members.append(member['alias'])
		
			if zb_group == ad_group and Counter(zb_members) != Counter(ad_members):
				to_update = {}
				to_update['group'] = zb_group
				to_update['id'] = zb_item['id']
				zb_remove = []
				zb_add = []

				for ad_member in ad_members:
					if ad_member not in zb_members:
						zb_add.append(zb_userid_map[ad_member])
	
				for zb_member in zb_members:
					if zb_member not in ad_members:
						zb_remove.append(zb_userid_map[zb_member])

				to_update['add'] = zb_add
				to_update['remove'] = zb_remove
				update_list.append(to_update)

	return list(update_list)


if __name__ == '__main__':

	# Instancia classes e conecta na API Zabbix e no AD
	zm = ZabbixManager()
	zm.connect()
	am = AdManager()
	am.connect()
	
	# Criacao de grupos de host - Nao utilizado, gerenciar no Zabbix.
	#hostgroups_to_be_created = zabbixHostgroupsToBeCreated()
	#zm.createHostgroups(hostgroups_to_be_created)
	
	# Criacao de grupos de usuario
	usergroups_to_be_created = zabbixUsergroupsToBeCreated()
	zm.createUsergroups(usergroups_to_be_created)
	
	# Criacao de usuarios no Zabbix
	ad_dic = am.getGroupMembersDic(am.FILTER_GROUP_SEARCH_AD)	
	zb_dic = zm.getUsergroupsList(True)
	users_tobe_created = getUsersListToBeCreatedZabbix(zb_dic, ad_dic)
	zm.createUsers(users_tobe_created)

	# Sincronizacao usuarios AD e Zabbix
	zb_dic = zm.getUsergroupsList(True)
	users_tobe_updated = getUsersListToBeUpdatedZabbix(zb_dic, ad_dic)
	zm.updateUsers(users_tobe_updated)

	# Desconecta da API Zabbix e do AD
	am.disconnect()
	zm.disconnect()
