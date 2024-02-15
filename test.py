from app.models.ocr import Ocr
import global_vars
import cv2

modelBaseDIR = global_vars.root_path + "/paddleocr/"
ocr = Ocr(baseDir=modelBaseDIR,useGpu=False,totalProcessNum=1)
image = cv2.imread("/home/jacky/Pictures/Screenshots/123.png")
result = ocr.ocr(image, cls=False)
print(result)