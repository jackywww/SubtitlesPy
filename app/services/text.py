from multiprocessing import Process, Queue, Lock
import os
from app.models.ocr import Ocr
import app.models.rsa as arsa
import app.models.mac as amac
import app.models.api as aapi

import cv2
import psutil
import mmcv
import global_vars
import math

modelBaseDIR = global_vars.root_path + "/paddleocr/"
PEM_DIR = global_vars.root_path + "/"

line = 1
progressBarQueue = Queue(maxsize=int(psutil.cpu_count()))
qValue = 0

allProcess = []

stopProcessBar = False

subtitleResultQueue = Queue(maxsize=1)

def progressBarCount(frameCounts, callBack):
     global qValue
     global stopProcessBar
     
     while qValue != frameCounts:
          if stopProcessBar :
               break
          try:
            qValue += progressBarQueue.get(timeout=10)
          except:
               callBack(1)
               continue
          
          callBack(int((qValue/frameCounts)*100))

     qValue = 0
          

def getSubText(videoPath, stepCounts, index, lock, y1, y2, scaleValue, useGpu, cpuNum, speed, widthVideo):
        
        ocr = Ocr(baseDir=modelBaseDIR,useGpu=useGpu,totalProcessNum=cpuNum)
        indexFrame = 0
        resultData = []
        
        lock.acquire()
        video = mmcv.VideoReader(videoPath)
        start = index*global_vars.stepFrameCount
        end = start + global_vars.stepFrameCount

        if index + 1 != stepCounts:
            clip = video[start:end]
        else:
             clip = video[start:]
        lock.release()
        for frame in clip:
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
            progressBarQueue.put(1)
            
        shareData = {}
        shareData['index'] = index
        shareData['count'] = indexFrame
        shareData['data'] = resultData

        subtitleResultQueue.put(shareData)

def getText(videoPath, y1, y2, scaleValue, cpuNum, useGpu, speed, widthVideo, callBack, callBackShowSuccessInfo):  
        threads = []
        global allProcess
        video = mmcv.VideoReader(videoPath)
        
        frameCounts = len(video)
        


        stepCounts = math.ceil(frameCounts / global_vars.stepFrameCount)
        if int(cpuNum) > int(stepCounts):
             global_vars.stepFrameCount = math.floor(frameCounts / int(cpuNum))
             stepCounts = math.ceil(frameCounts / global_vars.stepFrameCount)
        
        qData = []
        for i in range(stepCounts):
            qData.append({})


        lock = Lock()
        

        for index in range(stepCounts):
            _data = []
            t = Process(target=getSubText, args=(videoPath, stepCounts, index, lock, y1, y2, scaleValue, useGpu, cpuNum, speed, widthVideo))
            threads.append(t)
            allProcess.append(t)
            if (index+1)%int(cpuNum) == 0 or (index+1 == stepCounts - 1):
                for thread in threads:
                    thread.start()
                for thread in threads:
                    getV = subtitleResultQueue.get()
                    qData[getV["index"]] = getV

                threads.clear()
            
        stepCounts = 0
        fps = video.fps
        global line
        line = 1
        for clipValue in qData:
            _data = clipValue['data']
            toSrt(step=stepCounts, data=_data, fps=fps, path=videoPath)
            stepCounts += int(clipValue['count'])

        callBack()
        callBackShowSuccessInfo(videoPath + ".srt")
        
        

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
    try:
        stopProcess()
    except:
         pass
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
    data["sign"] = sign
    return data, result

def signData(data):
    apiModel = aapi.ApiModel()
    sign = apiModel.md5Sign(data)
    data['sign'] = sign
    return data
     

