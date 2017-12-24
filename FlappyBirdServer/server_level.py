# -*- coding: utf-8 -*-
import socket, select, netstream, random, pickle, os, traceback, file_operation_level, types, thread, pyhooked

HOST = "127.0.0.1"
disconnected_list = []  # 断开连接的客户端列表
onlineUser = {}
sid = 0

REGISTER = 1
LOG_IN = 2

EASY = 1
MID = 2
HARD = 3

ON = 1
OFF = 0
server_state = OFF


def judge_input_type(ju):
	if type(ju)!= type('str'):
		print 'Wrong type. str without '' please. '
		return False
	return True


def checkKey(event):
	if isinstance(event, pyhooked.KeyboardEvent):
		global server_state
		if event.key_code == 123:  # Enter - F12
			if server_state == OFF:
				server_state = ON
			else:
				global sid, onlineUser, cInfo
				sid = 0
				onlineUser = {}
				cInfo = []
				print 'server reset. '


def checkKey_thread():
	hook_manager = pyhooked.Hook()
	hook_manager.handler = checkKey
	hook_manager.hook()


tmp_judge = raw_input('Do you want to add your BlackList? [y/n]')
while judge_input_type(tmp_judge) == False:
	tmp_judge = raw_input('Do you want to add your BlackList? [y/n]')

while tmp_judge != 'y' and tmp_judge != 'Y' and tmp_judge != 'n' and tmp_judge != 'N':
	print 'Invalid choice. '
	tmp_judge = raw_input('Do you want to add your BlackList? [y/n]')

while tmp_judge == 'y' or tmp_judge == 'Y':
	print 'Add into Black List: '
	black_account = raw_input("UserName: ")
	while judge_input_type(black_account) == False:
		black_account = raw_input("UserName: ")
	black_password = '0'
	if file_operation_level.search_user_black_list(black_account) == file_operation_level.NO_SUCH_USER:
		file_operation_level.write_new_user_black_list(black_account, black_password)
		print 'Add into black list successfully. '
	else:
		print 'Account already exist in black list. '

	tmp_judge = raw_input('Do you want to add your BlackList? [y/n]')
	while judge_input_type(tmp_judge) == False:
		tmp_judge = raw_input('Do you want to add your BlackList? [y/n]')
	while tmp_judge != 'y' and tmp_judge != 'Y' and tmp_judge != 'n' and tmp_judge != 'N':
		print 'Invalid choice. '
		tmp_judge = raw_input('Do you want to add your BlackList? [y/n]')


print 'Press F12 to start/reset server. \n' \
	  'You will see a statement to inform you that the server has started. \n' \
	  'If nothing work, press Fn and F12. '


thread.start_new_thread(checkKey_thread, ())
while server_state == OFF:
	xxx = 1  # nonsence.

s = socket.socket()
host = HOST
port = 9234

s.bind((host, port))
s.listen(4)

inputs = []
inputs.append(s)
print 'server start! listening host:', host, ' port:', port

