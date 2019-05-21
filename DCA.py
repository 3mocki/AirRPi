import requests, json
from Msgtype import *
from ResultCode import *
from globalVar import *
from State import *

class DCA_class:
    currentState_2 = SSN_INFORMED_STATE
    sspDcaReqRetries = 0
    msgType = SSP_DCAREQ

    # geoData
    payload = {
        "lat": '32.892425',
        "lng": '-117.234657',
        "nat": 'Q30',
        "state": 'Q99',
        "city": 'Q16552'
    }

    # eId is Sensor Serial Number
    eId = ""
    cId = ""
    MTI = ""
    TTI = ""
    MOBF = ""

    def fnPackSspDcaReq(self):
        packedMsg = {
            "header": {
                "msgType": self.msgType,  # msgHeader[0]
                "msgLen": len(str(self.payload)),  # msgHeader[1:2]
                "endpointId": self.eId  # msgHeader[3:5]
            },
            "payload": self.payload
        }
        return packedMsg  # return packedMsg

    def fnSendSspDcaReq(self):
        global rt
        print("| SEN | SET | DCA STATE | " + str(self.currentState_2) + "=> SSN_Informed_State")
        print("| SEN | PACK| SSP:DCA-REQ")
        response = requests.post(url_1, json=self.fnPackSspDcaReq())
        print("| SEN | SEND| REQ | SSP:DCA-REQ | " + str(self.fnPackSspDcaReq()))
        self.stateChange()
        print("| SEN | SET | DCA STATE | " + str(self.currentState_2) + "=> Half_CID_Informed_State")
        rt = response.elapsed.total_seconds()
        print('Response Time : ' + str(rt) + 'sec')

        t = response.json()
        print("| SEN | RCVD| RSP | " + str(t))
        data = response.text
        self.json_response = json.loads(data)

    def fnReceiveMsg(self):
        if rt > 5:
            print("Response time is exceeded 5 sec")
            self.sspDcaReqRetries += 1
            if self.sspDcaReqRetries == 5:
                self.stateChange_2(self.sspDcaReqRetries)
                print("| SEN | SET | DCA STATE | " + str(self.currentState_2) + "=> IDLE State")
                print("Maximum Retries => Quit Service")
                quit()
            else:
                self.stateChange_2(self.sspDcaReqRetries)
                self.fnSendSspDcaReq()
        else:
            self.verifyMsgHeader()
            if rcvdPayload != RES_FAILED:
                return rcvdPayload
            else:
                self.fnReceiveMsg()

    def verifyMsgHeader(self):
        global rcvdPayload
        rcvdType = self.json_response['header']['msgType'] # rcvdMsgType
        rcvdPayload = self.json_response['payload']
        # rcvdLength = len(str(self.rcvdPayload)) # rcvdLenOfPayload
        rcvdeId = self.json_response['header']['endpointId'] # rcvdEndpointId
        # expLen = rcvdLength - msg.header_size

        if rcvdeId == self.eId: # rcvdEndpointId = fnGetTemporarySensorId
            stateCheckResult = self.stateChange_3(rcvdType)
            print("| SEN | SET | DCA STATE | " + str(stateCheckResult) + "=> CID_INFORMED_STATE")
            if stateCheckResult == RES_SUCCESS:
                if rcvdType == self.msgType:
                    # if rcvdLength == expLen:
                    return rcvdPayload
        else:
            return RES_FAILED

    def UnpackMsg(self):
        if self.json_response['payload']['resultCode'] == RESCODE_SSP_DCA_OK: # 4.1
            self.cId = self.json_response['payload']['cid']
            self.MTI = self.json_response['payload']['mti']
            self.TTI = self.json_response['payload']['tti']
            self.MOBF = self.json_response['payload']['mobf']
            print("| SEN | UNPK| PYLD| SSP:DCA-RSP")
            # print("(check)cId :" + str(self.cId))
            return RES_SUCCESS
        else:
            print("System shut down. Check the result code in response payload.")
            return RES_FAILED

    def stateChange(self):
        self.currentState_2 = 'HALF_CID_INFORMED_STATE'
        return self.currentState_2

    def stateChange_2(self, Retries):
        if Retries == 5:
            self.currentState_2 = IDLE_STATE
            return self.currentState_2
        else:
            self.currentState_2 = SSN_INFORMED_STATE
            return self.currentState_2

    def stateChange_3(self, rcvdData):
        if rcvdData == SSP_DCARSP:
            if self.currentState_2 == 'HALF_CID_INFORMED_STATE':
                self.currentState_2 = CID_INFORMED_STATE
                return self.currentState_2

    def init(self):
        self.fnPackSspDcaReq()
        self.fnSendSspDcaReq()

        self.fnReceiveMsg()
        self.UnpackMsg()

if __name__ == "__main__":
    dca=DCA_class()
    dca.fnPackSspDcaReq()
    dca.fnSendSspDcaReq()

    dca.fnReceiveMsg()
    dca.UnpackMsg()