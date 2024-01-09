from app.gui.windows import Windows
from app.models.rsa import RsaModel
from app.models.key import Key
from app.models.api import ApiModel
from app.models.mac import MacAddressModel
import global_vars
import tkinter

if __name__ == '__main__':

    rsaModel = RsaModel()
    # publicKeyPath = global_vars.root_path + '/public_key.pem'
    # publicKey = rsaModel.publicKey(publicKeyPath)
    # message = "1=7=" + time.strftime("%Y-%m-%d",time.gmtime())


    # data = rsaModel.encrytedData(message, publicKey)
    # print(data)
    
    akeyModel = Key()

    keyResult = akeyModel.readKey(global_vars.root_path + "/key")

    if len(keyResult) == 0 :
        activateState=False

    privateKeyPath = global_vars.root_path + '/private_key.pem'
    privateKey = rsaModel.privateKey(privateKeyPath)
    keyData = rsaModel.decryptedData(keyResult, privateKey)
    
    message = ""
    if len(keyData) == 0:
        activateState = False
    else:
        activateState = True
        splitData = keyData.split("=")

        apiModel = ApiModel()
        name = splitData[0]
        sign = apiModel.md5Sign({"name": name})

        try:
            resultData = apiModel.getStateAndMacAddress({"name": name, "sign": sign})

            if 'status' in resultData:
                if resultData['status'] == 0:
                    activateState = False

                if resultData['status'] == 1:
                    data = resultData['data']
                    macAddressModel = MacAddressModel()
                    macAddress = macAddressModel.getMacAddress()
                    
                    if data['state'] == 0 or data['mac_address'] != macAddress:
                        activateState = False
        except Exception as errorInfo:
            message = "网络异常"

    windows = Windows(activateState, message)
    windows.run()







