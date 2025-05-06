from PyPicoScenes import *

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

def get_call_back_plot(nicName:str = "usrp"):
    # Get CSILivePlotter instance for usrp"
    CSILivePlotter.getInstance("usrp").startPlotService()

    # Set CSI magnitude to absolute value
    absoluteStyle = CSILivePlotter.MagnitudePlotStyle(CSILivePlotter.MagnitudePlotStyle.Absolute)
    # Alternative: Set CSI magnitude to logarithmic scale
    # logStyle = CSILivePlotter.MagnitudePlotStyle(CSILivePlotter.MagnitudePlotStyle.Log)

    CSILivePlotter.getInstance("usrp").setMagnitudePlotStyle(absoluteStyle)
    plotter = CSILivePlotter.getInstance("usrp")
    # Python callback receives frame and plot it
    def py_call_back_plot(frame):
        if plotter and plotter.isPlotServiceOn():
            # Must call this function before plotting the frame
            frame.csiSegment.getCSI().removeCSDAndInterpolateCSI()
            plotter.plotFrameAsync(frame)
        return True
    return py_call_back_plot


def recv_frame(nicName: str = 'usrp'):
    # Initialize PicoScenes platform
    picoscenes_start()
    
    # Retrieve SDR/NIC device handle
    nic = getNic(nicName)
    
    # Get front-end controller
    frontEnd = nic.getTypedFrontEnd[AbstractSDRFrontEnd]()

    # === Receiver Configuration ===
    # Set RX channels to [0]
    rxChannelList = [0]
    frontEnd.setRxChannels(rxChannelList)
    
    ## Configuration for 20MHz bandwidth
    ### Set sampling rate to 20MHz/s
    if (not frontEnd.getHardwareSupportedRxChannels().empty()):
        frontEnd.setRxSamplingRate(20e6)
    ### Set resampling ratio
    frontEnd.setRxResampleRatio(1.0)
    ### Configure channel bandwidth
    frontEnd.setRxChannelBandwidthMode(ChannelBandwidthEnum(20))
    
    '''
    ## Configuration for 40MHz bandwidth
    ### Set sampling rate to 40MHz/s
    if (not frontEnd.getHardwareSupportedRxChannels().empty()):
        frontEnd.setRxSamplingRate(40e6)
    frontEnd.setRxResampleRatio(1.0)
    frontEnd.setRxChannelBandwidthMode(ChannelBandwidthEnum(40))
    '''
    
    '''
    ## Configuration for 80MHz bandwidth 
    ### Set sampling rate to 100MHz/s
    if (not frontEnd.getHardwareSupportedRxChannels().empty()):
        frontEnd.setRxSamplingRate(100e6)
    frontEnd.setRxResampleRatio(1.0)
    frontEnd.setRxChannelBandwidthMode(ChannelBandwidthEnum(80))
    '''
    
    # Clock configuration (default: internal)
    frontEnd.setClockSource("internal")
    frontEnd.setTimeSource("internal")
    
    # Center frequency configuration (2.412GHz)
    frontEnd.setCarrierFrequency(2412e6)
    
    # Gain control (65% of max gain)
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setRxGain(0.65)
    '''
    # Absolute gain setting (20dBm)
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setRxGain(20)
    '''
    
    # AGC control (disabled by default)
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setAGC(False)
        
    # Antenna configuration (default: "TX/RX")
    frontEnd.setRxAntennas(["TX/RX", "TX/RX"])
    '''
    # Alternative antenna configuration
    frontEnd.setRxAntennas(["RX2"])
    '''
    
    # Multithreading configuration
    frontEnd.setNumThreads4RxDecoding(1)
    
    # Start receiver service
    nic.startRxService()
    
    # Register callbacks
    # Register Python callbacks
    call_backs = {
        "call_back" : get_simple_call_back(),
        "call_back_dump" : get_call_back_dump(),
        "call_back_plot" : get_call_back_plot(nicName),
    }
    for call_back_name, call_back in call_backs.items():
        nic.registerGeneralHandler(call_back_name, call_back)
        
    # Main loop
    while (True):
        pass
    
    # === Cleanup ===
    # Terminate NIC receiver service
    nic.stopRxService()
    # Terminate NIC transmitter service  
    nic.stopTxService()
    # Shutdown PicoScenes platform
    picoscenes_stop()
    # picoscenes_wait() blocks indefinitely until picoscenes_stop() invocation
    picoscenes_wait()
    
if __name__ == "__main__":
    recv_frame('usrp')