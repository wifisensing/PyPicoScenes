import sys
import os
import random
from .PyPicoScenes import *

FrameDumper = cppyy.gbl.FrameDumper
EchoProbeInjectionContent = cppyy.gbl.EchoProbeInjectionContent
EchoProbePacketFrameType = cppyy.gbl.EchoProbePacketFrameType
EchoProbeParameters = cppyy.gbl.EchoProbeParameters

def buildBasicFrame(taskId, frameType, nic, parameters):
    frame = nic.initializeTxFrame()
    if frameType == EchoProbePacketFrameType.SimpleInjectionFrameType and parameters.injectorContent == EchoProbeInjectionContent.NDP:
        frame.setTxParameters(nic.getUserSpecifiedTxParameters()).txParameters.NDPFrame = True
    else:
        frame.setTxParameters(nic.getUserSpecifiedTxParameters())
        frame.setTaskId(taskId)
        frame.setPicoScenesFrameType(frameType)
        if frameType == EchoProbePacketFrameType.SimpleInjectionFrameType and parameters.injectorContent == EchoProbeInjectionContent.Full:
            frame.addSegment(std.make_shared[ExtraInfoSegment](nic.getFrontEnd().buildExtraInfo()))
        if frameType == EchoProbePacketFrameType.EchoProbeRequestFrameType:
            frame.addSegment(std.make_shared[ExtraInfoSegment](nic.getFrontEnd().buildExtraInfo()))
        if parameters.randomPayloadLength.has_value():
            l = parameters.randomPayloadLength.value()
            vec = [random.randint(0,255) for _ in range(l)]
            segment = std.make_shared[PayloadSegment]("RandomPayload", vec, PayloadDataType.RawData)
            frame.addSegment(segment)

    sourceAddr = nic.getFrontEnd().getMacAddressPhy()
    if parameters.randomMAC:
        sourceAddr[0] = random.randint(0,255)
        sourceAddr[1] = random.randint(0,255)
    frame.setSourceAddress(sourceAddr.data())
    if parameters.inj_target_mac_address.has_value():
        frame.setDestinationAddress(parameters.inj_target_mac_address.data())
    else:
        frame.setDestinationAddress(MagicIntel123456.data())
    frame.set3rdAddress(nic.getFrontEnd().getMacAddressPhy().data())
    frame.txParameters.forceSounding = True

    if parameters.inj_for_intel5300.value_or(False):
        frame.setSourceAddress(MagicIntel123456.data())
        frame.setDestinationAddress(MagicIntel123456.data())
        frame.set3rdAddress(nic.getFrontEnd().getMacAddressPhy().data())
        frame.setForceSounding(False)
        frame.setChannelCoding(ChannelCodingEnum.BCC)
    return frame

