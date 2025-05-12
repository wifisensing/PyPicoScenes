from PyPicoScenes.PyPicoScenes import *
from PyPicoScenes.buildFrames import *
import time
import random
import math

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


def radar_mode(nicName:str="usrp", txFreq=2300, rxFreq=2300.001, parameters=None):
    assert parameters, "parameters can't be None"
    # Start PicoScenes platform
    picoscenes_start()
    # Get network interface card
    nic = getNic(nicName)
    
    frontEnd = nic.getTypedFrontEnd[AbstractSDRFrontEnd]()
    ## Set transmission parameters
    txChannelList = [0]
    frontEnd.setTxChannels(txChannelList)
    nic.getUserSpecifiedTxParameters().txcm = frontEnd.getTxChainMask()
    frontEnd.setTxCarrierFrequencies([txFreq * 1e6])
    if (frontEnd.getTxChainMask() != 0):
        frontEnd.setTxpower(0.1)
    frontEnd.setTxAntennas(["TX/RX"])
    
    ## Set reception parameters
    rxChannelList = [0]
    frontEnd.setRxChannels(rxChannelList)
    frontEnd.setRxCarrierFrequencies([rxFreq * 1e6])
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setRxGain(0.65)
    frontEnd.setRxAntennas(["RX2"])
    frontEnd.setNumThreads4RxDecoding(1)
    
    ## Apply preset configurations
    frontEnd.applyPreset("TR_CBW_20_EHTSU", False)
    frontEnd.setClockSource("internal")
    frontEnd.setTimeSource("internal")
    # frontEnd.setCarrierFrequency(5955e6)
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setAGC(False)
     
    ## Enable radar mode
    tmp = std.vector[std.array[std.uint8_t, 6]]()
    tmp.push_back(MagicIntel123456)
    nic.getFrontEnd().setDestinationMACAddressFilter(tmp)
    nic.getTypedFrontEnd[AbstractSDRFrontEnd]().setFullDuplex(True)
    nic.startRxService()
    nic.startTxService()
    
    # Register callbacks
    # Register Python callbacks
    call_backs = {
        "call_back_dump" : get_call_back_dump(),
        "call_back_plot" : get_call_back_plot(nicName),
    }
    for call_back_name, call_back in call_backs.items():
        nic.registerGeneralHandler(call_back_name, call_back)
    
    ## Configure transmission parameters
    frontEnd = nic.getFrontEnd()
    round_repeat = parameters.round_repeat.value_or(1)
    cf_repeat = parameters.cf_repeat.value_or(100)
    tx_delay_us = parameters.tx_delay_us
    tx_delayed_start = parameters.delayed_start_seconds.value_or(0)
    
    sfList = enumerateSamplingRates(nic, parameters)
    cfList = enumerateArbitraryCarrierFrequencies(nic, parameters)
    
    prebuiltFrames = []
    sessionId = random.randint(9999, 65535)
    
    if tx_delayed_start > 0:
        time.sleep(tx_delayed_start)
    
    if parameters.useBatchAPI:
        prebuiltFrames = buildBatchFrames(EchoProbePacketFrameType.SimpleInjectionFrameType, nic, parameters)
    for ri in range(round_repeat):
        for sf_value in sfList:
            for cf_value in cfList:
                if sf_value != frontEnd.getSamplingRate():
                    frontEnd.setSamplingRate(sf_value)
                    if parameters.delay_after_cf_change_ms.has_value():
                        time.sleep(parameters.delay_after_cf_change_ms.value() / 1e3)
                
                if cf_value != frontEnd.getCarrierFrequency():
                    frontEnd.setCarrierFrequency(cf_value)
                    if parameters.delay_after_cf_change_ms.has_value():
                        time.sleep(parameters.delay_after_cf_change_ms.value() / 1e3)
                
                if parameters.useBatchAPI:
                    framePoints = [cppyy.addressof(frame) for frame in prebuiltFrames]
                    repeats = math.ceil(1.0 * cf_repeat / framePoints.size())
                    nic.getFrontEnd().transmitFramesInBatch(framePoints, repeats)
                else:
                    for _ in range(cf_repeat):
                        taskId = random.randint(9999, 65535)
                        txframe = buildBasicFrame(taskId, EchoProbePacketFrameType.SimpleInjectionFrameType, nic, parameters)
                        nic.transmitPicoScenesFrameSync(txframe)
                        time.sleep(parameters.tx_delay_us / 1e6)        
    
    time.sleep(10)
    nic.stopRxService()
    nic.stopTxService()
    picoscenes_stop()
    picoscenes_wait()    
    
if __name__ == "__main__":
    parameters = EchoProbeParameters()
    txFreq = 2300
    rxFreq = 2300.001
    radar_mode("usrp", txFreq=txFreq, rxFreq=rxFreq, parameters=parameters)