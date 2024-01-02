
# import tkinter as tk

# global x, y
# x = 0
# y = 0
# def on_mouse_down(event):
#     x = event.x
#     y = event.y
#     print("down")
 
# def on_mouse_move(event):
#     # canvas.move(rectangle, event.x - x, event.y - y)
#     x = event.x
#     y = event.y
#     print("move")
 
# def on_mouse_up(event):
#     # canvas.unbind("<B1-Motion>")
#     print("up")
 
# root = tk.Tk()
# canvas = tk.Canvas(root, width=400, height=400)
# canvas.pack()
 
# rectangle = canvas.create_rectangle(50, 50, 150, 150, fill="blue")
 
# canvas.bind("<B1-Motion>", on_mouse_move)
# canvas.bind("<Button-1>", on_mouse_down)
# canvas.bind("<B1-ButtonRelease>", on_mouse_up)
 
# root.mainloop()

# import tkinter as tk

# root = tk.Tk()

# canvas = tk.Canvas(root, width=400, height=400)

# canvas.pack()

# rect = canvas.create_rectangle(100, 100, 200, 200, fill='red')

# def on_mouse_move(event):

#     canvas.coords(rect, event.x-50, event.y-50, event.x+50, event.y+50)

# canvas.bind('<B1-Motion>', on_mouse_move)

# root.mainloop()
# import tkinter as tk
# from functools import partial

# class DrawShapes(tk.Canvas):
#     def __init__(self, master=None, **kwargs):
#         super().__init__(master, **kwargs)
#         image = self.create_rectangle(0, 0, 800, 700, width=5, fill='red')
#         # self.tag_bind(image, '<Button-1>', self.on_click)
#         # self.tag_bind(image, '<Button1-Motion>', self.on_motion)
#         self.current = self.create_rectangle(10,10, 300, 100, width=5)
#         self.tag_bind(self.current, '<Button-1>', partial(self.on_click_rectangle, self.current))
#         self.tag_bind(self.current, '<Button1-Motion>', self.on_motion)

#     # def on_click(self, event):
#     #     """fires when user clicks on the background ... creates a new rectangle"""
#     #     self.start = event.x, event.y
        

#     def on_click_rectangle(self, tag, event):
#         """fires when the user clicks on a rectangle ... edits the clicked on rectange"""
#         self.current = tag
#         x1, y1, x2, y2 = self.coords(tag)
#         # if abs(event.x-x1) < abs(event.x-x2):
#         #     # opposing side was grabbed; swap the anchor and mobile side
#         #     x1, x2 = x2, x1
#         if abs(event.y-y1) < abs(event.y-y2):
#             y1, y2 = y2, y1
#         x1 = 10
#         x2 = 100
#         self.start = x1, y1

#     def on_motion(self, event):
#         """fires when the user drags the mouse ... resizes currently active rectangle"""
#         self.coords(self.current, *self.start, 300, event.y)

# def main():
#     c = DrawShapes()
#     c.pack()
#     c.mainloop()

# if __name__ == '__main__':
#     main()

# import tkinter as tk
  
# # Create Tkinter window
# frame = tk.Tk()
# frame.title('GFG Cursors')
# frame.geometry('200x200')
  
# # Specify dot cursor with blue color for frame
# frame.config(cursor="dot blue")
# canvas = tk.Canvas(frame, width=600, height=600)
# canvas.create_line(300, 40, 300, 140, arrow=tk.BOTH, width=5)
# canvas.pack()
  
# # Specify various cursor icons with colors
# # for label and buttons
# tk.Label(frame, text="Text cursor",
#          cursor="xterm #0000FF").pack()
  
# tk.Button(frame, text="Circle cursor",
#           cursor="circle #FF00FF").pack()
  
# tk.Button(frame, text="Plus cursor",
#           cursor="plus red").pack()
  
# # Specify cursor icon and color using
# # config() method
# a = tk.Button(frame, text='Exit')
# a.config(cursor="dot green red")
# a.pack()
  
