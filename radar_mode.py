from PyPicoScenes import *
from buildFrames import *
import time
import random
import math

EchoProbeParameters = cppyy.gbl.EchoProbeParameters

def get_call_back_dump(fileName="testCSI"):
    # Python callback receives frame and saves it to file
    def py_call_back_dump(frame):
        print(f"dump a frame to {fileName}")
        # Save frame to file
        FrameDumper.getInstanceWithoutTime(fileName).dumpRxFrame(frame)
        return True
    return py_call_back_dump

def radar_mode(nicName:str="usrp", parameters=None):
    assert parameters, "parameters can't be None"
    # Start PicoScenes platform
    picoscenes_start()
    # Get network interface card
    nic = getNic(nicName)
    
    frontEnd = nic.getTypedFrontEnd[AbstractSDRFrontEnd]()
    ## 设置发送参数
    txChannelList = [0]
    frontEnd.setTxChannels(txChannelList)
    nic.getUserSpecifiedTxParameters().txcm = frontEnd.getTxChainMask()
    if (frontEnd.getTxChainMask() != 0):
        frontEnd.setTxpower(0.1)
    frontEnd.setTxAntennas(["TX/RX"])
    
    ## 设置接收参数
    rxChannelList = [0]
    frontEnd.setRxChannels(rxChannelList)
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setRxGain(0.65)
    frontEnd.setRxAntennas(["RX2"])
    frontEnd.setNumThreads4RxDecoding(1)
    
    ## 
    frontEnd.applyPreset("TR_CBW_20_EHTSU", False)
    frontEnd.setClockSource("internal")
    frontEnd.setTimeSource("internal")
    frontEnd.setCarrierFrequency(5955e6)
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setAGC(False)
     
    ## 开启radar模式
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
    }
    for call_back_name, call_back in call_backs.items():
        nic.registerGeneralHandler(call_back_name, call_back)
    
    ##
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
        prebuiltFrames = buildBatchFrames(EchoProbePacketFrameType.SimpleInjectionFrameType)
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
    radar_mode("usrp", parameters)