from paddleocr import PaddleOCR
import os


BASE_DIR = os.path.expanduser("~/Dev/Project/SubtitlePy/paddleocr/")

class Ocr(PaddleOCR):
    def __init__(self, baseDir, useGpu, totalProcessNum ):
        super().__init__(
            det_model_dir = baseDir + "whl/det/ch/ch_PP-OCRv4_det_infer",
            rec_model_dir = baseDir + "whl/rec/ch/ch_PP-OCRv4_rec_infer",
            cls_model_dir = baseDir + "whl/cls/ch_ppocr_mobile_v2.0_cls_infer",
            use_angle_cls=True, 
            lang="ch",
            show_log=False,
            use_gpu=useGpu,
            use_mp=True,
            total_process_num = totalProcessNum
        )


def main():
    BASE_DIR = os.path.expanduser("~/Dev/Project/SubtitlePy/paddleocr/")
    ocr = Ocr(baseDir=BASE_DIR)
    img_path = '/home/jacky/Pictures/Screenshots/123.png'
    result = ocr.ocr(img_path, cls=True)
    print(result)

if __name__ == '__main__':
    main()