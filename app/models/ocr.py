from paddleocr import PaddleOCR

import global_vars

BASE_DIR = global_vars.root_path + "/paddleocr/"



class Ocr(PaddleOCR):
    def __init__(self, baseDir, useGpu, totalProcessNum ):
        super().__init__(
            # det_model_dir = baseDir + "whl/det/ch/ch_PP-OCRv4_det_infer",
            # rec_model_dir = baseDir + "whl/rec/ch/ch_PP-OCRv4_rec_infer",
            # cls_model_dir = baseDir + "whl/cls/ch_ppocr_mobile_v2.0_cls_infer",
            use_angle_cls=True, 
            lang="ch",
            show_log=False,
            use_gpu=useGpu,
            use_mp=True,
            total_process_num = totalProcessNum,
            use_space_char = True,
            cls = False,

        )
