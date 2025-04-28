import cppyy
import cppyy.ll
import subprocess
import sys

if sys.platform.startswith("linux"):
    cppyy.add_library_path("/usr/local/PicoScenes/lib/")
elif sys.platform.startswith('win32'):
    cppyy.add_library_path("C:\\Program Files\\PicoScenes\\lib")
else:
    raise RuntimeError("Please add PicoScenes lib path here!")

cppyy.load_library("libServer")
cppyy.load_library("libmac80211Injection")
cppyy.load_library("libDSP")
cppyy.load_library("libFrontEnd")
cppyy.load_library("libIntrinsics")
cppyy.load_library("libLicense")
cppyy.load_library("libmac80211Injection")
cppyy.load_library("libNICHAL")
cppyy.load_library("librxs_parsing")
cppyy.load_library("libSDRBaseband")
cppyy.load_library("libSodiumWrapper")
cppyy.load_library("libSystemTools")


if sys.platform.startswith("linux"):
    cppyy.add_library_path("/usr/local/PicoScenes/include/")
elif sys.platform.startswith('win32'):
    cppyy.add_library_path("C:\\Program Files\\PicoScenes\\include")
else:
    raise RuntimeError("Please add PicoScenes include path here!")

cppyy.include("PicoScenes/PyPicoScenes.hxx")

cppyy.include("cstdint")
cppyy.include("exception")
cppyy.include("queue")
cppyy.include("atomic")
cppyy.include("condition_variable")

cppyy.include("PicoScenes/SDRExtraSegment.hxx")
cppyy.include("PicoScenes/PicoScenesFrameTxParameters.hxx")
cppyy.include("PicoScenes/MVMExtraSegment.hxx")
cppyy.include("PicoScenes/UDPService.hxx")
cppyy.include("PicoScenes/LicenseModel.hxx")
cppyy.include("PicoScenes/LoggingService.hxx")
cppyy.include("PicoScenes/PayloadSegment.hxx")
cppyy.include("PicoScenes/AbstractPicoScenesFrameSegment.hxx")
cppyy.include("PicoScenes/LicenseService.hxx")
cppyy.include("PicoScenes/RxSBasicSegment.hxx")
cppyy.include("PicoScenes/IntelRateNFlag.hxx")
cppyy.include("PicoScenes/ExtraInfoSegment.hxx")
cppyy.include("PicoScenes/SignalMatrix.hxx")
cppyy.include("PicoScenes/PicoScenesCommons.hxx")
cppyy.include("PicoScenes/FrontEndModePreset.hxx")
cppyy.include("PicoScenes/FrameDumper.hxx")
cppyy.include("PicoScenes/TaggedThreadPool.hxx")
cppyy.include("PicoScenes/SDRFrontEndConfigurations.hxx")
cppyy.include("PicoScenes/CSISegment.hxx")
cppyy.include("PicoScenes/BasebandSignalSegment.hxx")
cppyy.include("PicoScenes/FrontEndConfigurations.hxx")
cppyy.include("PicoScenes/Singleton.hxx")
cppyy.include("PicoScenes/CargoSegment.hxx")
cppyy.include("PicoScenes/DynamicFieldInterpretation.hxx")
cppyy.include("PicoScenes/FIFOWaitBlocker.hxx")
cppyy.include("PicoScenes/SDRHardwareInformation.hxx")
cppyy.include("PicoScenes/Intrinsics.hxx")
cppyy.include("PicoScenes/SoapySDRUtils.hxx")
cppyy.include("PicoScenes/ModularPicoScenesFrame.hxx")
cppyy.include("PicoScenes/RXSExtraInfo.hxx")
cppyy.include("PicoScenes/BBSignalsFileWriter.hxx")
cppyy.include("PicoScenes/DSPRateTracker.hxx")
cppyy.include("PicoScenes/AbstractSDRFrontEnd.hxx")

std = cppyy.gbl.std
ChannelBandwidthEnum = cppyy.gbl.ChannelBandwidthEnum
LoggingService = cppyy.gbl.LoggingService
AbstractSDRFrontEnd = cppyy.gbl.AbstractSDRFrontEnd
uint16_t = cppyy.gbl.uint16_t
ModularPicoScenesRxFrame = cppyy.gbl.ModularPicoScenesRxFrame
FrontEndModePreset = cppyy.gbl.FrontEndModePreset
PacketFormatEnum = cppyy.gbl.PacketFormatEnum
GuardIntervalEnum = cppyy.gbl.GuardIntervalEnum
PicoScenesFrameTxParameters = cppyy.gbl.PicoScenesFrameTxParameters
MagicIntel123456 = cppyy.gbl.MagicIntel123456
TxPrecodingParameters = cppyy.gbl.TxPrecodingParameters
ExtraInfoSegment = cppyy.gbl.ExtraInfoSegment
PicoScenesDeviceType = cppyy.gbl.PicoScenesDeviceType
isIntelMVMTypeNIC = cppyy.gbl.isIntelMVMTypeNIC
ChannelCodingEnum = cppyy.gbl.ChannelCodingEnum
PayloadDataType = cppyy.gbl.PayloadDataType
PayloadSegment = cppyy.gbl.PayloadSegment

PicoScenesStart = cppyy.gbl.PicoScenesStart
PicoScenesWait = cppyy.gbl.PicoScenesWait
PicoScenesStop = cppyy.gbl.PicoScenesStop
getNIC = cppyy.gbl.getNIC

def picoscenes_start(commandString:str = None):
    proc = subprocess.Popen(
        ["PicoScenes", "-q"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    try:
        stdout, stderr = proc.communicate(timeout=10)
    except subprocess.TimeoutExpired:
        proc.kill()
    PicoScenesStart()

def picoscenes_wait():
    PicoScenesWait()

def picoscenes_stop():
    PicoScenesStop()

def getNic(nicName):
    nic = getNIC(nicName)
    return nic

if __name__ == "__main__":
    pass