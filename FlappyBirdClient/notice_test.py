# -*- coding: utf-8 -*-
import socket
import threading
import time
import random
from lib import netstream,game_controller

host = "127.0.0.1"
port = 9234
total_thread_num = 1000
notice_time = [0]*total_thread_num
notice_num = [0]*total_thread_num


def anotice(sock,serialID,act_pswd,account):
	send_data = {}
	send_data['sid'] = serialID
	send_data['notice'] = 'request notice'
	send_data['account'] = account
	netstream.send(sock,send_data)


def th_notice(thread_num, notice_time):
	#connect server
	s_time = time.time()
	serialID = 0
	sock = socket.socket()
	try:
		sock.connect((host,port))
	except:
		#f=open('test.txt', 'a')
		#f.writelines(['NO.',str(thread_num),' thread connect faild\n'])
		#print('NO.%d thread connect faild'%(thread_num))
		#f.close()
		return
	while(1):
		data = netstream.read(sock)
		if data == netstream.TIMEOUT or data == netstream.CLOSED or data == netstream.EMPTY:
			continue
		if 'sid' in data:
			serialID = data['sid']
			account = "threadnum"+str(thread_num)
			anotice(sock,serialID,thread_num-1,account)
		if 'notice_content' in data:
			e_time = time.time()
			c_time = e_time - s_time
			notice_time[thread_num-1] = c_time
			notice_num[thread_num-1] = 1
			#print 'NO.%d thread get notice successfully cost time:%.15fs\n'%(thread_num,c_time)
			return


if __name__ == '__main__':
	f=open('test.txt', 'a')
	f.writelines(['----------------------Test for notice---------------------', '\n'])
	f.close()
	thread_num = 1
	total_time = 0
	for i in range(total_thread_num):
		athread = threading.Thread(target = th_notice,args = (thread_num, notice_time))
		athread.start()
		thread_num = thread_num+1
	time.sleep(30)
	notice_number = 0
	for i in range(total_thread_num):
		notice_number = notice_number+notice_num[i]
		total_time = total_time + notice_time[i]
	avg_time = total_time / notice_number
	throughput = notice_number / total_time
	f=open('test.txt', 'a')
	f.writelines(['------------------------Notice test-----------------------','\n'])
	f.writelines(['thread number: ', str(total_thread_num), '\n'])
	f.writelines(['Handling events: ', str(notice_number), '\n'])
	f.writelines(['average time: ', str(round(avg_time, 15)),'s\n'])
	f.writelines(['throughput rate: ',str(round(throughput,3)),'\n'])
	f.writelines(['----------------------Notice test over--------------------', '\n'])
	f.close()

	print("test over")






