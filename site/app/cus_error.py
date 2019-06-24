class Error(Exception):
   """Base class for other exceptions"""
   pass

class Wrong_Own(Error):
   pass

class Al_Exists(Error):
   pass

class Al_Deleted(Error):
   pass
