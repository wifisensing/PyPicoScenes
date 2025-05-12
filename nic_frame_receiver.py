from PyPicoScenes.PyPicoScenes import *

FrameDumper = cppyy.gbl.FrameDumper

def get_simple_call_back():
    # Simple callback function
    def py_call_back(frame):
        print("-----------------------------get one frame----------------------------")
        return True
    return py_call_back

def get_call_back_dump(fileName="testCSI"):
    # Python callback receives frame and saves it to file
    def py_call_back_dump(frame):
        print(f"dump a frame to {fileName}")
        # Save frame to file
        FrameDumper.getInstanceWithoutTime(fileName).dumpRxFrame(frame)
        return True
    return py_call_back_dump

def get_call_back_plot(nicName:str = "4"):
    # Get CSILivePlotter instance for NIC with PHYPath_ID "4"
    CSILivePlotter.getInstance("4").startPlotService()

    # Set CSI magnitude to absolute value
    absoluteStyle = CSILivePlotter.MagnitudePlotStyle(CSILivePlotter.MagnitudePlotStyle.Absolute)
    # Alternative: Set CSI magnitude to logarithmic scale
    # logStyle = CSILivePlotter.MagnitudePlotStyle(CSILivePlotter.MagnitudePlotStyle.Log)

    CSILivePlotter.getInstance("4").setMagnitudePlotStyle(absoluteStyle)
    plotter = CSILivePlotter.getInstance("4")
    # Python callback receives frame and plot it
    def py_call_back_plot(frame):
        if plotter and plotter.isPlotServiceOn():
            # Must call this function before plotting the frame
            frame.csiSegment.getCSI().removeCSDAndInterpolateCSI()
            plotter.plotFrameAsync(frame)
        return True
    return py_call_back_plot

def recv_frame(nicName:str = '4'):
    # Start PicoScenes platform
    picoscenes_start()
    # Get network interface card
    nic = getNic(nicName)
    
    # Start NIC's Rx service
    nic.startRxService()

    # Register Python callbacks
    call_backs = {
        "call_back" : get_simple_call_back(),
        "call_back_dump" : get_call_back_dump(),
        "call_back_plot" : get_call_back_plot(nicName),
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