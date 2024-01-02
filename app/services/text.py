from multiprocessing import Process, Queue
from moviepy.editor import VideoFileClip
import os
from app.models.ocr import Ocr
import app.models.rsa as arsa
import app.models.mac as amac
import app.models.api as aapi

import cv2
import psutil

modelBaseDIR = os.path.expanduser("~/Dev/Project/SubtitlePy/paddleocr/")
PEM_DIR = os.path.expanduser("~/Dev/Project/SubtitlePy/") 

line = 1
qCount = Queue(maxsize=int(psutil.cpu_count()))
qValue = 0

allProcess = []

stopProcessBar = False

q = Queue(maxsize=1)

def progressBarCount(frameCounts, callBack):
     global qValue
     global stopProcessBar
     
     while qValue != frameCounts:
          if stopProcessBar :
               break
          try:
            qValue += qCount.get(timeout=10)
          except:
               callBack(1)
               continue
          
          callBack(int((qValue/frameCounts)*100))

     qValue = 0
          

def getSubText(clip, y1, y2, scaleValue, index, q, useGpu, cpuNum, speed, widthVideo):
        
        ocr = Ocr(baseDir=modelBaseDIR,useGpu=useGpu,totalProcessNum=cpuNum)
        indexFrame = 0
        resultData = []
       
        for frame in clip.iter_frames():
            subFrame = frame[int(y1*scaleValue):int(y2*scaleValue),0:int(widthVideo)]
            
            img = cv2.cvtColor(subFrame,cv2.COLOR_BGR2RGBA)
            h, w, _ = img.shape

            a = cv2.resize(img, (int(w/float(speed)),int(h/float(speed))),interpolation=cv2.INTER_NEAREST)
            
            result = ocr.ocr(a, cls=True)

            if result[0] is not None :
                if result[0][0][-1][1] >= 0.8:
                    
                    if len(resultData) == 0 :
                        resultItem = {}
                        resultItem['title'] = result[0][0][-1][0]
                        resultItem['start'] = indexFrame
                        resultItem['end'] = indexFrame
                        resultData.append(resultItem)
                    else:
                        if resultData[-1]['title'] != result[0][0][-1][0]:
                            resultItem = {}
                            resultItem['title'] = result[0][0][-1][0]
                            resultItem['start'] = indexFrame
                            resultItem['end'] = indexFrame
                            resultData.append(resultItem)

                        if resultData[-1]['title'] == result[0][0][-1][0]:
                            resultData[-1]['end'] = indexFrame
     
            indexFrame += 1
            qCount.put(1)
            
        shareData = {}
        shareData['index'] = index
        shareData['count'] = indexFrame
        shareData['data'] = resultData

        q.put(shareData)

def getText(videoPath, y1, y2, scaleValue, cpuNum, useGpu, speed, widthVideo, callBack):  
        threads = []
        global allProcess
        video = VideoFileClip(videoPath)
        time = video.duration - 1
        
        # duration = math.floor(time/int(self.cpuNum))
        duration = 10

        # clips = [video.subclip(i, i+duration) for i in range(0, int(video.duration), duration)]
        clips = []
        clipIndex = 1
        for i in range(0, int(video.duration), duration):
            if video.duration - i >= duration:
                clips.append(video.subclip(i, i+duration))
            else:
                clips.append(video.subclip(i))
            clipIndex += 1
 
        length = len(clips)
        qData = []
        for i in range(length):
            qData.append({})

        # q = Queue(maxsize=10)
        global q

        clipLast = clips.pop()
        last = Process(target=getSubText, args=(clipLast, y1, y2, scaleValue, len(clips), q, useGpu, cpuNum, speed, widthVideo))
        allProcess.append(last)
        last.start()
        last.join()


        getV = q.get(timeout=1)
        qData[getV["index"]] = getV

        for i in range(length-1):
            _data = []
            val = clips[i]
            t = Process(target=getSubText, args=(val, y1, y2, scaleValue, i, q,  useGpu, cpuNum, speed, widthVideo))
            threads.append(t)
            allProcess.append(t)
            if (i+1)%int(cpuNum) == 0 or (i+1 == length - 1):
                for thread in threads:
                    thread.start()
                for thread in threads:
                    getV = q.get()
                    qData[getV["index"]] = getV

                threads.clear()
            
        stepCounts = 0
        fps = video.reader.fps
        global line
        line = 1
        for clipValue in qData:
            _data = clipValue['data']
            toSrt(step=stepCounts, data=_data, fps=fps, path=videoPath)
            stepCounts += int(clipValue['count'])

        callBack()
        
        

def timeFormate(s):
        timeMs = int(round(s*1000))
        ms = int(timeMs%1000)

        timeS = int(timeMs/1000)

        s = int(timeS%60)

        timeM = timeS/60

        m = int(timeM%60)

        h = int(timeM/60)

        return str(h) + ":" + str(m) + ":" + str(s) + "," + str(ms)

def toSrt(step, data, fps, path):
        if len(data) > 0 :
            for value in data:
                with open(path + ".srt", "a") as file:
                    startTimeStr = timeFormate((value['start'] + step)/fps)
                    endTimeStr = timeFormate((value['end'] + 1 + step)/fps)
                    global line
                    lines = [ str(line) + "\n", startTimeStr + " --> " + endTimeStr + "\n", value['title'] + "\n\n"]
                    file.writelines(lines)
                    line += 1
def stopProcess():
    global allProcess
    global stopProcessBar

    stopProcessBar = True
    for process in allProcess:
        process.terminate()
    #   if process.is_alive():
    #        process.terminate()

    allProcess.clear()

   

def terminateProcess():
    stopProcess()
    os._exit(0)

def decryptedDataAndSign(textData):
    rsamodel = arsa.RsaModel()
    result = rsamodel.decryptedData(textData, rsamodel.privateKey(PEM_DIR + 'private_key.pem'))

    macAddressModel = amac.MacAddressModel()
    macAddress = macAddressModel.getMacAddress()
    nameDays = result.split("=")
    name = nameDays[0]
    days = nameDays[1]

    data = {
        "name": name,
        "days": int(days),
        "mac_address": macAddress
    }
    apiModel = aapi.ApiModel()
    sign = apiModel.md5Sign(data)
    data['sign'] = sign
    return data, result
     

