class Key():
   def __init__(self):
        pass
   def writeKey(self, path, data):
        try:
            with open(path, 'w') as f:  
                f.write(data)
        except:
           return False
        
        return True
   
   def readKey(self, path):
        result = ""
        try:
            with open(path, 'rb') as f:
               result = f.read()
        except:
           return ""
        
        return str(result, encoding='utf-8')