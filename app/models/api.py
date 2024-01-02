import requests
import hashlib
import global_vars

class ApiModel():
   def __init__(self):
      self.md5Pre = "2024_Gai_subtitles"
      
   
   def post(self, url, parms):
      r = requests.post(url, json=parms)
      return r.json()
   
   def activate(self, data):
      return self.post(global_vars.baseUrl + "v1/activate", data)
   
   def getStateAndMacAddress(self, data):
      return self.post(global_vars.baseUrl + "v1/record", data)
   
   def md5Sign(self, data):
      if 'name' in data :
         name = data['name']
      else:
         name =""
      
      if 'days' in data :
         days = '{}'.format(data['days'])
      else:
         days = ""

      if 'mac_address' in data :
         macAddress = data['mac_address']
      else:
         macAddress = ""

      str = self.md5Pre + name + days + macAddress

      md5Object = hashlib.md5()
      md5Object.update(str.encode('utf-8'))

      return md5Object.hexdigest()
