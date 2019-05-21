import requests, json
from Msgtype import *
from ResultCode import *
from globalVar import *
from State import *

class DCD_class:
    currentState_3 = CID_INFORMED_STATE
    sspDcdReqRetries = 0
    msgType = SSP_DCDNOT
    payload = None
    # eId is Connection ID
    eId = ""

    def fnPackSspDcdNot(self):
        packedMsg = {
            "header": {
                "msgType" : self.msgType,
                "msgLen" : self.payload,
                "endpointId" : self.eId
            }
        }
        return packedMsg

    def fnSendSspDcdNot(self):
        global rt
        print("| SEN | SET | DCD STATE | " + str(self.currentState_3) + "=> CID INFORMED STATE")
        print("| SEN | PACK| SSP:DCD-NOT")
        response = requests.post(url_1, json=self.fnPackSspDcdNot())  # 2.2 fnSendMsg => json
        print("| SEN | SEND| REQ | SSP:DCD-NOT | " + str(self.fnPackSspDcdNot()))
        self.stateChange()
        print("| SEN | SET | DCD STATE | " + str(self.currentState_3) + "=> HALF-IDLE STATE")
        rt = response.elapsed.total_seconds()
        print('Response Time : ' + str(rt) + 'sec')

        t = response.json()
        print("| SEN | RCVD| RSP | " + str(t))
        data = response.text
        self.json_response = json.loads(data)

    # 3.1 fnRecvMsg()
    def fnReceiveMsg(self):
        if rt > 5:
            print("Response time is exceeded 5 sec")
            self.sspDcdReqRetries += 1
            self.fnSendSspDcdNot()  # 3.2 => go to responseTimer 2.0
            if self.sspDcdReqRetries == 5:
                self.stateChange_2(self.sspDcdReqRetries)
                print("| SEN | SET | DCD STATE | " + str(self.currentState_3) + "=> IDLE State")
                print("Maximum Retries => Quit Service")
                quit()
            else:
                self.stateChange_2(self.sspDcdReqRetries)
                self.fnSendSspDcdNot()
        else:
            self.verifyMsgHeader()
            if rcvdPayload != RES_FAILED:
                return rcvdPayload
            else:
                self.fnReceiveMsg()

    def verifyMsgHeader(self): # 3.3.1
        global rcvdPayload
        rcvdType = self.json_response['header']['msgType'] # rcvdMsgType
        rcvdPayload = self.json_response['payload']
        # rcvdLength = len(str(rcvdPayload)) # rcvdLenOfPayload
        rcvdeId = self.json_response['header']['endpointId'] # rcvdEndpointId
        # expLen = rcvdLength - msg.header_size

        if rcvdeId == self.eId:
            stateCheckResult = self.stateChange_3(rcvdType)
            print("| SEN | SET | DCD STATE | " + str(stateCheckResult) + "=> IDLE STATE")
            if stateCheckResult == RES_SUCCESS:
                if rcvdType == self.msgType:
                    # if rcvdLength == expLen:
                    return rcvdPayload
        else:
            print("System shutdown.")
            quit()

    def UnpackMsg(self):
        if self.json_response['payload']['resultCode'] == RESCODE_SSP_DCD_OK:
            quit()

        else:
            print("System shutdown.")
            quit()

    def stateChange(self):
        self.currentState_3 = HALF_IDLE_STATE
        return self.currentState_3

    def stateChange_2(self, Retries):
        if Retries == 5:
            self.currentState_3 = IDLE_STATE
            return self.currentState_3
        else:
            self.currentState_3 = CID_INFORMED_STATE
            return self.currentState_3
    def stateChange_3(self, rcvdData):
        if rcvdData == SSP_DCDACK:
            if self.currentState_3 == 'HALF-IDLE STATE':
                self.currentState_3 = IDLE_STATE
                return self.currentState_3


    def init(self):
        self.fnPackSspDcdNot()
        self.fnSendSspDcdNot()

        self.fnReceiveMsg()
        self.UnpackMsg()

if __name__=="__main__":
    dcd = DCD_class()
    dcd.fnPackSspDcdNot()
    dcd.fnSendSspDcdNot()
    dcd.fnReceiveMsg()
    dcd.UnpackMsg()