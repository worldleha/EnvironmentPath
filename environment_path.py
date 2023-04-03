import win32api
import win32con
import sys
import os


def isPath(path):
    if path == "":
        return False
    elif path[0] == "%":
        return True
    else:
        return os.path.exists(path)
    
class EnvironmentPath():

    def __init__(self, key:"key" = None):
        self.key = EnvironmentPath._OpenEnvironmentKey()
        
    def __enter__(self):
        return self
    
    def __exit__(self,exc_type,exc_value,traceback):
        win32api.RegCloseKey(self.key)
        print(exc_value)
        del self
        return True
        
    @classmethod
    def _OpenEnvironmentKey(cls) -> "Key":
        regRoot = win32con.HKEY_LOCAL_MACHINE
        regPath = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        regFlags = win32con.WRITE_OWNER|win32con.KEY_WOW64_64KEY|win32con.KEY_ALL_ACCESS|win32con.KEY_SET_VALUE
        key = win32api.RegOpenKeyEx(regRoot, regPath, 0, regFlags)
        return key

    def ListPath(self) -> list:
        try:
            pathList = self.pathList
            
        except:
            value = win32api.RegQueryValueEx(self.key,'Path')[0]
            pathList = list(filter(lambda x: len(x)> 1, value.split(";")))
            self.pathList = pathList

        return pathList



    def ChangePath(self) -> None:
        pathList = self.ListPath()
        pathList = filter(isPath, pathList)
        value = ';'.join(pathList) + ";"
        win32api.RegSetValueEx(self.key, "Path", 0, win32con.REG_SZ, value)
        

    def AddPath(self, path:"str") -> list:
        pathList = self.ListPath()
        pathList.append(path)
        self.ChangePath()
        return pathList
    
    def DelPath(self, index:int=-1, path:"str"=None) -> list:
        if path:
            pathList = self.ListPath()
            pathList.remove(path)
        elif index!=-1:
            pathList = self.ListPath()
            pathList.pop(index)
        else:
            pathList = self.ListPath()
        self.ChangePath()
        return pathList
    

           
