from SIR import SIR_class
from DCA import DCA_class
from RAD import RAD_class
import time

if __name__ == '__main__':

    try:
        print("-----------Generate SIR-----------")
        sir = SIR_class()
        sir.init()

        print("-----------Generate DCA-----------")
        dca = DCA_class()
        dca.eId = sir.ssn
        dca.init()
        init_time = int(time.time())
        while True:
            start = time.time()
            init_time += 1
            print("-----------Generate RAD-----------")
            rad = RAD_class()
            rad.eId = dca.cId
            print("----------------------------------")
            print("Real Unixtime : " + str(init_time))
            rad.init()
            end = time.time()
            communicating = end - start
            timegap = 10 - communicating
            time.sleep(timegap)


    except KeyboardInterrupt:
        # [Ctrl + C] or [Ctrl + Z]
        print("-----Quit Measuring-----")