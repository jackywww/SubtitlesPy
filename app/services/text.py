from multiprocessing import Process, Queue, Lock
import os
from app.models.ocr import Ocr
import app.models.rsa as arsa
import app.models.mac as amac
import app.models.api as aapi

import threading
import cv2
import mmcv
import global_vars
import math
import difflib

modelBaseDIR = global_vars.root_path + "/paddleocr/"
PEM_DIR = global_vars.root_path + "/"

line = 1

qValue = 0

allProcess = []

stopProcessBar = False



def progressBarCount(frameCounts, progressBarQueue, callBack):
     global qValue
     global stopProcessBar

     while qValue != frameCounts:

          try:
            qValue += progressBarQueue.get()
          except:
               continue

          callBack(float((qValue/frameCounts)*100))

     qValue = 0

def getFrameSubTitle(frame, ocr):
        # subFrame = frame[int(y1*scaleValue):int(y2*scaleValue),0:int(widthVideo)]
            
        
        
        result = ocr.ocr(frame, cls=True)
        resultString = ""

        if result[0] is not None :
            if result[0][0][-1][1] >= 0.8:
                resultString = result[0][0][-1][0]
                    
        return resultString  

def binarySearch(left, right, searchValue, clip, ocr):
     while left <= right :
        mid = math.floor((left + right) / 2)

        midResult = getFrameSubTitle(clip[mid], ocr)
        

        if midResult != searchValue :
             right = mid - 1
             continue

        if mid == right:
             return mid
        
        midNextResult = getFrameSubTitle(clip[mid+1], ocr)
        
        if midNextResult != searchValue :
             return mid
        else:
             left = mid + 1

        

def getSubText(videoPath, stepCounts, index, lock, y1, y2, scaleValue, useGpu, cpuNum, speed, widthVideo, progressBarQueue, subtitleResultQueue, processNum):
        try:
            ocr = Ocr(baseDir=modelBaseDIR,useGpu=useGpu,totalProcessNum=cpuNum)
            resultData = []
            
            lock.acquire()
            video = mmcv.VideoReader(videoPath)
            start = index*global_vars.stepFrameCount
            end = start + global_vars.stepFrameCount

            clip = []
            frameCounts = len(video)
            
            if index + 1 == stepCounts:
                if frameCounts % global_vars.stepFrameCount > 0:
                    end = start + frameCounts % global_vars.stepFrameCount

            startIndex = start

            while start < end:

                frame = video[start]
                subFrame = frame[int(y1*scaleValue):int(y2*scaleValue),0:int(widthVideo)]
                img = cv2.cvtColor(subFrame,cv2.COLOR_BGR2RGBA)
                h, w, _ = img.shape

                ocrImg = cv2.resize(img, (int(w/float(speed)),int(h/float(speed))),interpolation=cv2.INTER_NEAREST)
                
                clip.append(ocrImg)
                start += 1
            
            lock.release()
            left = 0
            right = len(clip) - 1
            
            while left <= right :
                
                frame = clip[left]
                result = getFrameSubTitle(frame, ocr)
                if len(result) == 0 :
                        left += 1

                if len(result) > 0:
                    searchValue = result

                    searchIndex = binarySearch(left, right, searchValue, clip, ocr)
                    resultItem = {}
                    resultItem['title'] = searchValue
                    resultItem['start'] = startIndex + left
                    resultItem['end'] = startIndex + searchIndex
                    resultData.append(resultItem)
                    left = searchIndex + 1

                
            progressBarQueue.put(right+1)

            shareData = {}
            shareData['index'] = index
            shareData['data'] = resultData

            subtitleResultQueue.put(shareData)
            processNum.get()

        except Exception as errorInfo:
            processNum.get()
            print(errorInfo)

