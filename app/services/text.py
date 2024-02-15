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

def getFrameSubTitle(frame, y1, y2, scaleValue, speed, widthVideo, ocr):
        subFrame = frame[int(y1*scaleValue):int(y2*scaleValue),0:int(widthVideo)]
            
        img = cv2.cvtColor(subFrame,cv2.COLOR_BGR2RGBA)
        h, w, _ = img.shape

        a = cv2.resize(img, (int(w/float(speed)),int(h/float(speed))),interpolation=cv2.INTER_NEAREST)
        
        result = ocr.ocr(a, cls=True)
        resultString = ""

        if result[0] is not None :
            if result[0][0][-1][1] >= 0.8:
                resultString = result[0][0][-1][0]
                    
        return resultString  

def binarySearch(left, right, searchValue, clip, noneSubTitleData, subTitltData, y1, y2, scaleValue, speed, widthVideo, ocr):
     while left <= right :
        mid = math.floor((left + right) / 2)
        midResult = getFrameSubTitle(clip[mid],y1, y2, scaleValue, speed, widthVideo, ocr)
        if len(midResult) > 0:
            subTitltData[mid] = midResult
        else:
            noneSubTitleData[mid] = 1

        if midResult != searchValue :
             right = mid - 1
             continue

        if mid == right:
             return mid, subTitltData, noneSubTitleData
        
        midNextResult = getFrameSubTitle(clip[mid+1],y1, y2, scaleValue, speed, widthVideo, ocr)
        if len(midNextResult) > 0:
            subTitltData[mid+1] = midNextResult
        else:
            noneSubTitleData[mid+1] = 1

        if midNextResult != searchValue :
             return mid, subTitltData, noneSubTitleData
        else:
             left = mid + 1

        

def getSubText(videoPath, stepCounts, index, lock, y1, y2, scaleValue, useGpu, cpuNum, speed, widthVideo, progressBarQueue, subtitleResultQueue, processNum):
        
        ocr = Ocr(baseDir=modelBaseDIR,useGpu=useGpu,totalProcessNum=cpuNum)
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
        left = 0
        right = len(clip) - 1
        noneSubTitleData = {}
        subTitltData = {}
        while left <= right :
            
            frame = clip[left]
            result = getFrameSubTitle(frame,y1, y2, scaleValue, speed, widthVideo, ocr)
            if len(result) == 0 :
                    noneSubTitleData[left] = 1
                    left += 1

            if len(result) > 0:
                subTitltData[left] = result
                searchValue = result

                searchIndex, subTitltData, noneSubTitleData = binarySearch(left, right, searchValue, clip, noneSubTitleData, subTitltData, y1, y2, scaleValue, speed, widthVideo, ocr)
                resultItem = {}
                resultItem['title'] = searchValue
                resultItem['start'] = left
                resultItem['end'] = searchIndex
                resultData.append(resultItem)
                left = searchIndex + 1

        # for frame in clip:
            #  resultData = getFrameSubTitle(frame,y1, y2, scaleValue, speed, indexFrame, widthVideo, ocr, resultData)
        # for frame in clip:
        #     subFrame = frame[int(y1*scaleValue):int(y2*scaleValue),0:int(widthVideo)]
            
        #     img = cv2.cvtColor(subFrame,cv2.COLOR_BGR2RGBA)
        #     h, w, _ = img.shape

        #     a = cv2.resize(img, (int(w/float(speed)),int(h/float(speed))),interpolation=cv2.INTER_NEAREST)
            
        #     result = ocr.ocr(a, cls=True)

        #     if result[0] is not None :
        #         if result[0][0][-1][1] >= 0.8:
                    
        #             if len(resultData) == 0 :
        #                 resultItem = {}
        #                 resultItem['title'] = result[0][0][-1][0]
        #                 resultItem['start'] = indexFrame
        #                 resultItem['end'] = indexFrame
        #                 resultData.append(resultItem)
        #             else:
        #                 if resultData[-1]['title'] != result[0][0][-1][0]:
        #                     resultItem = {}
        #                     resultItem['title'] = result[0][0][-1][0]
        #                     resultItem['start'] = indexFrame
        #                     resultItem['end'] = indexFrame
        #                     resultData.append(resultItem)

        #                 if resultData[-1]['title'] == result[0][0][-1][0]:
        #                     resultData[-1]['end'] = indexFrame
     
        #     indexFrame += 1

        #     
            
        progressBarQueue.put(right+1)

        shareData = {}
        shareData['index'] = index
        shareData['count'] = right+1
        shareData['data'] = resultData

        subtitleResultQueue.put(shareData)
        processNum.get()

def getText(videoPath, y1, y2, scaleValue, cpuNum, useGpu, speed, widthVideo, callBack, callBackShowSuccessInfo, progressBarQueue, name, toActivateCodeWindow):  

        threads = []
        global allProcess
        video = mmcv.VideoReader(videoPath)
        
        frameCounts = len(video)
        


        stepCounts = math.ceil(frameCounts / global_vars.stepFrameCount)
        if int(cpuNum) >= int(stepCounts):
             global_vars.stepFrameCount = math.floor(frameCounts / int(cpuNum))
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
           
            # if (index+1)%int(cpuNum) == 0 or (index+1 == stepCounts):
            #     for thread in threads:
            #         thread.start()
            #     for thread in threads:
            #         getV = subtitleResultQueue.get()
            #         qData[getV["index"]] = getV

            #     threads.clear()
                
        
        
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
    for clipValue in qData:
        _data = clipValue['data']

        toSrt(step=stepCounts, data=_data, fps=fps, path=videoPath)
        stepCounts += int(clipValue['count'])

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

def toSrt(step, data, fps, path):
        if len(data) > 0 :
            for value in data:
                with open(path + ".srt", "a", encoding="utf-8") as file:
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
     