while inputs:
	try:
		rs, ws, es = select.select(inputs, [], [])
		for r in rs:
			if r is s:
				print 'sid:', sid
				# accept
				connection, addr = s.accept()
				print 'Got connection from' + str(addr)
				inputs.append(connection)
				sendData = {}
				sendData['sid'] = sid
				netstream.send(connection, sendData)
				cInfo = {}
				cInfo['connection'] = connection
				cInfo['addr'] = str(addr)
				cInfo['ready'] = False
				onlineUser[sid] = cInfo
				print(str(onlineUser))
				sid += 1
			else:
				# receive data
				recvData = netstream.read(r)
				# print 'Read data from ' + str(r.getpeername()) + '\tdata is: ' + str(recvData)
				# socket关闭
				if recvData == netstream.CLOSED or recvData == netstream.TIMEOUT:
					if r.getpeername() not in disconnected_list:
						print str(r.getpeername()) + 'disconnected'
						disconnected_list.append(r.getpeername())
				else:  # 根据收到的request发送response
					if 'sid' not in recvData:
						continue
					if type(recvData['sid']) != type(1):
						continue
					print recvData

					number = recvData['sid']
					if 'notice' in recvData and 'account' in recvData:

						# judge if type is acceptable.
						if type(recvData['notice']) != types.UnicodeType or type(
								recvData['account']) != types.UnicodeType:
							continue

						print(recvData['notice'])
						print 'receive notice request from user id:', number
						broadcast_content = "Broadcast: " + recvData['notice']
						sendData = {"notice_content": broadcast_content, 'sid': number, 'account': recvData['account']}

						for online_sid in onlineUser:
							number = online_sid
							sendData['sid'] = number
							netstream.send(onlineUser[number]['connection'], sendData)
						number = recvData['sid']
					elif 'sendState' in recvData and 'account' in recvData and 'password' in recvData:

						# judge if type is acceptable.
						if type(recvData['account']) != types.UnicodeType:
							print 'type error'
							continue
						if type(recvData['password']) != types.UnicodeType:
							print 'type error'
							continue
						if type(recvData['sendState']) != type(1):
							print 'type error'
							continue

						print 'Receive: account ', recvData['account'], 'password ', recvData['password']
						if recvData['sendState'] == REGISTER:
							# if file_operation_level.search_user_black_list(recvData['account']) != file_operation_level.NO_SUCH_USER:
							# 	print 'error: Account in black list. '
							# 	sendData = {'error1-1': 'Account in black list. ', 'sid': number}
							# 	netstream.send(onlineUser[number]['connection'], sendData)
							if file_operation_level.search_user(
									recvData['account']) == file_operation_level.NO_SUCH_USER:
								file_operation_level.write_new_user(recvData['account'], recvData['password'])
								sendData = {'create': 'new account finished. ', 'sid': number}
								netstream.send(onlineUser[number]['connection'], sendData)
							# print 'create new account finished. '
							else:
								print 'error: Account exist. '
								sendData = {'error1': 'Account exist. ', 'sid': number}
								netstream.send(onlineUser[number]['connection'], sendData)
						elif recvData['sendState'] == LOG_IN:
							if file_operation_level.search_user_black_list(recvData['account']) != file_operation_level.NO_SUCH_USER:
								print 'error: Account in black list. '
								sendData = {'error2-1': 'Account in black list. ', 'sid': number}
								netstream.send(onlineUser[number]['connection'], sendData)
							elif file_operation_level.search_user(
									recvData['account']) == file_operation_level.NO_SUCH_USER:
								print 'error: No such account. '
								sendData = {'error2': 'No such account. ', 'sid': number}
								netstream.send(onlineUser[number]['connection'], sendData)
							elif not file_operation_level.check_password(recvData['account'], recvData['password']):
								print 'error: Wrong password. '
								sendData = {'error3': 'Wrong passowrd. ', 'sid': number}
								netstream.send(onlineUser[number]['connection'], sendData)
							else:
								print 'log in successfully! '
								sendData = {'successfully': 'log in successfully!', 'sid': number}
								netstream.send(onlineUser[number]['connection'], sendData)

					elif 'log_out' in recvData:

						# judge if type is acceptable.
						if type(recvData['log_out']) != type(True):
							print 'type error'
							continue

						sendData = {'log_out': True, 'sid': number}
						netstream.send(onlineUser[number]['connection'], sendData)
						print 'log out - sid: ', number

					elif 'account' in recvData and 'password' in recvData and 'score' in recvData and 'time' in recvData and 'level' in recvData:

						# judge if type is acceptable.
						if type(recvData['account']) != types.UnicodeType or type(
								recvData['password']) != types.UnicodeType or type(recvData['score']) != type(
							1) or type(recvData['time']) != type(1) or type(recvData['level']) != type(1) or \
								recvData['level'] < EASY or recvData['level'] > HARD:
							print 'type error'
							continue

						# to protect data, the program need to check.
						if not file_operation_level.check_password(recvData['account'], recvData['password']):
							continue
						print 'send_score'
						final_best_score, final_best_time = file_operation_level.update_record(recvData['account'],
																							   recvData['score'],
																							   recvData['time'],
																							   recvData['level'])
						sendData = {'account': recvData['account'], 'best_score': final_best_score,
									'best_time': final_best_time, 'sid': number}
						netstream.send(onlineUser[number]['connection'], sendData)

					elif 'requestChampion' in recvData and 'level' in recvData:

						if type(recvData['level']) != type(1) or recvData['level'] < EASY or recvData['level'] > HARD:
							print 'type error'
							continue
						print 'champion request'
						champion_account, champion_score, champion_time = file_operation_level.find_champion(
							recvData['level'])
						sendData = {'championAccount': champion_account, 'championScore': champion_score,
									'championTime': champion_time, 'sid': number}
						netstream.send(onlineUser[number]['connection'], sendData)

	except Exception:
		traceback.print_exc()
		print 'Error: socket 链接异常'
