from PyPicoScenes.PyPicoScenes import *
from PyPicoScenes.buildFrames import *
import random
import time
import threading

import ReplySegment
RTTFrameType = cppyy.gbl.RTTFrameType
Reply = cppyy.gbl.Reply
ReplySegment = cppyy.gbl.ReplySegment


class RTTInitiator:
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
        self.nic.getTypedFrontEnd[AbstractSDRFrontEnd]().setFullDuplex(True)
        self.nic.startRxService()
        self.nic.startTxService()
        
        ## rtt parameters
        self.condition = threading.Condition()
        self.TIME_OUT = 2
        self.received = True
        self.t = [0] * 4
        currentTaskId = 0
    
    def get_call_back(self):
        def handleFrame(frame):
            frameType = frame.PicoScenesHeader.frameType
            
            if frameType == std.uint8_t(RTTFrameType.ReplyEnd):
                segment =frame.txUnknownSegments.at("Reply")
                replySegment =  ReplySegment(segment.getSyncedRawBuffer().data(), segment.getSyncedRawBuffer().size())
                reply = replySegment.getReply()
                self.t[0] = std.uint64_t(frame.sdrExtraSegment.SDRExtra.lastTxTime * 1e9)
                self.t[1] = reply.lastRxTime
                self.t[2] = reply.lastTxTime
                self.t[3] = std.uint64_t(frame.sdrExtraSegment.SDRExtra.preciseRxTime * 1e9)
                print(f"RTT: distance is {(self.t[1]-self.t[0]+self.t[3]-self.t[2]) * 3 / 20.0} m")
                self.received = True
            return True
        return handleFrame
    
    def startJob(self, repeat=1000, delayStartTime=1):
        self.nic.registerGeneralHandler("RTTInitiatorHandleFrame", self.get_call_back())
        time.sleep(delayStartTime)
        for i in range(repeat):
            with self.condition:
                self.condition.wait_for(lambda : self.received, timeout=self.TIME_OUT)
                taskId = random.randint(9999, 65535)
                txFrame = self.nic.initializeTxFrame()
                txFrame.setPicoScenesFrameType(std.uint8_t(RTTFrameType.RTTInitiation)).   \
                    setDeviceType(self.nic.getDeviceType()).                               \
                    setDestinationAddress(MagicIntel123456.data()).                        \
                    setSourceAddress(self.nic.getFrontEnd().getMacAddressPhy().data()).    \
                    setTxParameters(self.nic.getUserSpecifiedTxParameters()).              \
                    setTaskId(taskId)
                txFrame.txParameters.mcs[0] = 1
                txFrame.txParameters.frameType = PacketFormatEnum.PacketFormat_NonHT

                currentTaskId = taskId
                print(f"RTT: Initializing RTT session: {currentTaskId}")
                self.nic.transmitPicoScenesFrame(txFrame)
                self.received = False
                time.sleep(0.5)

if __name__ == "__main__":
    rttInitiator = RTTInitiator("usrp")
    rttInitiator.startJob(100, 1)
            
            
    

