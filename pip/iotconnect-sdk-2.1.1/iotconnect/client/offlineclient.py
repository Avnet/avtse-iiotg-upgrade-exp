import sys, os
import json
import threading
import datetime
import math
from iotconnect.IoTConnectSDKException import IoTConnectSDKException

class offlineclient:
    _data_path = None
    _sdk_config = None
    _lock = False
    
    def Send(self, data):
        if self._file_size == 0:
            print("\nFile Size not found")
            return
                
        _data = json.dumps(data) + "\n"
        self._data_path = self.new_active_file(self._data_path)
        
        if self._data_path:
            try:
                with open(self._data_path, "a") as dfile:
                    dfile.write(_data)
            except:
                return False
        return True
    
    def send_back_to_client(self):
        try:
            #self._lock = False
            #return
            log_path = os.path.join(sys.path[0], "logs")
            files = self.get_log_files()
            if len(files) > 0:
                for f in files:
                    isAction = 0
                    logs = self.read_file_data(f)
                    if len(logs) > 0:
                        rData = []
                        for obj in logs:
                            isSend = False
                            if self.sendBackToClient != None:
                                isSend = self.sendBackToClient(obj)
                            
                            if isSend == False:
                                rData.append(obj)
                        if len(rData) > 0:
                            isAction = 1             
                        if isAction == 0: #DELETE
                            print("\nPublish offline data : " + str(len(logs)))
                            self.delete_file(f)
                        if isAction == 1: #WRITE
                            self.write_file(f, rData)
            self._lock = False
        except:
            self._lock = False
    
    def PublishData(self):
        if self._lock == False:
            self._lock = True
            self.send_back_to_client()
    
    def event_call(self, name, taget, arg):
        _thread = threading.Thread(target=getattr(self, taget), args=arg)
        _thread.daemon = True
        _thread.setName(name)
        _thread.start()
    
    def get_active_file(self):
        try:
            data_path = None
            log_path = os.path.join(sys.path[0], "logs")
            path_staus=os.path.exists(log_path)
            if path_staus:
                pass
            else:
                os.mkdir(log_path)
            files = os.listdir(log_path)
            if len(files) > 0:
                for f in files:
                    if f.startswith("active"):
                        fpath = os.path.join(sys.path[0] + "/logs", f)
                        fsize = round(self.convert_unit(float(os.stat(fpath).st_size), self._file_unit), 2)
                        if fsize < self._file_size:
                            data_path = fpath
                        else:
                            os.rename(fpath, os.path.join(sys.path[0] + "/logs", f.replace("active_", "")))
            if data_path == None:
                data_path = os.path.join(sys.path[0], "logs/active_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt")
            
            #Remove first file if size limit exceed 
            self.remove_first_file()
            
            return data_path
        except Exception as ex:
            return os.path.join(sys.path[0], "logs/active_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt")
    
    def new_active_file(self, file_path):
        try:
            is_new = False
            data_path = None
            if os.path.exists(file_path):
                fsize = round(self.convert_unit(float(os.stat(file_path).st_size), self._file_unit), 2)
                if fsize < self._file_size:
                    data_path = file_path
                else:
                    os.rename(file_path, file_path.replace("active_", ""))
            if data_path == None:
                is_new = True
                data_path = os.path.join(sys.path[0], "logs/active_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt")
            
            #Remove first file if size limit exceed
            if is_new:
                self.remove_first_file()
            
            return data_path
        except Exception as ex:
            return os.path.join(sys.path[0], "logs/active_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".txt")
    
    def get_log_files(self):
        logs = []
        try:
            log_path = os.path.join(sys.path[0], "logs")
            files = os.listdir(log_path)
            if len(files) > 0:
                for f in files:
                    fpath = os.path.join(sys.path[0] + "/logs", f)
                    if f.startswith("active"):
                        os.rename(fpath, fpath.replace("active_", ""))
                        fpath = fpath.replace("active_", "")
                    
                    if os.path.exists(fpath):
                        logs.append(fpath)
            return logs
        except:
            return logs
    
    def read_file_data(self, file_path):
        logs = []
        try:
            try:
                with open(file_path, "r") as dfile:
                    _data = dfile.read()
            except:
                _data = None
            
            if _data != None:
                _data = _data.split("\n")
            
            for obj in _data:
                try:
                    if len(obj) > 0:
                        logs.append(json.loads(obj))
                except:
                    print("\nInvalid file data : " + obj)
            return logs
        except:
            return logs
    
    def delete_file(self, file_path):
        try:
            os.remove(file_path)
            print("\nLog file deleted successfully")
        except:
            print("\nErrro while delete file")
    
    def clear_all_files(self):
        try:
            log_path = os.path.join(sys.path[0], "logs")
            filelist = [ f for f in os.listdir(log_path) if f ]
            for f in filelist:
                os.remove(os.path.join(log_path, f))
        except:
            print("\nyou can not clear the directory.....\n")
    
    def write_file(self, file_path, logs):
        try:
            isDone = False
            try:
                wData = []
                for log in logs:
                    wData.append(json.dumps(log))
                wData = "\n".join(wData)
                with open(file_path, "w") as dfile:
                    dfile.write(wData)
                isDone = True
            except:
                print("\nErrro while write file")
            if isDone:
                print("\nLog file write successfully")
            else:
                self.delete_file(file_path)
        except:
            print("\nErrro while write file")
    
    def convert_unit(self, size_in_bytes, unit = 0):
        try:
            if unit == 1:#KB
                return size_in_bytes/1024
            elif unit == 2:#MB
                return size_in_bytes/(1024*1024)
            elif unit == 3:#GB
                return size_in_bytes/(1024*1024*1024)
            else:
                return size_in_bytes
        except:
            return size_in_bytes
    
    def get_file_size(self, max_size, file_count):
        try:
            tSize = max_size * (1024 * 1024)
            sSize = tSize / file_count
            return self.convert_unit(sSize, 1)
        except:
            return 0
    
    def remove_first_file(self):
        try:
            log_path = os.path.join(sys.path[0], "logs")
            files = os.listdir(log_path)
            if len(files) >= self.file_count:
                v=[]
                for i in range(0,len(files)):
                    v.append(int(files[0].replace('-','').replace('.txt','')))
                fpath = os.path.join(sys.path[0] + "/logs", files[v.index(min(v))])
                os.remove(fpath)
        except:
            pass
    
    def has_key(self, data, key):
        try:
            return key in data
        except:
            return False
    
    def __init__(self, sdk_config, sendBackToClient):
        self._sdk_config = sdk_config
        self.max_size = 10 #MB
        self.file_count = 5
        
        if self.has_key(sdk_config, "maxSize"):
            self.max_size = int(sdk_config["maxSize"])
        
        if self.has_key(sdk_config, "fileCount"):
            self.file_count = int(sdk_config["fileCount"])
        
        self._file_size = self.get_file_size(self.max_size, self.file_count) #KB
        self._file_unit = 1 #KB
        self._data_path = self.get_active_file()
        self.sendBackToClient = sendBackToClient
