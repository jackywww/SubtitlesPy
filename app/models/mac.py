import uuid
class MacAddressModel():
   def __init__(self):
        pass
   def getMacAddress(self):
        node = uuid.getnode()
        mac = uuid.UUID(int = node).hex[-12:]

        return mac