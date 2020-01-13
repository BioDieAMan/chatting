#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   newclient.py
@Time    :   2020/01/13 14:17:16
@Author  :   Pan Rongfei
@Version :   1.0
@Contact :   bit_panrongfei@163.com 1838863836@gmail.com
'''

# here put the import lib

import threading
import time
import tkinter as tk
import tkinter.messagebox
import tkinter.scrolledtext as tst
import wave
from socket import *
import os

import cv2
import numpy as np
import pyaudio


class inputportdialog(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.master = master
        # 文本框中输入
        self.portinput = tk.Text(self, width=30, height=5)
        self.portinput.grid(row=0, column=0, columnspan=1)
        self.ipinput = tk.Text(self, width=30, height=5)
        self.ipinput.grid(row=1, column=0, columnspan=1)
        tk.Button(self, text='确定', command=self.setIP).grid(row=1, column=2)
        self.grid()

    def setIP(self):
        global serverport
        global serverip
        # 获取文本内容
        serverport = self.portinput.get('1.0', 'end-1c')
        serverport = int(serverport)
        serverip = self.ipinput.get('1.0', 'end-1c')
        serverip = int(serverip)
        # 销毁窗口
        self.master.destroy()


class Application(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def createWidgets(self):
        # ----------------定义语音流---------------------
        self.send_message = ''
        self.receive_message = ''
        self.audio = pyaudio.PyAudio()
        self.audio1 = pyaudio.PyAudio()
        self.audio_stream = self.audio.open(format=pyaudio.paInt16,
                                            channels=2,
                                            rate=44100,
                                            input=True,
                                            frames_per_buffer=1024)
        self.stream = self.audio1.open(format=pyaudio.paInt16,
                                       channels=2,
                                       rate=44100,
                                       output=True)
        self.frames = []
        # 显示聊天窗口
        self.clienttext = tst.ScrolledText(self, width=50, height=15)
        self.clienttext.grid(row=0, column=0, rowspan=1, columnspan=4)
        self.clienttext.config(state='disabled')
        # 定义标签，改变字体颜色
        self.clienttext.tag_config('server', foreground='red')
        self.clienttext.tag_config('guest', foreground='blue')

        # 编辑输入框
        self.inputText = tk.Text(self, width=40, height=7)
        self.inputText.grid(row=1, column=0, columnspan=1)
        # 定义快捷键，按下回车即可发送消息
        self.inputText.bind("<KeyPress-Return>", self.textSendReturn)

        # 发送按钮，所有按钮包装在Frame容器内
        frames = tk.Frame(self)
        frames.grid(row=1, column=3)
        # 文字发送
        self.btnSend = tk.Button(frames, text='send', command=self.textSend)
        self.btnSend.pack(fill='x')
        # 语音录制及发送
        self.recordstart = tk.Button(frames,
                                     text='record',
                                     command=self.wav_start)
        self.recordstart.pack(fill='x')
        self.recordend = tk.Button(frames,
                                   text='sendaudio',
                                   command=self.wavend)
        self.recordend.pack(fill='x')
        # 视频通信
        self.vedio_button = tk.Button(frames, text='video', command=self.video)
        self.vedio_button.pack(fill='x')
        # 语音播放按钮
        self.audio_button = tk.Button(self.clienttext,
                                      text='display',
                                      command=self.display_audio)
        # 退出
        self.out = tk.Button(frames, text='quit', command=self.logout)
        self.out.pack(fill='x')
        # 开启线程
        t = threading.Thread(target=self.getInfo)
        t.start()

    # 退出程序
    def logout(self):
        os._exit(0)

    # 开始发送视频
    def video(self):
        video_thread = threading.Thread(target=self.video_send)
        video_thread.start()

    # 视频发送
    def video_send(self):
        cap = cv2.VideoCapture(0)
        encode_para = [int(cv2.IMWRITE_JPEG_QUALITY), 15]
        # 压缩参数
        while cap.isOpened():
            try:
                ret, frame = cap.read()
                time.sleep(0.1)  # 时延保证稳定性
                result, imgencode = cv2.imencode('.jpg', frame, encode_para)
                data = np.array(imgencode)
                string_data = np.ndarray.tostring(data)
                video_header = 'video' + '0' * (15 - len(str(
                    len(string_data)))) + str(len(string_data)) + '###'
                video_header = bytes(video_header, encoding='utf8')
                video_message = video_header + string_data
                clientSocket.sendall(video_message)
            except:
                break
        cap.release()
        cv2.destroyAllWindows()

    # 开启语音录制
    def wav_start(self):
        thread = threading.Thread(target=self.wavstart)
        thread.start()

    # 录制语音
    def wavstart(self):
        # 循环获取语音
        self.audio = pyaudio.PyAudio()
        self.audio_stream = self.audio.open(format=pyaudio.paInt16,
                                            channels=2,
                                            rate=44100,
                                            input=True,
                                            frames_per_buffer=1024)
        self.frames = []
        while True:
            try:
                if self.audio_stream.is_stopped() is True:
                    break
                data = self.audio_stream.read(1024)
                self.frames.append(data)
            except:
                break

    # 录制结束，发送语音
    def wavend(self):
        # --------关闭语音获取并发送协议和语音流---------------
        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio.terminate()
        # ---------音频发送-----------------------------------
        self.frames = b''.join(self.frames)
        self.send_message = bytes(
            ('audio' + '0' * (15 - len(str(len(self.frames)))) +
             str(len(self.frames)) + '###'),
            encoding='utf8') + self.frames
        clientSocket.sendall(self.send_message)

    def display_audio(self):
        # ----------------音频播放------------------------
        data = self.wf.readframes(1024)
        while data != b'':
            self.stream.write(data)
            data = self.wf.readframes(1024)
        self.stream.close()
        self.audio1.terminate()

    # 发送文字
    def textSend(self):
        string = self.inputText.get('1.0', 'end-1c')
        if string != "" and string is not None:
            # 显示发送时间和发送消息
            timemsg = '客户端' + time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime()) + '\n'
            # -----------------------用户界面内容更新------------
            # 通过设置state属性设置clienttext可编辑
            self.clienttext.config(state='normal')
            self.clienttext.insert(tk.INSERT, '\n' + timemsg, 'guest')
            self.clienttext.insert(tk.INSERT, string + '\n')
            # 将滚动条拉到最后显示最新消息
            self.clienttext.see(tk.END)
            # 通过设置state属性设置clienttext不可编辑
            self.clienttext.config(state='disabled')
            self.inputText.delete(0.0, tk.END)
            # ---------------信息发送--------------------------
            self.send_message = 'word' + '0' * (
                16 - len(str(len(string)))) + str(len(string)) + '###' + string
            clientSocket.send(bytes(self.send_message, encoding='utf8'))
            # ------------------------------------------------
        else:
            tk.messagebox.showinfo('警告', "不能发送空白信息！")

    def getInfo(self):
        global clientSocket
        while True:
            recMessage = clientSocket.recv(1024)
            # total_data 中为数据内容
            total_data = recMessage[23:]
            try:
                # 将header提取用作后续处理
                self.receive_message = recMessage[0:23].decode()
            except:
                continue
            # --------------接收数据处理-----------------------------
            if self.receive_message == '':
                break
            recTime = '服务端' + time.strftime('%Y-%m-%d %H:%M:%S',
                                            time.localtime()) + '\n'
            # 通过header判断数据种类
            # 文字
            if self.receive_message.find('word') != -1:
                self.clienttext.config(state='normal')
                # server作为标签,改变字体颜色
                self.clienttext.insert(tk.END, recTime, 'server')
                self.clienttext.insert(tk.END, total_data.decode())
                # 将滚动条拉到最后显示最新消息
                self.clienttext.see(tk.END)
                self.clienttext.config(state='disabled')
            # 语音
            elif self.receive_message.find('audio') != -1:
                self.clienttext.config(state='normal')
                self.clienttext.insert(tk.END, '\n' + recTime, 'server')
                audio_length = self.receive_message.split('###')[0]
                audio_length = audio_length[5:20]
                audio_length = int(audio_length)
                self.receive_message = total_data
                list_frames = []
                list_frames.append(self.receive_message)
                recv_length = 1024
                while recv_length < audio_length:
                    new_message = clientSocket.recv(9999)
                    recv_length += len(new_message)
                    list_frames.append(new_message)
                self.wf = wave.open('output.wav', 'wb')
                self.wf.setnchannels(2)
                self.wf.setsampwidth(
                    self.audio.get_sample_size(pyaudio.paInt16))
                self.wf.setframerate(44100)
                self.wf.writeframes(b''.join(list_frames))
                self.wf.close()
                self.wf = wave.open('output.wav', 'rb')
                self.audio1 = pyaudio.PyAudio()
                self.stream = self.audio1.open(
                    format=self.audio1.get_format_from_width(
                        self.wf.getsampwidth()),
                    channels=2,
                    rate=self.wf.getframerate(),
                    frames_per_buffer=1024,
                    output=True)
                self.clienttext.window_create(tk.INSERT,
                                              window=self.audio_button)
                self.clienttext.see(tk.END)
            # 视频
            elif self.receive_message.find('video') != -1:
                video_length = self.receive_message.split('###')[0]
                video_length = video_length[5:20]
                video_length = int(video_length)
                recv_video_length = 1024
                video_frame = total_data
                while recv_video_length < video_length:
                    new_video_data = clientSocket.recv(8000)
                    recv_video_length += len(new_video_data)
                    video_frame += new_video_data
                dataaa = np.frombuffer(video_frame, np.uint8)
                # 将获取到的字符流数据转换成1维数组
                decimg = cv2.imdecode(dataaa, cv2.IMREAD_COLOR)
                # 将数组解码成图像
                cv2.imshow('SERVER', decimg)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    # 将文字发送按键与回车键绑定
    def textSendReturn(self, event):
        if event.keysym == "Return":
            self.textSend()


# 指定服务器地址，端口
servername = '101.201.69.224'
# 服务器ip，101.201.69.224为项目期间使用IP
serverport = None
# 端口

get_port = tk.Tk()
get_port.title('输入目标端口及IP')
portdialog = inputportdialog(get_port)
portdialog.mainloop()
clientSocket = socket(AF_INET, SOCK_STREAM)

clientSocket.connect((servername, serverport))
root = tk.Tk()
root.title('客户端')

app = Application(master=root)
app.mainloop()
