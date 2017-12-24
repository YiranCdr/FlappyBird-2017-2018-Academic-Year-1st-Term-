# -*- coding: utf-8 -*-
import socket, netstream
connected = False
sock = None

serialID = 0            #server向客户端发回的序列ID号
isSet = False

logInState = 0
connected = False

def connect(gameScene):
    global connected, sock, isRead
    if connected:
        return connected
    #connect server
    host = "127.0.0.1"
    port = 9234
    sock = socket.socket()
    try: 
    	sock.connect((host, port))
    except:
    	connected = False
    	return connected
    
    connected = True
    # return connected

    #始终接收服务端消息
    def receiveServer(dt):
        global connected, serialID, isRead
        # logInState = netstream.getLogInState()
        if not connected:
            return
        data = netstream.read(sock)
        if data == netstream.TIMEOUT or data == netstream.CLOSED or data == netstream.EMPTY:
            return
        
        #客户端SID
        if 'sid' in data:
            # print ('sid')
            import game_controller
            serialID = data['sid']

        # 用于broadcast
        if 'notice_content' in data:
            import game_controller
            game_controller.showContent(data['notice_content']) #show+Content is from game_controller

        # 根据Server返回信息调用showLogInMessage显示对应信息
        if 'error1' in data:
            print data['error1']
            logInState = 1
            import game_controller
            game_controller.showLogInMessange(logInState)

        if 'create' in data:
            print data['create']
            import game_controller
            logInState = 2
            game_controller.showLogInMessange(logInState)

        # if 'error1-1' in data:
        #     print data['error1-1']
        #     logInState = 3
        #     import game_controller
        #     game_controller.showLogInMessange(logInState)
            
        if 'error2' in data:
            print data['error2']
            logInState = 6
            import game_controller
            game_controller.showLogInMessange(logInState)

        if 'error2-1' in data:
            print data['error2-1']
            logInState = 7
            import game_controller
            game_controller.showLogInMessange(logInState)

        if 'error3' in data:
            print data['error3']
            logInState = 8
            import game_controller
            game_controller.showLogInMessange(logInState)

        if 'successfully' in data:
            print data['successfully']
            logInState = 9
            import game_controller
            game_controller.showLogInMessange(logInState)

        if 'log_out' in data:
            print ("log_out")
            import game_controller
            game_controller.doLogOut()

        if 'championAccount' in data:
            print ("championAccount")
            import game_controller
            name = data['championAccount']
            score = data['championScore']
            game_controller.receive_champion(name, score)

        # sock = None

        
    gameScene.schedule(receiveServer)
    return connected

def get_send_data():
    send_data = {}
    send_data['sid'] = serialID
    return send_data

#向server请求公告
# def request_notice():
#     send_data = get_send_data()
#     send_data['notice'] = 'request notice'
#     netstream.send(sock, send_data)

# 向server请求best信息
def request_champion(difficulty):
    send_data = get_send_data()
    send_data['requestChampion'] = 'requestChampion'
    send_data['level'] = difficulty
    netstream.send(sock, send_data)

# 向Server发送登录信息
def send_log_in_message(sendState, account, password):
    send_data = get_send_data()
    send_data['sendState'] = sendState
    send_data['account'] = account
    send_data['password'] = password
    netstream.send(sock, send_data)

# 向server发送登出信息
def send_log_out():
    send_data = get_send_data()
    send_data['log_out'] = True
    netstream.send(sock, send_data)

# 向server发送分数信息
def send_score(account, password, score, time, level):
    send_data = get_send_data()
    print 'send_score', score, account
    send_data['account'] = account
    send_data['password'] = password
    send_data['score'] = score
    send_data['time'] = time
    send_data['level'] = level
    netstream.send(sock, send_data)

# 向server发送broadcast信息
def send_notice(notice_send, account):
    send_data = get_send_data()
    send_data['notice'] = notice_send
    send_data['account'] = account
    netstream.send(sock, send_data)