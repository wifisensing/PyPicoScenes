from PyPicoScenes import *
import random
import time

cppyy.include("PyPicoScenesCommon.hpp")
FrameDumper = cppyy.gbl.FrameDumper

EchoProbeWorkingMode = cppyy.gbl.EchoProbeWorkingMode
EchoProbeInjectionContent = cppyy.gbl.EchoProbeInjectionContent
EchoProbePacketFrameType = cppyy.gbl.EchoProbePacketFrameType
EchoProbeReplyStrategy = cppyy.gbl.EchoProbeReplyStrategy
EchoProbeParameters = cppyy.gbl.EchoProbeParameters

def buildBasicFrame(taskId, frameType, nic, **kwargs):
    frame = nic.initializeTxFrame()
    if frameType == EchoProbePacketFrameType.SimpleInjectionFrameType and kwargs.get("injectorContent") == EchoProbeInjectionContent.NDP:
        frame.setTxParameters(nic.getUserSpecifiedTxParameters()).txParameters.NDPFrame = True
    else:
        frame.setTxParameters(nic.getUserSpecifiedTxParameters())
        frame.setTaskId(taskId)
        frame.setPicoScenesFrameType(frameType)
        if frameType == EchoProbePacketFrameType.SimpleInjectionFrameType and kwargs.get("injectorContent") == EchoProbeInjectionContent.Full:
            frame.addSegment(std.make_shared[ExtraInfoSegment](nic.getFrontEnd().buildExtraInfo()))
        if frameType == EchoProbePacketFrameType.EchoProbeRequestFrameType:
            frame.addSegment(std.make_shared[ExtraInfoSegment](nic.getFrontEnd().buildExtraInfo()))
        if kwargs.get("randomPayloadLength"):
            l = int(kwargs["randomPayloadLength"])
            vec = [random.randint(0,255) for _ in range(l)]
            segment = std.make_shared[PayloadSegment]("RandomPayload", vec, PayloadDataType.RawData)
            frame.addSegment(segment)

    sourceAddr = nic.getFrontEnd().getMacAddressPhy()
    if kwargs.get("randomMAC"):
        sourceAddr[0] = random.randint(0,255)
        sourceAddr[1] = random.randint(0,255)
    frame.setSourceAddress(sourceAddr.data())
    frame.setDestinationAddress(MagicIntel123456.data())
    frame.set3rdAddress(nic.getFrontEnd().getMacAddressPhy().data())
    frame.txParameters.forceSounding = True

    if kwargs.get("inj_for_intel5300"):
        frame.setSourceAddress(MagicIntel123456.data())
        frame.setDestinationAddress(MagicIntel123456.data())
        frame.set3rdAddress(nic.getFrontEnd().getMacAddressPhy().data())
        frame.setForceSounding(False)
        frame.setChannelCoding(ChannelCodingEnum.BCC)
    return frame

def transmit_frame(nicName:str = '4'):
    # Start PicoScenes platform
    picoscenes_start()
    # Get network interface card
    nic = getNic(nicName)

    ## Transmit packets in TX_CBW_20_HT format
    txParameters = nic.getUserSpecifiedTxParameters()
    txParameters.frameType = PacketFormatEnum.PacketFormat_HT
    txParameters.guardInterval = GuardIntervalEnum.GI_800
    txParameters.cbw = ChannelBandwidthEnum.CBW_20
    txParameters.coding[0] = ChannelCodingEnum.BCC
    
    '''
    ## Transmit packets in TX_CBW_160_HESU format
    txParameters = nic.getUserSpecifiedTxParameters()
    txParameters.frameType = PacketFormatEnum.PacketFormat_HESU
    txParameters.guardInterval = GuardIntervalEnum.GI_3200
    txParameters.cbw = ChannelBandwidthEnum.CBW_160
    txParameters.coding[0] = ChannelCodingEnum.LDPC
    '''
    
    ''' ## Transmit packets in TX_CBW_160_VHT format
    txParameters = nic.getUserSpecifiedTxParameters()
    txParameters.frameType = PacketFormatEnum.PacketFormat_VHT
    txParameters.guardInterval = GuardIntervalEnum.GI_800
    txParameters.cbw = ChannelBandwidthEnum.CBW_160
    txParameters.coding[0] = ChannelCodingEnum.BCC
    '''
    
    cppyy.gbl.setTxParameters(nic, txParameters)
    
    # Start NIC service
    nic.startTxService()

    cf_repeat = 1000
    tx_delay_us = 5e3

    for i in range(int(cf_repeat)):
        taskId = random.randint(9999, 65535)
        txframe = buildBasicFrame(taskId, EchoProbePacketFrameType.SimpleInjectionFrameType, nic)
        nic.transmitPicoScenesFrameSync(txframe)
        time.sleep(tx_delay_us/1e6)
        
    # Stop NIC's Rx service
    nic.stopRxService()
    # Stop NIC's Tx service
    nic.stopTxService()
    # Stop PicoScenes platform
    picoscenes_stop()
    # picoscenes_wait() blocks until picoscenes_stop() is called
    picoscenes_wait()

if __name__ == "__main__":
    transmit_frame("4")