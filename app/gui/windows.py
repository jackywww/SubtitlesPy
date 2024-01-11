from tkinter import *
from tkinter import ttk
from tkinter import font
from multiprocessing import Queue
import tkinter
from tkinter.filedialog import *
from PIL import ImageTk, Image
import cv2
from functools import partial
from app.models.ocr import Ocr
import psutil
import threading
import app.services.text as ast
import app.models.key as akey
import app.models.api as aapi
import app.models.mac as amac

import global_vars

BASE_DIR = global_vars.root_path + "/images/"
PEM_DIR = global_vars.root_path + "/" 

modelBaseDIR = global_vars.root_path + "/paddleocr/"
class Windows():
    def __init__(self, activateState, message, name):
        self.root = Tk(className="概")
        self.activateState = activateState
        self.scalValue = 1
        # self.width = self.root.winfo_screenwidth()
        # self.height = self.root.winfo_screenheight()
        self.width = 1200
        self.height = 1000
        self.startX = 3
        self.startY = 10
        self.endY = 100
        self.line = -1
        self.innerImage = -1
        self.font = font.Font(family='Helvetica', size=7)

        self.start = self.startX, self.startY

        self.left = PanedWindow(orient='vertical', width=int(self.width / 4))
        self.right = PanedWindow(orient='vertical', width=int(self.width / 4))
        

        self.right.grid(row = 0, column = 1)

        self.cpuCounts = psutil.cpu_count()

        self.cpuNum = int(self.cpuCounts/2)
        self.speed = 2
        self.threads = []
        self.useGpu = False
        self.currentFrameIndex = 1
        self.message = message
        self.userName = name
         
        
        
    def position(self):
        self.root.geometry("%dx%d+%d+%d" % (int(self.width / 2), int(self.height / 2), int(self.width / 4), int(self.height / 4)))
    
    def openVideo(self,path):
        self.video = cv2.VideoCapture(path)
        self.getVideoSize()

        if self.widthVideo / (self.width/2) > self.heightVideo / (self.height/2) :
            self.scalValue = self.widthVideo / (self.width/2)
        else:
            self.scalValue = self.heightVideo / ((self.height-50)/2)

        if hasattr(self, 'canvas') :
            self.canvas.destroy()
        self.canvas = Canvas(self.right, width=int(self.widthVideo/self.scalValue),height=int(self.heightVideo/self.scalValue), bg="white")
        self.right.add(self.canvas, stretch='always')

        return int(self.widthVideo/self.scalValue), int(self.heightVideo/self.scalValue)

    def getVideoSize(self):
        self.widthVideo  = self.video.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.heightVideo = self.video.get(cv2.CAP_PROP_FRAME_HEIGHT)
        

    
    def getFrameCounts(self):
        try: 
            return int(self.video.get(cv2.CAP_PROP_FRAME_COUNT))
        except:
            return 0

    def updateImageToCanvas(self, index):
        
        self.endX = int(self.widthVideo/self.scalValue)-3
        self.innerImageHeight = int(abs(self.endY - self.startY)) - 10
        self.innerImageWidth = int(abs(self.endX - self.startX)) - 10

        self.video.set(cv2.CAP_PROP_POS_FRAMES, index)  
        retval, frame = self.video.read()

        if retval :
            
            img = cv2.cvtColor(frame,cv2.COLOR_BGR2RGBA)
            currentImage = Image.fromarray(img).resize((int(self.widthVideo/self.scalValue),int(self.heightVideo/self.scalValue)))
            
            self.textPostionImage = img
            
            self.imgtk = ImageTk.PhotoImage(image = currentImage)
            
            self.canvas.create_image(0,0, anchor = NW, image = self.imgtk)
            self.current = self.canvas.create_rectangle(self.startX, self.startY, self.endX, self.endY, width = 5, outline="red", activeoutline="orange")


            if self.innerImageHeight >= 0 and self.innerImageWidth >= 0:
                image = Image.new('RGBA', (self.innerImageWidth, self.innerImageHeight), (255,0,0,0))
                self.moveImage = ImageTk.PhotoImage(image)

                self.innerImage = self.canvas.create_image(self.startX + 5, self.startY + 5,anchor = NW, image = self.moveImage)
                self.canvas.tag_bind(self.innerImage, '<Button1-Motion>', self.onMotionInner)
            

            self.canvas.tag_bind(self.current, '<Button-1>', partial(self.onClickRectangle))
            self.canvas.tag_bind(self.current, '<Button1-Motion>', self.onMotion)
            
            # self.canvas.tag_bind(self.innerImage, "<Enter>", self.onMouseEnter)
            # self.canvas.tag_bind(self.innerImage, "<Leave>", self.onMouseLeave)


    def onClickRectangle(self, event):
        """fires when the user clicks on a rectangle ... edits the clicked on rectange"""
        
        self.startX, self.startY, self.endX, self.endY = self.canvas.coords(self.current)
 
        # if abs(event.x-x1) < abs(event.x-x2):
        #     # opposing side was grabbed; swap the anchor and mobile side
        #     x1, x2 = x2, x1
        if abs(event.y-self.startY) < abs(event.y-self.endY):
            self.startY, self.endY = self.endY, self.startY
        
        self.start = self.startX, self.startY


    def onMotion(self, event):
        if self.line > 0 :
            self.canvas.delete(self.line)
        """fires when the user drags the mouse ... resizes currently active rectangle"""
        x1,y1,x2,y2 = self.canvas.coords(self.current)
    
        self.endY = y2
        self.startX = x1
        self.startY = y1
        self.endX = x2

        self.canvas.coords(self.current, *self.start, int(self.widthVideo/self.scalValue)-3, event.y)

        self.innerImageHeight = int(abs(y2 - y1)) - 10
        self.innerImageWidth = int(abs(x2 - x1)) - 10

        self.canvas.delete(self.innerImage)

        if self.innerImageHeight > 0 :
            image = Image.new('RGBA', (self.innerImageWidth, self.innerImageHeight), (255,0,0,0))
            self.moveImage = ImageTk.PhotoImage(image)
            self.innerImage = self.canvas.create_image(x1 + 5, y1 + 5, anchor = NW, image = self.moveImage)
            self.canvas.tag_bind(self.innerImage, '<Button1-Motion>', self.onMotionInner)
            # self.canvas.tag_bind(self.innerImage, "<Enter>", self.onMouseEnter)
            # self.canvas.tag_bind(self.innerImage, "<Leave>", self.onMouseLeave)

    def onMotionInner(self, event):
        self.startX, self.startY, self.endX, self.endY = self.canvas.coords(self.current)
        diffVal = abs(self.startY - self.endY) / 2

        x = int((self.startX + self.endX)/2)

        yDiffVal = int(abs(self.endY - self.startY) / 4)


        # self.innerImage = self.canvas.create_image(self.startInnerX, event.y - diffValInner,anchor = NW, image = self.moveImage)
        self.canvas.coords(self.innerImage, self.startX + 5, event.y - diffVal + 5)

        self.canvas.coords(self.line, x, event.y - yDiffVal, x, event.y+yDiffVal)

        self.canvas.coords(self.current, self.startX, event.y - diffVal, self.endX, event.y+diffVal)


    def changeFrame(self,value):
        self.currentFrameIndex = int(value)
        self.updateImageToCanvas(int(value))

    
    def getPositionAndScaleValue(self):
        return self.canvas.coords(self.current), self.scalValue
    
    def openFile(self):
        val = askopenfilename(title="选择视频文件", filetypes=[('mp4视频文件', '*.mp4')])

        if len(val) > 0:
            self.videoPath = val

            self.right.destroy()
            self.right = PanedWindow(orient='vertical')
            self.right.grid(row=0, column=1)
            videoWidth, videoHeight = self.openVideo(val)
            counts = self.getFrameCounts() - 1
            _width = int(self.width / 2) + int(videoWidth) - int(self.width / 4) + 10

            if videoHeight+40 < 290:
                videoHeight = 290
            self.root.geometry("%dx%d" % (_width, videoHeight+40))
            scale = tkinter.Scale(
                self.right,
                from_=1,
                to= counts,
                orient=tkinter.HORIZONTAL, 
                resolution=1, 
                length=videoWidth,
                showvalue=False,
                command=self.changeFrame,
            )

            self.right.add(scale) 
            self.changeFrame(1)

           



    def stopThreads(self):
        
        for thread in self.threads:
            thread.join()

        self.threads.clear()
                    

    def subWind(self):
        childWin = tkinter.Toplevel(self.root)
        childWin.geometry("%dx%d+%d+%d" % (int(self.width / 2), 40, int(self.width / 4), int(self.height / 4)))

        prbar = tkinter.ttk.Progressbar(
            childWin,
            mode="determinate",
        )
        prbar.pack()
        stopP = PhotoImage(file=BASE_DIR + "stop.png")
        button = tkinter.Button(childWin, image=stopP, command=self.stopProcess)
        button.pack()
        childWin.grab_set()
        childWin.mainloop()

    def disableButton(self):
        self.buttonStart.config(state=tkinter.DISABLED)
        self.button.config(state=tkinter.DISABLED)
        self.buttonTextPosition.config(state=tkinter.DISABLED)
        self.cpuScale.config(state=tkinter.DISABLED)
        self.recScale.config(state=tkinter.DISABLED)
        # self.buttonStop.config(state=tkinter.NORMAL)

    def normalButton(self):
        self.buttonStart.config(state=tkinter.NORMAL)
        self.button.config(state=tkinter.NORMAL)
        self.buttonTextPosition.config(state=tkinter.NORMAL)
        self.cpuScale.config(state=tkinter.NORMAL)
        self.recScale.config(state=tkinter.NORMAL)
        # self.buttonStop.config(state=tkinter.DISABLED)

    def startRun(self):
        if len(self.userName) == 0:
            macAddressModel = amac.MacAddressModel()
            macAddress = macAddressModel.getMacAddress()
            data = ast.signData({"mac_address":macAddress})

            apiModel = aapi.ApiModel()

            apiResult = apiModel.tryAgain(data)
            if apiResult['status'] == 0:
                tkinter.messagebox.showinfo("提示", "服务异常，请联系商家")
                return
            
            if apiResult['status'] == 1:
                resultData = apiResult['data']
                if resultData == False:
                    tkinter.messagebox.showinfo("提示", "试用次数已经用完，请激活")
                    self.left.grid_remove()
                    self.activateFalse()
                    return
            
        frameCounts = self.getFrameCounts()
        if frameCounts > 0 :
            self.disableButton()
            videoPath = self.videoPath
            position, scaleValue = self.getPositionAndScaleValue()
            x1,y1,x2,y2 = position
            cpuNum = self.cpuNum
            useGpu = self.useGpu
            speed = self.speed
            widthVideo = self.widthVideo

            progressBarQueue = Queue(maxsize=int(psutil.cpu_count()))
            tCount = threading.Thread(target=ast.progressBarCount, args=(frameCounts, progressBarQueue, self.setProgressBar))
            tCount.start()
            self.threads.append(tCount)

            t = threading.Thread(target=ast.getText, args=(videoPath, y1, y2, scaleValue, cpuNum, useGpu, speed, widthVideo, self.normalButton, self.showSuccessInfo, progressBarQueue, self.userName))
            t.start()
            self.threads.append(t)
        
    def changeCpuNum(self, value): 
        self.cpuNum = value   

    def changeSpeed(self, value): 
        self.speed = value  

    def setProgressBar(self, value):

        self.progressBar["value"] = value
        
        self.style.configure('text.Horizontal.TProgressbar', text='{:g} %'.format(value))

    

    def textPosition(self):
        ocr = Ocr(baseDir=modelBaseDIR,useGpu=self.useGpu,totalProcessNum=1)

        imgResult = cv2.resize(self.textPostionImage, (int(self.widthVideo/self.scalValue),int(self.heightVideo/self.scalValue)),interpolation=cv2.INTER_NEAREST)
        result = ocr.ocr(imgResult, cls=True)
       
        if result[0] is not None :
            if result[0][-1][-1][1] > 0.8:
                self.startY = result[0][-1][0][0][-1] - 10
                self.endY = result[0][-1][0][-1][-1] + 10
                self.updateImageToCanvas(self.currentFrameIndex)

    def onClosing(self):
        if tkinter.messagebox.askokcancel("Quit", "是否确定退出?"):
            ast.terminateProcess()
            self.root.destroy()
            
    def stopRun(self):
        ast.terminateProcess()
        self.normalButton()


    def getActivateCode(self):
        try:
            resultSave = False
            textData = self.text.get("1.0", tkinter.END)
            data, result = ast.decryptedDataAndSign(textData)

            apiModel = aapi.ApiModel()

            apiResult = apiModel.activate(data)

            if apiResult['status'] == 1:
                resultData = apiResult['data']

                if resultData['state'] == 0:
                    raise Exception("data error")

                if resultData['state'] == 1 and len(result) > 0:
                    keymodel = akey.Key()
                    resultSave = keymodel.writeKey(PEM_DIR + 'key', textData)
                    if resultSave == True:
                        self.activate.grid_remove()
                        self.left.grid_remove()
                        self.activateTrue()
                        tkinter.messagebox.showinfo("提示", "激活成功，系统自动关闭！请再一次双击程序！")
                        ast.terminateProcess()
                        self.root.destroy()
                        return

        except Exception as e:
            pass
        tkinter.messagebox.showinfo("提示", "激活码异常，请联系商家")

    def showSuccessInfo(self, path):
        tkinter.messagebox.showinfo("提示",  path)
    
    def activateTrue(self):
        self.left = PanedWindow(orient='vertical', width=int(self.width / 4))
        self.pic = PhotoImage(file=BASE_DIR + "open.png")
        self.button = tkinter.Button(image=self.pic, command=self.openFile)

        self.picTextPosition = PhotoImage(file=BASE_DIR + "textposition.png")
        self.buttonTextPosition = tkinter.Button(image=self.picTextPosition, command=self.textPosition)

        self.startPic = PhotoImage(file=BASE_DIR + "start.png")
        self.buttonStart = tkinter.Button(image=self.startPic, command=self.startRun)

        

        self.left.add(self.button)
        self.left.add(self.buttonTextPosition) 

        

        cpuNum = PanedWindow()

        self.pNumP = PhotoImage(file=BASE_DIR + "pnum.png")
        
        cpuNum.add(Label(image=self.pNumP, font=self.font))

        self.cpuScale = tkinter.Scale(
                from_ = 1,
                to = self.cpuCounts,
                orient=tkinter.HORIZONTAL, 
                resolution= 1,
                tickinterval= 5,
                length=20,
                showvalue=True,
                command=self.changeCpuNum,
                font=self.font
        )
        
        self.cpuScale.set(self.cpuNum)
        cpuNum.add(self.cpuScale)

        self.left.add(cpuNum)

       

        recSpeed = PanedWindow()

        self.recSpeedP = PhotoImage(file=BASE_DIR + "recspeed.png")
        recSpeed.add(Label(image=self.recSpeedP))

        self.recScale = tkinter.Scale(
                from_ = 1,
                to = 3,
                orient=tkinter.HORIZONTAL, 
                resolution= 0.1,
                tickinterval= 0.3,
                length=20,
                showvalue=True,
                command=self.changeSpeed,
                font=self.font
            )
        
        self.recScale.set(self.speed)
        recSpeed.add(self.recScale)

        self.left.add(recSpeed)
        
        self.left.add(self.buttonStart)
        

        stopPic = PhotoImage(file=BASE_DIR + "stop.png")
        self.buttonStop = tkinter.Button(image=stopPic, command=self.stopRun)
        # self.left.add(self.buttonStop)
        self.buttonStop.config(state=tkinter.DISABLED)

        self.style = ttk.Style(self.root)
        self.style.layout('text.Horizontal.TProgressbar',
                    [('Horizontal.Progressbar.trough',
                    {'children': [('Horizontal.Progressbar.pbar',
                                    {'side': 'left', 'sticky': 'ns'})],
                        'sticky': 'nswe'}),
                    ('Horizontal.Progressbar.label', {'sticky': ''})])
        self.style.configure('text.Horizontal.TProgressbar', text='0 %')

        self.progressBar = ttk.Progressbar(
            length=100,
            value=0,
            style='text.Horizontal.TProgressbar',
        )

        self.left.add(self.progressBar)
        self.left.grid(row = 0, column = 0)

    def activateFalse(self):
        self.activate = PanedWindow(orient='vertical', width=int(self.width / 4))
        self.menu = Menu(self.root,tearoff=0)
        self.left.grid_remove()
        

        self.picPaste = PhotoImage(file=BASE_DIR + "paste.png")
        self.menu.add_command(image=self.picPaste,command=self.paste)
        self.picCancel = PhotoImage(file=BASE_DIR + "cancel.png")
        self.menu.add_command(image=self.picCancel,command=self.cancel)

        self.codePic = PhotoImage(file=BASE_DIR + "inputcode.png")
        codelabel = tkinter.Label(image=self.codePic)
        self.activate.add(codelabel)

        self.activateButtonPic = PhotoImage(file=BASE_DIR + "activate_button.png")
        activateButton = tkinter.Button(image=self.activateButtonPic, command=self.getActivateCode)

        self.tryButtonPic = PhotoImage(file=BASE_DIR + "try_button.png")
        tryButton = tkinter.Button(image=self.tryButtonPic, command=self.tryAgain)

        self.text = tkinter.Text(height=5, width=10)
        self.text.bind('<Button-3>',self.popup) 
        self.activate.add(self.text)
        self.activate.add(activateButton)
        self.activate.add(tryButton)

        self.activate.grid(row = 0, column = 0)

        
    def tryAgain(self):
        # macAddressModel = amac.MacAddressModel()
        # macAddress = macAddressModel.getMacAddress()
        # data = ast.signData({"mac_address":macAddress})

        # apiModel = aapi.ApiModel()

        # apiResult = apiModel.tryAgain(data)
        # if apiResult['status'] == 0:
        #     tkinter.messagebox.showinfo("提示", "服务异常，请联系商家")
        #     return
        
        # if apiResult['status'] == 1:
        #     resultData = apiResult['data']
        #     if resultData == False:
        #         tkinter.messagebox.showinfo("提示", "试用次数已经用完，请联系商家")
        #         return
            
        self.activate.grid_remove()
        self.activateTrue()
        

    def startTK(self):
        
        self.position()

        videoArea = PhotoImage(file=BASE_DIR + "videoarea.png")

        label = tkinter.Label(image=videoArea, height=499, background="white")
        self.right.add(label)

        if self.activateState == True:
            self.activateTrue()
        
        if self.activateState == False:
            self.activateFalse()

        # self.canvas.create_rectangle(10,10, 300, 100, width=5)
        # self.canvas.grid(row =1 , column = 2)
        self.root.protocol("WM_DELETE_WINDOW", self.onClosing)
        if self.message != "":
            tkinter.messagebox.showinfo("提示", self.message)
        self.root.mainloop()

    
    def run(self):
        self.startTK()

    def popup(self,event):
        try:
            self.menu.tk_popup(event.x_root,event.y_root) # Pop the menu up in the given coordinates
        finally:
            self.menu.grab_release() # Release it once an option is selected

    def cancel(self):
        self.menu.grab_release()

    def paste(self):
        try:
            clipboard = self.root.clipboard_get() # Get the copied item from system clipboard
            self.text.insert('end',clipboard) # Insert the item into the entry widget
        except:
            pass

    def copy(self):
        inp = self.text.get() # Get the text inside entry widget
        self.root.clipboard_clear() # Clear the tkinter clipboard
        self.root.clipboard_append(inp) # Append to system clipboard
        