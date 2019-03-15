import random, requests, json, subprocess
from uuid import getnode as get_mac
from Msgtype import *
from ResultCode import *
from globalVar import *
from State import *

class SIR_class:
    currentState = IDLE_STATE
    # mac = get_mac()  # 1.3 WiFi MAC Address
    line = subprocess.getstatusoutput("/sbin/ifconfig | grep ether")
    line2 = str(line)[19:36]
    mac = line2.replace(':', '')

    # 1.2 msgHeader[0]
    msgType = SSP_SIRREQ
    # 1.5 msgHeader[1:2]
    payload = {
        "wmac": mac
    }
    sspSirReqRetries = 0
    # 1.1 Generate Temporary SID(randomly generated by a sensor)
    eId = random.randrange(1, 10 ** 3)

    ssn =""

    # 1.0 packedMsg
    def packedMsg(self):
        # 1.5 packedMsg include Header and Payload
        packedMsg = {
            "header": {
                "msgType" : self.msgType,
                "msgLen" : len(str(self.payload)), # 1.4 size(msgPayload)
                "endpointId" : self.eId # 1.2 msgHeader[3:5]
            },
            "payload" : self.payload
        }
        return packedMsg # 1.6 return packedMsg

    def responseTimer(self):
        global response, rt
        # print("Timer Working")
        print("| SEN | PACK| SSP:SIR_REQ")
        response = requests.post(url_1, json=self.packedMsg())  # 2.2 fnSendMsg => json
        print("| SEN | SEND| REQ | SSP:SIR-REQ | " + str(self.packedMsg()))
        rt = response.elapsed.total_seconds()
        # print('(check)rspTime :' + str(rt))
        return rt

    # 3.1 fnRecvMsg()
    def rcvdMsgPayload(self):
        # Set to Default value in Timer
        if rt > 5:
            print("Retry Checking response time")
            self.sspSirReqRetries += 1
            self.responseTimer()  # 3.2 => go to responseTimer 2.0
            if self.sspSirReqRetries == 5:
                self.statecheck()
                print("Maximum Retries => Quit Service")
                quit()
        else:
            self.verifyMsgHeader()
            if rcvdPayload != RES_FAILED:
                return rcvdPayload

    def verifyMsgHeader(self): # 3.3.1
        global rcvdPayload
        rcvdType = self.json_response['header']['msgType'] # rcvdMsgType
        rcvdPayload = self.json_response['payload']
        # rcvdLength = len(str(rcvdPayload)) # rcvdLenOfPayload
        rcvdeId = self.json_response['header']['endpointId'] # rcvdEndpointId
        # expLen = rcvdLength - msg.header_size

        if rcvdeId == self.eId: # rcvdEndpointId = fnGetTemporarySensorId
            stateCheckResult = self.stateCheck()
            print("| SEN | SET | SIR STATE | " + str(stateCheckResult) + "=> HALF_SSN_INFORMED_STATE")
            if stateCheckResult == RES_SUCCESS:
                if rcvdType == self.msgType:
                    # if rcvdLength == expLen:
                    return rcvdPayload
        else:
            return RES_FAILED

    def UnpackMsg(self):
        if self.json_response['payload']['resultCode'] == RESCODE_SSP_SIR_OK: # 4.1
            self.ssn = self.json_response['payload']['ssn'] # 4.2
            print("| SEN | UNPK| PYLD| SSP:SIR-RSP")
            # print("(check)ssn :" + (self.ssn))
        else:
            if self.json_response['payload']['resultCode'] == RESCODE_SSP_SIR_CONFLICT_OF_TEMPORARY_SENSOR_ID:
                self.responseTimer()
            else:
                print("(check) quit")
                quit()

    def stateCheck(self):
        if self.msgType == SSP_SIRRSP:
            if self.currentState == IDLE_STATE:
                self.currentState = HALF_SSN_INFORMED_STATE
                return self.currentState

    def init(self):
        print("| SEN | SET | SIR STATE | " + str(self.currentState) + "=> IDLE STATE")

        self.responseTimer()

        t = response.json()
        print("| SEN | RCVD| RSP | " + str(t))
        data = response.text
        self.json_response = json.loads(data)

        self.rcvdMsgPayload()
        self.UnpackMsg()