def buildBatchFrames(frameType, nic, parameters):
    frameBatches = []
    batchLength = parameters.batchLength
    if(parameters.cf_repeat.has_value() and parameters.cf_repeat.value()<batchLength):
        batchLength = parameters.cf_repeat.value()
    for i in range(batchLength):
        frame = nic.initializeTxFrame()
        frame.setTaskId(random.randint(9999, 30000))   \
        .setPicoScenesFrameType(frameType)             \
        .addSegment(std.make_shared[ExtraInfoSegment](nic.getFrontEnd().buildExtraInfo())) \
        .setDestinationAddress(MagicIntel123456.data()) \
        .setSourceAddress(MagicIntel123456.data() if parameters.inj_for_intel5300 else nic.getFrontEnd().getMacAddressPhy().data()) \
        .set3rdAddress(MagicIntel123456.data() if parameters.inj_for_intel5300 else nic.getFrontEnd().getMacAddressPhy().data())    \
        .setTxParameters(nic.getUserSpecifiedTxParameters()) \
        .setForceSounding(not parameters.inj_for_intel5300)  \
        .setChannelCoding(ChannelCodingEnum.BCC if parameters.inj_for_intel5300 else frame.txParameters.coding[0])

        frame.txParameters.NDPFrame = (frameType == EchoProbePacketFrameType.SimpleInjectionFrameType and parameters.injectorContent == EchoProbeInjectionContent.NDP)
        if(parameters.randomPayloadLength.has_value()):
            vec = [random.randint(0,255) for _ in range(parameters.randomPayloadLength.value())]
            segment = std.make_shared[PayloadSegment]("RandomPayload", vec, PayloadDataType.RawData)
            frame.addSegment(segment)
        
        splitFrames = frame.autoSplit(1350)
        if(isSDR(nic.getFrontEnd().getFrontEndType()) and not splitFrames.empty()):
            signals = nic.getTypedFrontEnd[AbstractSDRFrontEnd]().generateMultiChannelSignals(splitFrames[0], nic.getFrontEnd().getTxChannels().size())
            signalLength = signals[0].size()
            perPacketDurationUs = signalLength * 1e6 / nic.getTypedFrontEnd[AbstractSDRFrontEnd]().getTxSamplingRate()
            
            for currentFrame in splitFrames:
                actualIdleTimePerFrameUs = parameters.tx_delay_us - perPacketDurationUs
                currentFrame.txParameters.postfixPaddingTime = actualIdleTimePerFrameUs / 1e6
                nic.getTypedFrontEnd[AbstractSDRFrontEnd]().prebuildSignals(currentFrame, nic.getFrontEnd().getTxChannels().size())
        
        frameBatches = splitFrames
    return frameBatches

def enumerateSamplingRates(nic, parameters):
    deviceType = nic.getDeviceType()
    if deviceType == PicoScenesDeviceType.QCA9300 or deviceType == PicoScenesDeviceType.USRP:
        return enumerateArbitrarySamplingRates(nic, parameters)
    else:
        return [nic.getFrontEnd().getSamplingRate()]

def enumerateArbitrarySamplingRates(nic, parameters):
    frequencies = []
    sf_begin = parameters.sf_begin.value_or(nic.getFrontEnd().getSamplingRate())
    sf_end = parameters.sf_end.value_or(nic.getFrontEnd().getSamplingRate())
    sf_step = parameters.sf_step.value_or(5e6)
    cur_sf = sf_begin
    
    if (sf_step == 0):
        raise RuntimeError("sf_step = 0")

    if sf_end < sf_begin and sf_step > 0:
        raise RuntimeError("sf_step > 0, however sf_end < sf_begin.")
    
    if sf_end > sf_begin and sf_step < 0:
        raise RuntimeError("sf_step < 0, however sf_end > sf_begin.")
    
    while 1:
        frequencies.append(cur_sf)
        cur_sf += sf_step
        if((sf_step > 0 and cur_sf <= sf_end) or (sf_step < 0 and cur_sf >= sf_end)):
            pass
        else:
            break
    return frequencies

def enumerateCarrierFrequencies(nic, parameters):
    return enumerateArbitraryCarrierFrequencies(nic, parameters)

def enumerateArbitraryCarrierFrequencies(nic, parameters):
    frequencies = []
    cf_begin = parameters.cf_begin.value_or(nic.getFrontEnd().getCarrierFrequency())
    cf_end = parameters.cf_end.value_or(nic.getFrontEnd().getCarrierFrequency())
    cf_step = parameters.cf_step.value_or(5e6)
    cur_cf = cf_begin
    
    if cf_step == 0:
        raise ValueError("cf_step = 0")
    if cf_end < cf_begin and cf_step > 0:
        raise ValueError("cf_step > 0, however cf_end < cf_begin.")
    if cf_end > cf_begin and cf_step < 0:
        raise ValueError("cf_step < 0, however cf_end > cf_begin.")
    while 1:
        frequencies.append(cur_cf)
        cur_cf += cf_step
        if (cf_step > 0 and cur_cf <= cf_end) or (cf_step < 0 and cur_cf >= cf_end):
            pass
        else:
            break
    return frequencies