def getText(videoPath, y1, y2, scaleValue, cpuNum, useGpu, speed, widthVideo, callBack, callBackShowSuccessInfo, progressBarQueue, name, toActivateCodeWindow):  

        global allProcess
        video = mmcv.VideoReader(videoPath)
        
        frameCounts = len(video)

        stepCounts = math.ceil(frameCounts / global_vars.stepFrameCount)
        
        lock = Lock()
        
        subtitleResultQueue = Queue(maxsize=1)
        processNum = Queue(int(cpuNum))
        fps = video.fps

        consumerThread = threading.Thread(target=consumer, args=(videoPath, name, fps, stepCounts, subtitleResultQueue, callBackShowSuccessInfo, toActivateCodeWindow, callBack))
        consumerThread.start()
        
        for index in range(stepCounts):
            processNum.put(1)
            t = Process(target=getSubText, args=(videoPath, stepCounts, index, lock, y1, y2, scaleValue, useGpu, cpuNum, speed, widthVideo, progressBarQueue, subtitleResultQueue, processNum))
            t.start()
                  
        
def checkMac(name):
    if len(name) == 0:
        return True
    
    apiModel = aapi.ApiModel()
    sign = apiModel.md5Sign({"name": name})

    try:
        resultData = apiModel.getStateAndMacAddress({"name": name, "sign": sign})

        if 'status' in resultData:
            if resultData['status'] == 1:
                data = resultData['data']
                macAddressModel = amac.MacAddressModel()
                macAddress = macAddressModel.getMacAddress()
                
                if data['mac_address'] != macAddress:
                    return False
    except Exception as errorInfo:
       return True

    return True   
    
def consumer(videoPath, name, fps, stepCounts, subtitleResultQueue, callBackShowSuccessInfo, toActivateCodeWindow, callBack):
    qData = []
    for i in range(stepCounts):
        qData.append({})

    i = 1
    while True:
        if i > stepCounts:
            break
        getV = subtitleResultQueue.get()
        qData[getV["index"]] = getV
        i += 1
        

    stepCounts = 0
    
    global line
    line = 1
    checkResult = checkMac(name)
    if checkResult == False:
        callBackShowSuccessInfo("一个激活码不能多台电脑同时用")
        toActivateCodeWindow()
        return
    
    allData = []
    
    for value in qData:

         allData = allData + value["data"]
    fileData = []

    qlen = len(allData)
    data = []
    for key in range (qlen):
        currentData = allData[key]
        
        if len(data) == 0:
            data = currentData
            if key + 1 == qlen:
                fileData.append(data)
                data = [] 

            continue
        seq = difflib.SequenceMatcher(None, data["title"], currentData["title"])
        print(seq.ratio(), data["title"], currentData["title"])
        # if data["title"] == currentData["title"]:
        if seq.ratio() >= 0.8 :
            if data["end"] < currentData["end"]:
                data["end"] = currentData["end"]
            else:
                if data["start"] > currentData["start"]:
                    data["start"] = currentData["start"]

            if len(data["title"]) < len(currentData["title"]):
                 data["title"] = currentData["title"]

            if key + 1 == qlen:
                fileData.append(data)

            continue
        
        else:
                fileData.append(data)
                data = currentData

                if key + 1 == qlen:
                    fileData.append(data)
            

            
        

        # toSrt(data=_data, fps=fps, path=videoPath)

    toSrt(data=fileData, fps=fps, path=videoPath)

    callBack()
    callBackShowSuccessInfo("提取完毕！srt 文件地址:" + videoPath + ".srt")

def timeFormate(s):
        timeMs = int(round(s*1000))
        ms = int(timeMs%1000)

        timeS = int(timeMs/1000)

        s = int(timeS%60)

        timeM = timeS/60

        m = int(timeM%60)

        h = int(timeM/60)

        return str(h) + ":" + str(m) + ":" + str(s) + "," + str(ms)

def toSrt(data, fps, path):
        if len(data) > 0 :
            for value in data:
                with open(path + ".srt", "a", encoding="utf-8") as file:
                    startTimeStr = timeFormate((value['start'] + 0)/fps)
                    endTimeStr = timeFormate((value['end'] + 1)/fps)
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
     

