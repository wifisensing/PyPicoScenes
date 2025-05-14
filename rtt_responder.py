from PyPicoScenes.PyPicoScenes import *
from PyPicoScenes.buildFrames import *
import threading
import random
import time

import ReplySegment
RTTFrameType = cppyy.gbl.RTTFrameType
Reply = cppyy.gbl.Reply
ReplySegment = cppyy.gbl.ReplySegment


class RTTResponder:
    def __init__(self, nicName: str="usrp"):
        # Start PicoScenes platform
        picoscenes_start()
        # Get network interface card
        self.self.nic = getNic(nicName)
        
        frontEnd = self.nic.getTypedFrontEnd[AbstractSDRFrontEnd]()
        ## Set transmission parameters
        txChannelList = [0]
        frontEnd.setTxChannels(txChannelList)
        self.nic.getUserSpecifiedTxParameters().txcm = frontEnd.getTxChainMask()
        if (frontEnd.getTxChainMask() != 0):
            frontEnd.setTxpower(0.1)
        frontEnd.setTxAntennas(["TX/RX"])
    
        ## Set reception parameters
        rxChannelList = [0]
        frontEnd.setRxChannels(rxChannelList)
        if (frontEnd.getRxChainMask() != 0):
            frontEnd.setRxGain(0.65)
        frontEnd.setRxAntennas(["RX2"])
        frontEnd.setNumThreads4RxDecoding(1)
    
        ## Apply preset configurations
        frontEnd.applyPreset("TR_CBW_20_NonHT", False)
        frontEnd.setClockSource("internal")
        frontEnd.setTimeSource("internal")
        frontEnd.setCarrierFrequency(2300e6)
        if (frontEnd.getRxChainMask() != 0):
            frontEnd.setAGC(False)
     
        ## Start Tx/Rx service
        tmp = std.vector[std.array[std.uint8_t, 6]]()
        tmp.push_back(MagicIntel123456)
        self.nic.getFrontEnd().setDestinationMACAddressFilter(tmp)
        self.nic.startRxService()
        self.nic.startTxService()
        
        ## rtt parameters
        self.condition = threading.Condition()
        self.TIME_OUT = 2
        self.received = True
        self.t = [0] * 4
        currentTaskId = 0
    
    def get_call_back(self):
        def call_back(frame):
            if frame.PicoScenesHeader and frame.PicoScenesHeader.frameType == std.uint8_t(RTTFrameType.RTTInitiation) and                    \
            not std.equal(frame.standardHeader.addr2.cbegin(), frame.standardHeader.addr2.cend(), self.nic.getFrontEnd().getMacAddressPhy().cbegin()):   
                if isIntelMVMTypeNIC(self.nic.getDeviceType()) and frame.mvmExtraSegment and not frame.mvmExtraSegment.getDynamicInterpreter().queryField("LastTxTime"):
                   raise RuntimeError("LastTxTime is required!")
                sdrFrontEnd = self.nic.getTypedFrontEnd[AbstractSDRFrontEnd]()
                
                replyStartFrame = self.nic.initializeTxFrame()
                replyStartFrame.setTaskId(frame.PicoScenesHeader.taskId).                    \
                setPicoScenesFrameType(std.uint8_t(RTTFrameType.ReplyStart)).     \
                setTxParameters(self.nic.getUserSpecifiedTxParameters()).        \
                setDestinationAddress(MagicIntel123456.data()).                   \
                setSourceAddress(self.nic.getFrontEnd().getMacAddressPhy().data()).  \
                set3rdAddress(self.nic.getFrontEnd().getMacAddressPhy().data()) 
                sdrFrontEnd.transmit(replyStartFrame)
                time.sleep(0.01)
                
                
                frame.csiSegment.getCSI().removeCSDAndInterpolateCSI()
                replyEnd = Reply(
                    std.uint64_t(frame.sdrExtraSegment.getSdrExtra().preciseRxTime * 1e9 if isSDR(self.nic.getDeviceType()) else frame.mvmExtraSegment.getDynamicInterpreter().getField[std.uint32_t]("FTMClock")),
                    std.uint64_t(sdrFrontEnd.getLastTxStatus().txTime * 1e9 if isSDR(self.nic.getDeviceType()) else 0)
                )
                replyEndFrame = self.nic.initializeTxFrame()
                replyEndFrame.setTaskId(frame.PicoScenesHeader.taskId).                                  \
                setPicoScenesFrameType(std.uint8_t(RTTFrameType.ReplyEnd)).                              \
                addSegment(std.make_shared[ReplySegment](replyEnd)).                                \
                setTxParameters(self.nic.getUserSpecifiedTxParameters()).                           \
                setDestinationAddress(MagicIntel123456.data()).                                      \
                setSourceAddress(self.nic.getFrontEnd().getMacAddressPhy().data()).                  \
                set3rdAddress(self.nic.getFrontEnd().getMacAddressPhy().data())                       
                sdrFrontEnd.transmit(replyEndFrame)
                time.sleep(0.01)
                return True
        return call_back
    
    def startJob(self):
        self.nic.registerGeneralHandler("RTTResponderHandleFrame", self.get_call_back())

if __name__ == "__main__":
    rttResponder = RTTResponder("usrp")
    rttResponder.startJob()
        
            
            
    

