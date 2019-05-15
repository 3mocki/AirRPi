import requests, json
from Msgtype import *
from ResultCode import *
from globalVar import *
from State import *

class DCD_class:
    currentState = CID_INFORMED_STATE
    sspDcdReqRetries = 0
    msgType = SSP_DCDNOT
    payload = None
    # eId is Connection ID
    eId = ""

    def packedMsg(self):
        packedMsg = {
            "header": {
                "msgType" : self.msgType,
                "msgLen" : self.payload,
                "endpointId" : self.eId
            }
        }
        return packedMsg

    def reponseTimer(self):
        global response, rt
        print("| SEN | SET | DCD STATE | " + str(self.currentState) + "=> CID INFORMED STATE")
        print("| SEN | PACK| SSP:SIR_REQ")
        response = requests.post(url_1, json=self.packedMsg())  # 2.2 fnSendMsg => json
        print("| SEN | SEND| REQ | SSP:DCD-NOT | " + str(self.packedMsg()))
        rt = response.elapsed.total_seconds()
        print('Response Time : ' + str(rt) + 'sec')

    # 3.1 fnRecvMsg()
    def rcvdMsgPayload(self):
        if rt > 5:
            print("Response time is exceeded 5 sec")
            self.sspDcdReqRetries += 1
            self.responseTimer()  # 3.2 => go to responseTimer 2.0
            if self.sspDcdReqRetries == 5:
                print("Maximum Retries => Quit Service")
                quit()
        else:
            self.verifyMsgHeader()
            if rcvdPayload != RES_FAILED:
                return rcvdPayload
            else:
                self.rcvdMsgPayload()

    def verifyMsgHeader(self): # 3.3.1
        global rcvdPayload
        rcvdType = self.json_response['header']['msgType'] # rcvdMsgType
        rcvdPayload = self.json_response['payload']
        # rcvdLength = len(str(rcvdPayload)) # rcvdLenOfPayload
        rcvdeId = self.json_response['header']['endpointId'] # rcvdEndpointId
        # expLen = rcvdLength - msg.header_size

        if rcvdeId == self.eId: # rcvdEndpointId = fnGetTemporarySensorId
            stateCheck = 1
            if stateCheck == RES_SUCCESS:
                if rcvdType == self.msgType:
                    # if rcvdLength == expLen:
                    return rcvdPayload
        else:
            return RES_FAILED

    def UnpackMsg(self):
        rc = self.json_response['payload']['resultCode']
        return rc

    def init(self):

        self.responseTimer()

        t = response.json()
        print("| SEN | RCVD| RSP | " + str(t))
        data = response.text
        self.json_response = json.loads(data)

        self.rcvdMsgPayload()
        self.UnpackMsg()