# frame.mainloop()
# from paddleocr import PaddleOCR, draw_ocr

# # Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
# # 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
# ocr = PaddleOCR(use_angle_cls=True, lang="ch")  # need to run only once to download and load model into memory
# img_path = './imgs/11.jpg'
# result = ocr.ocr(img_path, cls=True)
# for idx in range(len(result)):
#     res = result[idx]
#     for line in res:
#         print(line)

# # 显示结果
# from PIL import Image
# result = result[0]
# image = Image.open(img_path).convert('RGB')
# boxes = [line[0] for line in result]
# txts = [line[1][0] for line in result]
# scores = [line[1][1] for line in result]
# im_show = draw_ocr(image, boxes, txts, scores, font_path='./fonts/simfang.ttf')
# im_show = Image.fromarray(im_show)
# im_show.save('result.jpg')
# import tkinter as tk

# def on_resize(event):
#     print('New size:', event.width, event.height)

# root = tk.Tk()

# pw = tk.PanedWindow(root, orient='horizontal')
# pw.pack(fill='both', expand=True)

# w1 = tk.Label(pw, text='Pane One', width=10, height=15, relief='groove')
# pw.add(w1, stretch='always')
# w2 = tk.Label(pw, text='Pane Two', width=10, height=15, relief='groove')
# pw.add(w2, stretch='always')

# pw.bind('<Configure>', on_resize)

# root.mainloop()
# import multiprocessing


# def addA(a, b):
#     print("aaaa")
#     return a + b


# if __name__ == '__main__':
#     pool = multiprocessing.Pool(2)  # 两个进程执行
#     multi_result = []
#     # 开始运行
#     for i in range(20):
#         multi_result.append(pool.apply_async(func=addA, args=(i, i + 1)))
#     pool.close()
#     pool.join()
    
#     # 打印结果
#     for _r in multi_result:
#         print(str(_r.get()))

#!/usr/bin/env python
# coding:UTF-8 
 
# import ntplib

# ntp_client = ntplib.NTPClient()
# response = ntp_client.request('pool.ntp.org')
# ntp_timestamp = response.tx_time
# print(ntp_timestamp)

# import uuid

# def get_mac_address():

#     node = uuid.getnode()

#     mac = uuid.UUID(int = node).hex[-12:]
#     return mac

# print(get_mac_address())

# import rsa
# import base64
# import uuid
#生成公钥、私钥
# publicKey, privateKey=rsa.newkeys(512)

# with open('public_key.pem', 'wb') as file:
#     file.write(publicKey.save_pkcs1())

# with open('private_key.pem', 'wb') as file:
#     file.write(privateKey.save_pkcs1())

# with open('public_key.pem', 'rb') as file:
#     publicKeyData = file.read()
#     publicKey = rsa.PublicKey.load_pkcs1(publicKeyData)

# with open('private_key.pem', 'rb') as file:
#     privateKeyData = file.read()
#     privateKey = rsa.PrivateKey.load_pkcs1(privateKeyData)


# message = str(uuid.uuid1()) + "d7"
# print(message)
# encrytedData = rsa.encrypt(bytes(message, encoding='utf-8'),pub_key=publicKey)

# aa = base64.b64encode(encrytedData)
# base64Decode = base64.b64decode(aa)
# print(base64Decode)
# decryptedData = rsa.decrypt(base64Decode, priv_key=privateKey)

# print(str(base64.b64encode(encrytedData), encoding='utf-8'), decryptedData)

# signature = rsa.sign(message, privateKey, "SHA-256")

# verificationResult = rsa.verify(message, signature, publicKey)
# print(verificationResult)
# print(signature)

import struct

i = 0x123456
binary_data = struct.pack('<I', i)  # 将整数转换为二进制数据，使用小端字节序


with open('output.bin', 'wb') as f:  # 以二进制模式打开文件进行写入
    f.write(binary_data)