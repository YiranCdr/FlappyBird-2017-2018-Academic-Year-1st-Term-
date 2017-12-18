# -*- coding: utf-8 -*-
# TODO
# 在数据库中查找，返回行数
# 若不存在，添加新用户
# 若存在，审核密码是否正确
# 游戏结束，记录战绩
#
from __future__ import print_function
import os
MIN_SCORE = 0
MIN_TIME = 0
NO_SUCH_USER = -1

EASY = 1
MID = 2
HARD = 3

def search_user(goal_name):
    lineNum = NO_SUCH_USER
    if not os.path.isfile('user_data_level.txt'):
        with open('user_data_level.txt', 'w'):
            print ('user_data_level.txt has been created. ')
            return lineNum
    with open('user_data_level.txt', 'r') as user_data_file:
        tmp_lineNum = 0
        for line in user_data_file.readlines():
            if line == '\n':
                tmp_lineNum = tmp_lineNum + 1
                continue
            (user_name, password, socre_str1, time_str1, socre_str2, time_str2, socre_str3, time_str3) = line.split(':', 7)
            user_name = user_name.strip()
            if user_name == goal_name:
                lineNum = tmp_lineNum
                return lineNum
            tmp_lineNum = tmp_lineNum + 1
        return NO_SUCH_USER

def write_new_user(user_name, password):
    with open("user_data_level.txt", "a") as user_data_file:
        # username + score + time
        print(user_name + ':' + password + ':0' + ':0' + ':0' + ':0' + ':0' + ':0' , file = user_data_file)

# Please use this function once you have checked that the user exist.
def check_password(userName, password):
    lineNum = search_user(userName)
    with open('user_data_level.txt', 'r') as user_data_file:
        tmp_lineNum = 0
        for line in user_data_file.readlines():
            if lineNum == tmp_lineNum:
                (file_user_name, file_password, file_socre_str1, file_time_str1, file_socre_str2, file_time_str2, file_socre_str3, file_time_str3) = line.split(':', 7)
                file_password = file_password.strip()
                if password == file_password:
                    return True
                else:
                    return False
            tmp_lineNum = tmp_lineNum + 1

# Please use this function once you have checked that the user exist.
def update_record(userName, score, time, level):
    global my_best_score
    global my_best_time
    lineNum = search_user(userName)
    finalData = ''
    with open('user_data_level.txt', 'r') as user_data_file:
        tmp_lineNum = 0
        for line in user_data_file.readlines():
            if lineNum == tmp_lineNum:
                (file_userName, file_password, file_score_str1, file_time_str1, file_score_str2, file_time_str2, file_score_str3, file_time_str3) = line.split(':', 7)

                global file_score_str
                global file_time_str
                if level == EASY:
                    file_score_str = file_score_str1
                    file_time_str = file_time_str1
                if level == MID:
                    file_score_str = file_score_str2
                    file_time_str = file_time_str2
                if level == HARD:
                    file_score_str = file_score_str3
                    file_time_str = file_time_str3

                file_userName = file_userName.strip()
                file_password = file_password.strip()
                file_score_str = file_score_str.strip()
                file_time_str = file_time_str.strip()
                file_score = int(file_score_str)
                file_time = int(file_time_str)
                my_best_score = file_score
                my_best_time = file_time
                if score > file_score:
                    file_score_str = str(score)
                    my_best_score = score
                if time > file_time:
                    file_time_str = str(time)
                    my_best_time = time

                if level == EASY:
                    file_score_str2 = file_score_str2.strip()
                    file_time_str2 = file_time_str2.strip()
                    file_score_str3 = file_score_str3.strip()
                    file_time_str3 = file_time_str3.strip()
                    finalData += file_userName + ':' + file_password + ':' + file_score_str + ':' + file_time_str + ':' + file_score_str2 + ':' + file_time_str2 + ':' + file_score_str3 + ':' + file_time_str3 + '\n'
                elif level == MID:
                    file_score_str1 = file_score_str1.strip()
                    file_time_str1 = file_time_str1.strip()
                    file_score_str3 = file_score_str3.strip()
                    file_time_str3 = file_time_str3.strip()
                    finalData += file_userName + ':' + file_password + ':' + file_score_str1 + ':' + file_time_str1 + ':' + file_score_str + ':' + file_time_str + ':' + file_score_str3 + ':' + file_time_str3 + '\n'
                elif level == HARD:
                    file_score_str1 = file_score_str1.strip()
                    file_time_str1 = file_time_str1.strip()
                    file_score_str2 = file_score_str2.strip()
                    file_time_str2 = file_time_str2.strip()
                    finalData += file_userName + ':' + file_password + ':' + file_score_str1 + ':' + file_time_str1 + ':' + file_score_str2 + ':' + file_time_str2 + ':' + file_score_str + ':' + file_time_str + '\n'

            else:
                finalData += line
            tmp_lineNum += 1
    with open('user_data_level.txt', 'w') as user_data_file:
        print(finalData, end = '', file = user_data_file)
    return my_best_score, my_best_time


def find_champion(level):
    champion_account = 'a'
    champion_score = 0
    champion_time = 0
    with open('user_data_level.txt', 'r') as user_data_file:
        for line in user_data_file.readlines():
            (file_userName, file_password, file_score_str1, file_time_str1, file_score_str2, file_time_str2, file_score_str3, file_time_str3) = line.split(':', 7)
            file_userName = file_userName.strip()

            global file_score
            global file_time

            if level == EASY:
                file_score_str = file_score_str1.strip()
                file_time_str = file_time_str1.strip()
                file_score = int(file_score_str)
                file_time = int(file_time_str)
            if level == MID:
                file_score_str = file_score_str2.strip()
                file_time_str = file_time_str2.strip()
                file_score = int(file_score_str)
                file_time = int(file_time_str)
            if level == HARD:
                file_score_str = file_score_str3.strip()
                file_time_str = file_time_str3.strip()
                file_score = int(file_score_str)
                file_time = int(file_time_str)


            if champion_score <= file_score:
                if champion_score < file_score:
                    champion_account = file_userName
                    champion_score = file_score
                    champion_time = file_time
                if champion_score == file_score:
                    if champion_time < file_time:
                        champion_account = file_userName
                        champion_score = file_score
                        champion_time = file_time
        return champion_account, champion_score, champion_time

# 用法示例
def myDemo():
    if search_user('Yiran') == NO_SUCH_USER:
        write_new_user('Yiran', '123456')
    if search_user('zok') == NO_SUCH_USER:
        write_new_user('zok', '6666660102')
    if search_user('Yiran') > NO_SUCH_USER:
        print (check_password('Yiran', '000000'))
        print(check_password('Yiran', '123456'))
    if search_user('zok') > NO_SUCH_USER:
        update_record('zok', 3, 8, HARD)
    if search_user('YiranCdr') == NO_SUCH_USER:
        write_new_user('YiranCdr', '11111111123456')
    if search_user('YiranCdr') > NO_SUCH_USER:
        update_record('YiranCdr', 3, 4, HARD)
        update_record('YiranCdr', 3, 4, MID)
    (ca, cs, ct) = find_champion(HARD)
    print (ca)
    (ca, cs, ct) = find_champion(MID)
    print (ca)

if __name__ == '__main__':
    myDemo()