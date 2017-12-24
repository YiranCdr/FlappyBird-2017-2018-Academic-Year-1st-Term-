# -*- coding: utf-8 -*-
import socket
import threading
import time
import random
from lib import netstream,game_controller

host = "127.0.0.1"
port = 9234
total_thread_num = 1000
user_time = [0]*total_thread_num*6
total_num = [0]*total_thread_num*6
total_action = [0]*total_thread_num

REGISTER = 1
LOG_IN = 2

EASY = 1
MID = 2
HARD = 3


def anotice(sock,serialID,account):
	send_data = {}
	send_data['sid'] = serialID
	send_data['notice'] = 'request notice'
	send_data['account'] = account
	netstream.send(sock,send_data)

def aregister(sock,serialID,account):
	send_data = {}
	send_data['sid'] = serialID
	send_data['sendState'] = REGISTER
	send_data['account'] = account
	send_data['password'] = '000111'
	netstream.send(sock,send_data)

def alog_in(sock,serialID,account):
	send_data = {}
	send_data['sid'] = serialID
	send_data['sendState'] = LOG_IN
	send_data['account'] = account
	send_data['password'] = '000111'
	netstream.send(sock, send_data)

def amy_score(sock,serialID,account,mytime):
	send_data = {}
	send_data['sid'] = serialID
	send_data['account'] = account
	send_data['password'] = '000111'
	send_data['score'] = random.randint(1,100)
	send_data['time'] = mytime
	k = random.randint(1,3)
	if k == 1:
		send_data['level'] = EASY
	elif k == 2:
		send_data['level'] = MID
	else:
		send_data['level'] = HARD
	netstream.send(sock,send_data)

def aget_champion(sock,serialID):
	send_data = {}
	send_data['sid'] = serialID
	k = random.randint(1, 3)
	if k == 1:
		send_data['level'] = EASY
	elif k == 2:
		send_data['level'] = MID
	else:
		send_data['level'] = HARD
	send_data['requestChampion'] = 'I want to be NO.1'
	netstream.send(sock, send_data)

def alog_out(sock,serialID):
	send_data = {}
	send_data['sid'] = serialID
	send_data['log_out'] = True
	netstream.send(sock, send_data)

def th_test(thread_num, user_time):
	#connect server
	s_time = time.time()
	serialID = 0
	get_id = 1
	mytime = 0
	sock = socket.socket()
	try:
		sock.connect((host,port))
	except:
		return
	while(1):
		data = netstream.read(sock)
		if data == netstream.TIMEOUT or data == netstream.CLOSED or data == netstream.EMPTY:
			continue
		if get_id == 1:
			if 'sid' in data:
				serialID = data['sid']
				account = 'threadnum'+str(thread_num)
				get_id = 0
				e_time = time.time()
				c_time = e_time - s_time
				user_time[(thread_num - 1) * 6] = c_time
				total_num[(thread_num - 1) * 6] = 1
				total_action[thread_num-1] = c_time + total_action[thread_num-1]
				time.sleep(5)
				s_time = time.time()
				aregister(sock,serialID,account)
		else:
			if 'create' in data or 'error1' in data:
				e_time = time.time()
				c_time = e_time-s_time
				user_time[(thread_num-1)*6+1] = c_time
				total_num[(thread_num - 1) * 6+1] = 1
				total_action[thread_num - 1] = c_time + total_action[thread_num - 1]
				time.sleep(1)
				s_time = time.time()
				alog_in(sock,serialID,account)
			elif 'successfully' in data or 'error2' in data or 'error3' in data:
				e_time = time.time()
				c_time = e_time - s_time
				user_time[(thread_num-1)*6+2] = c_time
				total_num[(thread_num - 1) * 6+2] = 1
				total_action[thread_num - 1] = c_time + total_action[thread_num - 1]
				mytime = random.randint(1, 15)
				time.sleep(mytime)
				s_time = time.time()
				amy_score(sock, serialID, account, mytime)
			elif 'best_score' in data:
				e_time = time.time()
				c_time = e_time - s_time
				user_time[(thread_num-1)*6+3] = c_time
				total_num[(thread_num - 1) * 6+3] = 1
				total_action[thread_num - 1] = c_time + total_action[thread_num - 1]
				time.sleep(1)
				s_time = time.time()
				aget_champion(sock,serialID)
			elif 'championAccount' in data:
				e_time = time.time()
				c_time = e_time - s_time
				user_time[(thread_num-1)*6+4] = c_time
				total_num[(thread_num - 1) * 6+4] = 1
				total_action[thread_num - 1] = c_time + total_action[thread_num - 1]
				time.sleep(1)
				s_time = time.time()
				alog_out(sock,serialID)
			elif 'log_out' in data:
				e_time = time.time()
				c_time = e_time - s_time
				user_time[(thread_num-1)*6+5] = c_time
				total_num[(thread_num - 1) * 6+5] = 1
				total_action[thread_num - 1] = c_time + total_action[thread_num - 1]
				return



if __name__ == '__main__':
	f = open('test_users.txt', 'a')
	f.writelines(['------------------------Test Start------------------------', '\n'])
	f.close()

	thread_num = 1
	total_time = 0
	total_num_inall = 0
	total_action_time = 0;

	for i in range(total_thread_num):
		athread = threading.Thread(target=th_test, args=(thread_num, user_time))
		athread.start()
		thread_num = thread_num + 1

	time.sleep(180)
	for i in range(6*total_thread_num):
		total_time = total_time + user_time[i]
		total_num_inall = total_num_inall + total_num[i]
	for i in range(total_thread_num):
		total_action_time = total_action_time + total_action[i];
	avg_time = total_time / total_num_inall
	throughput = total_num_inall / total_time
	avg_act_time = total_action_time / total_thread_num
	f = open('test_users.txt', 'a')
	f.writelines(['-----------------------Test result-----------------------', '\n'])
	f.writelines(['Thread number: ', str(total_thread_num), '\n'])
	f.writelines(['Action Transaction: ', str(round(avg_act_time, 15)), 's\n'])
	f.writelines(['Handling events: ', str(total_num_inall), '\n'])
	f.writelines(['Average time: ', str(round(avg_time, 15)), 's\n'])
	f.writelines(['Throughput rate: ', str(round(throughput, 3)), '\n'])
	f.writelines(['------------------------Test over-------------------------', '\n'])
	f.close()
	print('test over')