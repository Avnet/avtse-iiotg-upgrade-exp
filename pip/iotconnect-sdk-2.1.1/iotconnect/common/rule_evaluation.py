import sys
import copy
import threading
import time
from datetime import datetime

class rule_evaluation:    
    _command_sender = None
    
    def replace_conditional_operator(self, condition):
        try:
            condition = condition.replace(" = ", " == ")
            condition = condition.replace("AND", "and")
            condition = condition.replace("OR", "or")
            return condition
        except Exception as ex:
            return condition
            print("replace_operator : " + ex.message)
    
    def eval_exp(self,exp):
        try:
            return eval(exp)
        except Exception as ex:
            return False
    
    def evalRules(self, rule, rule_data):
        try:
            if rule == None:
                return
            
            condition = ""
            if self.has_key(rule, "con") and rule["con"] != None:
                condition = self.replace_conditional_operator(str(rule["con"]))
            
            command_text = ""
            if self.has_key(rule, "cmd") and rule["cmd"] != None:
                command_text = str(rule["cmd"])
            
            if condition != "":
                for rdata in rule_data:
                    rdata["valid"] = None
                    d = {}
                    for data in rdata["d"]:
                        if rdata["p"] == "":
                            prop = data["ln"]
                        else:
                            prop = rdata["p"] + "." + data["ln"]
                        
                        if condition.find(str(prop)) > -1 and data["v"] != None:
                            condition = condition.replace(prop, str(data["v"]))
                            d[data["ln"]] = data["v"]
                        
                    if len(d) > 0:
                        rdata["valid"] = d
                
                if self.eval_exp(condition) == True:
                    print("\n---- Rule Matched ---")
                    if self._command_sender and command_text != "":
                        self._command_sender(command_text)
                    
                    sdata = []
                    for rdata in rule_data:
                        if rdata["valid"] != None and len(rdata["valid"]) > 0:
                            sdata.append(rdata["valid"])
                    
                    if len(sdata) > 0:
                        if self.listner_callback != None:
                            self.listner_callback(sdata, rule)
                else:
                    print("\n---- Rule Not Matched ---")
        except Exception as ex:
            print("evalRules : " + ex.message)
    
    def has_key(self, data, key):
        try:
            return key in data
        except Exception as ex:
            return False
    
    @property
    def _timestamp(self):
        return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
    
    def __init__(self, listner, command_sender):
        if listner != None:
            self.listner_callback = listner
        
        if command_sender != None:
            self._command_sender = command_sender
