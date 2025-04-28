from PyPicoScenes import *

FrameDumper = cppyy.gbl.FrameDumper

# Simple callback function
def py_call_back(frame):
    print("-----------------------------get one frame----------------------------")
    return True

# Python callback receives frame and saves it to file
def py_call_back_dump(frame, fileName="testCSI"):
    print(f"dump a frame to {fileName}")
    # Save frame to file
    FrameDumper.getInstanceWithoutTime(fileName).dumpRxFrame(frame)
    return True

def recv_frame(nicName:str = '4'):
    # Start PicoScenes platform
    picoscenes_start()
    # Get network interface card
    nic = getNic(nicName)
    
    # Start NIC's Rx service
    nic.startRxService()

    # Register Python callbacks
    call_backs = {
        "call_back" : py_call_back,
        "call_back_dump" : py_call_back_dump,
    }
    for call_back_name, call_back in call_backs.items():
        nic.registerGeneralHandler(call_back_name, call_back)
    while (True):
        pass

    # Stop NIC's Rx service
    nic.stopRxService()
    # Stop NIC's Tx service
    nic.stopTxService()
    # Stop PicoScenes platform
    picoscenes_stop()
    # picoscenes_wait() will block until picoscenes_stop() is called
    picoscenes_wait()

if __name__ == "__main__":
    recv_frame("4")