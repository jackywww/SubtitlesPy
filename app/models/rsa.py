import rsa
import base64
import uuid

class RsaModel():
    def __init__(self):
        pass

    def newKeys(self, length):
        if length is None:
            length = 512

        publicKey, privateKey = rsa.newkeys(length)

        return publicKey, privateKey

    def publicKey(self, publicKeyFile):
        with open(publicKeyFile, 'rb') as file:
            publicKeyData = file.read()
            publicKey = rsa.PublicKey.load_pkcs1(publicKeyData)

        return publicKey
    
    def privateKey(self, privateKeyFile):
        with open(privateKeyFile, 'rb') as file:
            privateKeyData = file.read()
            privateKey = rsa.PrivateKey.load_pkcs1(privateKeyData)

        return privateKey
    
    def saveKeys(self, publicKey, publicKeyFile, privateKey, privateKeyFile):
        try:
            with open(publicKeyFile, 'wb') as file:
                file.write(publicKey.save_pkcs1())

            with open(privateKeyFile, 'wb') as file:
                file.write(privateKey.save_pkcs1())
            
            return True
        
        except:
            return False
        

    def encrytedData(self, message, publicKey):
        encrytedData = rsa.encrypt(bytes(message, encoding='utf-8') ,pub_key = publicKey)

        return str(base64.b64encode(encrytedData), encoding='utf-8')
    
    def decryptedData(self, message, privateKey):
        try:
            base64Decode = base64.b64decode(message)
            decryptedData = rsa.decrypt(base64Decode, priv_key = privateKey)

            return str(decryptedData, encoding='utf-8')
        except:
            return ""

#生成公钥、私钥
# publicKey, privateKey=rsa.newkeys(512)

# with open('public_key.pem', 'wb') as file:
#     file.write(publicKey.save_pkcs1())

# with open('private_key.pem', 'wb') as file:
#     file.write(privateKey.save_pkcs1())


# message = str(uuid.uuid1()) + "d7"
# print(message)
# encrytedData = rsa.encrypt(bytes(message, encoding='utf-8'),pub_key=publicKey)

# aa = base64.b64encode(encrytedData)
# base64Decode = base64.b64decode(aa)
# print(base64Decode)
# decryptedData = rsa.decrypt(base64Decode, priv_key=privateKey)

# print(str(base64.b64encode(encrytedData), encoding='utf-8'), decryptedData)
