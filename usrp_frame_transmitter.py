from PyPicoScenes import *
import random
import time

cppyy.include("PyPicoScenesCommon.hpp")
FrameDumper = cppyy.gbl.FrameDumper

EchoProbeInjectionContent = cppyy.gbl.EchoProbeInjectionContent
EchoProbePacketFrameType = cppyy.gbl.EchoProbePacketFrameType

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

def transmit_frame(nicName: str = 'usrp'):
    # Initialize PicoScenes platform
    picoscenes_start()
    # Retrieve SDR/NIC device handle
    nic = getNic(nicName)
    # Get front-end controller
    frontEnd = nic.getTypedFrontEnd[AbstractSDRFrontEnd]()

    # === Transmitter Configuration ===
    # Set txcm to 1 (tx-channel:[0])
    txChannelList = [0]
    frontEnd.setTxChannels(txChannelList)
    nic.getUserSpecifiedTxParameters().txcm = frontEnd.getTxChainMask()

    ## Clock configuration (default: internal)
    frontEnd.setClockSource("internal")
    frontEnd.setTimeSource("internal")

    ## Set carrier frequency to 5300 MHz
    frontEnd.setCarrierFrequency(5300e6)

    ## Set transmit power to 75% of maximum
    if (frontEnd.getTxChainMask() != 0):
        frontEnd.setTxpower(0.75)
    
    ''' ## Alternative: Set absolute transmit power to 20 dBm
    if (frontEnd.getTxChainMask() != 0):
        frontEnd.setTxpower(20)
    '''

    ## AGC configuration (disabled by default)
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setAGC(False)

    ## Antenna configuration (default: "TX/RX")
    frontEnd.setTxAntennas(["TX/RX", "TX/RX"])

    ## Multithreading configuration (default: 1 thread)
    frontEnd.setNumThreads4RxDecoding(1)
    
    ## Configure packet format as TX_CBW_40_VHT
    ### Set sampling rate to 40 MHz
    if (not frontEnd.getHardwareSupportedTxChannels().empty()):
        frontEnd.setTxSamplingRate(40e6)
    ### Set resampling ratio
    frontEnd.setTxResampleRatio(1)
    txParameters = nic.getUserSpecifiedTxParameters()
    ### PHY format: 802.11ac VHT
    txParameters.frameType = PacketFormatEnum.PacketFormat_VHT
    txParameters.guardInterval = GuardIntervalEnum.GI_800
    ### Channel bandwidth: 40 MHz
    txParameters.cbw = ChannelBandwidthEnum.CBW_40
    ### Channel coding: BCC
    txParameters.coding[0] = ChannelCodingEnum.BCC
    
    ## MCS configuration (default: 0)
    txParameters.mcs[0] = 0
    ## Spatial streams (default: 1)
    txParameters.numSTS[0] = 1
    ## Extra sounding symbols (default: 0)
    txParameters.numExtraSounding = 0

    ''' ## Alternative configuration: TX_CBW_40_VHT_LDPC
    ### Set sampling rate to 40 MHz/s
    if (not frontEnd.getHardwareSupportedTxChannels().empty()):
        frontEnd.setTxSamplingRate(40e6)
    frontEnd.setTxResampleRatio(1)
    txParameters = nic.getUserSpecifiedTxParameters()
    txParameters.frameType = PacketFormatEnum.PacketFormat_VHT
    txParameters.guardInterval = GuardIntervalEnum.GI_800
    txParameters.cbw = ChannelBandwidthEnum.CBW_40
    txParameters.coding[0] = ChannelCodingEnum.LDPC
    '''
    
    ''' ## 802.11be EHT SU configuration
    ### Set sampling rate to 20 MHz/s
    if (not frontEnd.getHardwareSupportedTxChannels().empty()):
        frontEnd.setTxSamplingRate(20e6)
    frontEnd.setTxResampleRatio(1)
    txParameters = nic.getUserSpecifiedTxParameters()
    txParameters.frameType = PacketFormatEnum.PacketFormat_EHTSU
    txParameters.guardInterval = GuardIntervalEnum.GI_3200
    txParameters.cbw = ChannelBandwidthEnum.CBW_20
    txParameters.coding[0] = ChannelCodingEnum.LDPC
    '''

    cppyy.gbl.setTxParameters(nic, txParameters)
    # Start transmission service
    nic.startTxService()

    # Transmission parameters
    cf_repeat = 1000        # Number of frames to transmit
    tx_delay_us = 5e3       # Inter-frame interval (5 ms)

    # Frame transmission loop
    for i in range(int(cf_repeat)):
        taskId = random.randint(9999, 65535)
        txframe = buildBasicFrame(taskId, EchoProbePacketFrameType.SimpleInjectionFrameType, nic)
        nic.transmitPicoScenesFrameSync(txframe)
        time.sleep(tx_delay_us/1e6)

    # Cleanup sequence
    nic.stopRxService()     # Stop receiver service
    nic.stopTxService()      # Stop transmitter service
    picoscenes_stop()        # Shutdown platform
    picoscenes_wait()        # Block until shutdown completes

if __name__ == "__main__":
    transmit_frame("usrp")