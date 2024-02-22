from app.gui.windows import Windows
from app.models.rsa import RsaModel
from app.models.key import Key
from app.models.api import ApiModel
from app.models.mac import MacAddressModel
import global_vars
import multiprocessing
import time
if __name__ == '__main__':
    multiprocessing.freeze_support()
    rsaModel = RsaModel()
    publicKeyPath = global_vars.root_path + '/public_key.pem'
    publicKey = rsaModel.publicKey(publicKeyPath)
    message = "self221=7=" + time.strftime("%Y-%m-%d",time.gmtime())


    data = rsaModel.encrytedData(message, publicKey)
    print(data)
    
    




