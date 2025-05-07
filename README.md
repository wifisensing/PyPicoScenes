# ​1. PyPicoScenes​​ 
PyPicoScenes is a Python binding library for the C++-based Integrated Sensing and Communication (ISAC) research framework [PicoScenes](https://ps.zpj.io/index.html). Leveraging Cppyy's dynamic binding technology, it achieves seamless encapsulation of the underlying C++ APIs, providing researchers with a Python programming interface that combines high performance and development efficiency. The Python version fully inherits the original platform's hardware compatibility and algorithmic innovation while deeply integrating with the Python ecosystem, significantly lowering the development barriers for Wi-Fi sensing and communication synergy research.

# 2. Installation
PyPicoScenes relies on Python's cppyy library along with PicoScenes header files and dynamic libraries. Currently supported platforms include Ubuntu, macOS, and Windows.
## 2.1. Installing PyPicoScenes on Ubuntu
1. ​​PicoScenes Installation​  
[Refer to the PicoScenes installation guide here](https://ps.zpj.io/installation.html#picoscenes-software-installation).
2. Anaconda Installation​  
[Refer to the Anaconda installation guide here](https://anaconda.org/anaconda/conda).
3. Update Anaconda Environment​  
Activate your conda environment using conda activate ENV_NAME. If the libstdc++ dynamic library in Conda is outdated, run:
```bash
    conda install -c conda-forge libstdcxx-ng=13 -y  
```
4. Install cppyy && Dependencies  
cppyy is a Cling/LLVM-based dynamic binding tool that enables seamless Python-C++ interaction through runtime C++ code parsing. Its key advantages include no precompiled bindings, support for C++98 to C++20 standards, and compatibility with both PyPy and CPython interpreters. We recommend installing cppyy and its dependencies via Anaconda:
```bash
    conda create -n ENV_NAME python=3.10  
    conda activate ENV_NAME  
    pip install -r requirements  
```
5. Verify Installation  
Navigate to the PyPicoScenes directory and run `python parse_frame.py`. Successful cppyy installation will output:
```bash
    <cppyy.gbl.std.optional<ModularPicoScenesRxFrame> object at 0xeb54fa0>  
```

## 2.2. Installing PyPicoScenes on Windows
1. PicoScenes Installation​  
[Refer to the PicoScenes installation guide here](https://ps.zpj.io/installation.html#picoscenes-software-installation).
2. Install MSVC Build Tools​  
Both VS2019 and VS2022 can compile cppyy. For VS2022 users, additional installations are required:
    * Windows 10 SDK
    * MSVC v142 - VS2019 C++ x64/x86 build tools
3. Install cppyy  
Use venv to avoid polluting system directories and enable full cleanup by simply deleting the virtual environment directory (e.g., "WORK" in this example). Open ​​Visual Studio `x64 Native Tools Command Prompt`​​, and ​​for VS2022 users​​, specify the `VS2019 v142` toolchain:
```bash
    # Set build environment to VS2019  
    # Set VCToolsInstallDir to your actual Visual Studio installation directory.
    set VCToolsInstallDir=C:\Program Files\Microsoft Visual Studio\2019\Community\VC\Tools\MSVC\14.29.30133\  
    set PATH=%VCToolsInstallDir%\bin\Hostx64\x64;%PATH%  

    # Create Python virtual environment  
    python -m venv WORK  
    WORK\Scripts\activate  

    # Install cppyy v3.5.0  
    python -m pip install cppyy-cling==6.32.8 --no-deps --no-build-isolation --force-reinstall  
    python -m pip install cppyy-backend==1.15.3 --no-deps --no-build-isolation --force-reinstall  
    python -m pip install CPyCppyy==1.13.0 --no-deps --no-build-isolation --force-reinstall  
    python -m pip install cppyy==3.5.0 --no-deps --no-build-isolation --force-reinstall  
```
4. Verify Installation  
Execute WORK\Scripts\activate to activate the Python environment created in Step 3. Navigate to the PyPicoScenes directory and run `python parse_frame.py`. Successful cppyy installation will output:
```bash
    <cppyy.gbl.std.optional<ModularPicoScenesRxFrame> object at 0xeb54fa0>  
```


# 3. Cppyy Wrapping for PicoScenes 
[Cppyy](https://cppyy.readthedocs.io/en/latest/#), built upon the Cling interpreter, is a dynamic runtime Python-C++ bidirectional binding tool that generates efficient interfaces through real-time parsing of C++ code, enabling deep interoperability between the two languages. Its core value lies in zero manual wrapping, high performance, low memory overhead, and support for complex scenarios like cross-language inheritance, template instantiation, and exception mapping. It significantly simplifies the process of calling C++ libraries from Python, making it particularly suitable for large-scale projects and interactive development.   
```python
    """
    The following example uses STL to demonstrate how to use cppyy for interaction between Python and C++.
    """
    # Using C++ vector
    import cppyy
    cppyy.include("vector")
    # C++ symbols reside in cppyy.gbl namespace, access via cppyy.gbl
    vec = cppyy.gbl.std.vector[int](3, 1)
    print(vec)  # Outputs { 1, 1, 1 }
    # Using size() method of vector<int> in Python
    print(vec.size())
    # Using push_back() method of vector<int> in Python
    vec.push_back(5)
    print(vec)  # Outputs { 1, 1, 1, 5 }
    print(vec.size())
```
The following explains how to use cppyy to wrap PicoScenes.

## 3.1. Adding PicoScenes to cppyy's Path
Assuming the absolute installation path of PicoScenes is **​​your_picoscenes_path**​​, first add the header files and dynamic libraries to cppyy's path:
```python
    import cppyy
    import cppyy.ll
    # Add header file path
    cppyy.add_include_path("your_picoscenes_path/include")
    # Add dynamic library path
    cppyy.add_library_path("your_picoscenes_path/lib")
```

## 3.2. Importing C++ Header Files
Use `cppyy.include` to import required header files:
```python
    cppyy.include("PicoScenes/SystemTools.hxx")
    cppyy.include("PicoScenes/QCA9300FrontEnd.hxx")
    cppyy.include("PicoScenes/IntelRateNFlag.hxx")
    cppyy.include("PicoScenes/AbstractSDRFrontEnd.hxx")
    cppyy.include("PicoScenes/USRPFrontEnd.hxx")
    # And other required header files
```

## 3.3. Loading Dynamic Libraries
Use `cppyy.load_library` to load required dynamic libraries:
```python
    cppyy.load_library("libDSP")
    cppyy.load_library("libFrontEnd")
    cppyy.load_library("libIntrinsics")
    cppyy.load_library("libLicense")
    cppyy.load_library("libmac80211Injection")
    cppyy.load_library("libNICHAL")
    cppyy.load_library("librxs_parsing")
    # And other required dynamic libraries
```

## 3.4. Using C++ APIs
After importing header files and dynamic libraries, all C++ symbols reside in the cppyy.gbl namespace and can be accessed via Python. For example, to retrieve a USRP NIC:
```python
    nicName = "usrp"
    nic = cppyy.gbl.NICPortal.getInstance().getNIC(nicName)
    print(nic)
    # nic is an AbstractNIC object, e.g.:
    # nic: <cppyy.gbl.AbstractNIC object at 0x561264e43b28 held by std::shared_ptr<AbstractNIC> at 0x561264e25c40>

    # Start the NIC's RxService
    nic.startRxService()
    # Stop the NIC's RxService
    nic.stopRxService()
```

# 4. Quick Start
PyPicoScenes encapsulates the core APIs of the underlying PicoScenes framework, enabling developers to implement WiFi packet transceiving and CSI measurement through Python interfaces ​​without implementing complex C++ plugins​​. To utilize the transceiver functionalities of NICs (Network Interface Cards) or USRP SDR devices, follow these steps:
## 4.1. Workflow Overview
1. Platform Initialization  
Execute `picoscenes_start()` to launch the PicoScenes runtime environment.
2. Hardware Acquisition  
Acquire the target hardware device via `getNic(nicName="SDR/NIC")`.
3. Hardware Configuration  
Configure RF front-end parameters (e.g., sampling rate, bandwidth, center frequency) via Python APIs.
4. Tx parameters set up(optional)  
When implementing frame transmission functionality, the tx parameters (e.g., packet format, MCS, STS) must be configured via Python APIs. 
5. Functional Implementation​​  
Activate the NIC's transceiver services and execute data transmission/reception operations using the hardware-specific low-level APIs.
6. Registering Python Callbacks(optional)  
PyPicoScenes allows registering Python callback functions to process received WiFi packets. It is particularly important to note that the first formal parameter of the registered callback function must represent the WiFi packet, while all subsequent formal parameters must have default values specified. For example:
```python
    def call_back(frame, arg1=1, arg2=2, arg3=3,...)
```
7. Runtime Control  
Call `picoscenes_wait` to block the main thread and maintain platform execution.
8. Platform Termination  
Deactivate the NIC's transceiver services and invoke `picoscenes_stop()` to shut down the platform (note that `picoscenes_wait()` remains in a blocking state prior to this invocation).
## 4.2. Key Functionalities
* CSI File Parsing  
* CSI Measurement with SDR​ device
* WiFi Packet Transmission via SDR device​  
* CSI Measurement with Commercial NIC
* WiFi Packet Transmission via Commercial NIC

## 4.3. CSI File Parsing
The binary CSI file ​​`rx_by_usrpN210.csi`​​ is generated by PicoScenes through signal acquisition via a USRP N210 device. To decode the complete frame structure, invoke the `fromBuffer()` class method of the ModularPicoScenesRxFrame class, which performs direct deserialization from raw byte buffers into protocol-compliant frame objects.



```python
import struct
import numpy as np
from PyPicoScenes import *
import os

def parseCSIFile(filename: str = "", pos: int = 0, num: int = 0):
    """  
    Deserializes IEEE 802.11 frames from PicoScenes CSI binary files.  

    Args:  
        filename: Path to .csi binary file (little-endian format)  
        pos: Byte offset to start parsing (default=0)  
        num: Maximum frames to extract (0=read all remaining)  

    Returns:  
        List of ModularPicoScenesRxFrame objects  

    Raises:  
        IOError: File access failures  
        struct.error: Invalid binary formatting  
    """  
    res = []
    count = 0
    try:
        with open(filename, "rb") as f:
            # Get total file length
            f.seek(0, os.SEEK_END)
            lens = f.tell()
            f.seek(0, os.SEEK_SET)
            if num == 0:
                num = lens - pos  # Read remaining content
            while pos < (lens - 4) and count < num:
                header = f.read(4)
                if len(header) < 4:
                    break
                # Parse field length (adjust byte order if needed)
                # Assuming little-endian byte order (adjust if necessary)
                field_len = struct.unpack("<I", header)[0] + 4
                # Rewind pointer and read complete field
                f.seek(-4, os.SEEK_CUR)

                data = f.read(field_len)
                if len(data) < field_len:
                    break
                
                # Deserialize frame from buffer
                frame = ModularPicoScenesRxFrame.fromBuffer(np.frombuffer(data, dtype=np.uint8), field_len, True)
                if frame:
                    res.append(frame)
                pos += field_len
                count += 1

    except Exception as e:
        print(f"Failed to parse CSI file: {e}")
        return []
    return res

fileName = "rx_by_usrpN210.csi"
res = parseCSIFile(fileName)
print(res[0])
```

    <cppyy.gbl.std.optional<ModularPicoScenesRxFrame> object at 0xf5017a0>


## 4.4. WiFi Packet Reception & CSI Measurement via SDR
This section demonstrates how to implement ​​PHY-layer frame reception​​ and ​​Channel State Information (CSI) measurement​​ using SDR platforms (e.g., USRP N210/X310) through PyPicoScenes' granular API controls. The framework enables full-stack decoding of 802.11a/g/n/ac/ax/be protocols with ​​real-time CSI extraction​​. Developers can dynamically configure the receiver chain through the following core parameters:
* Rx-Channel Selection​​ (configured via setRxChannels for multi-channel capture)
* RF Bandwidth​​ (adjusted using setRxSamplingRate and PicoScenesFrameRxParameters.cbw)
* ​Carrier Frequency​​ (setCarrierFrequency for frequency agility)
* ​Gain Control​​ (proportional or absolute modes via setRxGain)
* Antenna Array​​ (selected through setRxAntennas)
* Resampling Optimization​​ (setRxResampleRatio for signal reconstruction)
* Parallel Decoding​​ (setNumThreads4RxDecoding for multi-threaded processing)

### 4.4.1. Single-Channel Rx by Single NI USRP Device


```python
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
recv_frame('usrp')
```

The rx-channel and rxcm options are functionally identical, both used to configure receive channels, but they differ in parameter format: rx-channel employs a direct listing of channel numbers (e.g., 0,1,2,3), while rxcm uses a bitmask representation (e.g., 15, which corresponds to binary 1111, indicates the activation of RF channels [0,1,2,3]). It is important to note that multi-channel reception only represents the configuration of physical layer resources and is not equivalent to MIMO transmission technology. The encoding rules for rxcm are as follows:
* 1 (binary 01): Only the 1st receive channel, corresponding to channelList as [0];
* 2 (binary 10): Only the 2nd receive channel, corresponding to channelList as [1];
* 3 (binary 11): Both the 1st and 2nd channels, corresponding to channelList as [0,1];
* 4 (binary 100): The 3rd receive channel, corresponding to channelList as [2];


### 4.4.2. Multi-Channel Rx by Single NI USRP Device
PicoScenes supports multi-channel Rx and even multi-USRP combined multi-channel Rx. For example, the NI USRP B210, X310, and other advanced models have two or more independent RF channels. PicoScenes supports receiving dual/multi-channel signals and decoding MIMO frames.


```python
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

def recv_frame(nicName:str = 'usrp'):
    # Initialize PicoScenes platform
    picoscenes_start()
    
    # Retrieve SDR/NIC device handle
    nic = getNic(nicName)
    
    # Get front-end controller
    frontEnd = nic.getTypedFrontEnd[AbstractSDRFrontEnd]()

    # === Receiver Configuration ===
    # Set RX channels to [0,1]
    rxChannelList = [0,1]
    frontEnd.setRxChannels(rxChannelList)
    
    ## Configuration for 40MHz bandwidth
    ### Set sampling rate to 40MHz/s
    if (not frontEnd.getHardwareSupportedRxChannels().empty()):
        frontEnd.setRxSamplingRate(40e6)
    ### Set resampling ratio
    frontEnd.setRxResampleRatio(1.0)
    ### Configure channel bandwidth
    frontEnd.setRxChannelBandwidthMode(ChannelBandwidthEnum(40))
    
    # Clock configuration (default: internal)
    frontEnd.setClockSource("internal")
    frontEnd.setTimeSource("internal")
    
    # Center frequency configuration (2.412GHz)
    frontEnd.setCarrierFrequency(5190e6)
    
    # Gain control (65% of max gain)
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setRxGain(0.65)
    
    # AGC control (disabled by default)
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setAGC(False)
        
    # Antenna configuration (default: "TX/RX")
    frontEnd.setRxAntennas(["TX/RX", "TX/RX"])
    
    # N-thread multithread Rx decoding, default is 1
    # frontEnd.setNumThreads4RxDecoding(1)
    
    # Start receiver service
    nic.startRxService()
    
    # Register callbacks
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

recv_frame()
```

## 4.5. Transmitting WiFi Packets Using SDR Devices
This section explains how to implement ​​PHY-layer frame transmission​​ using SDR hardware (e.g., USRP N210/X310) through PyPicoScenes' granular API controls. Developers can precisely configure the transmit chain through the following critical parameters:
* Multi-Channel Selection​​ (specify physical port indices via setTxChannels)
* ​RF Bandwidth​​ (configured using setTxSamplingRate and PicoScenesFrameTxParameters.cbw)
* Frame Format​​ (supports VHT/EHT-SU and other 802.11ac/ax/be standards)
* Guard Interval​​ (anti-multipath options like GI_800/GI_3200)
* Channel Coding​​ (BCC/LDPC encoding schemes)
* ​Transmit Power​​ (setTxpower with scaling/absolute modes)
* Carrier Frequency​​ (setCarrierFrequency for frequency agility)
* ​Antenna Array​​ (select antennas via setTxAntennas)

These capabilities enable advanced applications such as ​​MIMO precoding validation​​, ​​protocol stack compatibility testing​​, and ​​high-density signal emulation​​, providing researchers with precise control over wireless signal generation for complex experimental scenarios.
### 4.5.1. Single-Device Tx with Rich Low-Level Controls


```python
from PyPicoScenes import *
from buildFrames import *
import random
import time

def transmit_frame(nicName: str = 'usrp', parameters=None):
    assert parameters, "parameters can't be None"
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
        txframe = buildBasicFrame(taskId, EchoProbePacketFrameType.SimpleInjectionFrameType, nic, parameters)
        nic.transmitPicoScenesFrameSync(txframe)
        time.sleep(tx_delay_us/1e6)

    # Cleanup sequence
    nic.stopRxService()     # Stop receiver service
    nic.stopTxService()      # Stop transmitter service
    picoscenes_stop()        # Shutdown platform
    picoscenes_wait()        # Block until shutdown completes

parameters = EchoProbeParameters()
transmit_frame("usrp", parameters)
```

The tx-channel and txcm options are functionally identical, both used to configure transmit channels, but they differ in parameter format: tx-channel uses a direct listing of channel numbers (e.g., 0,1,2,3), while txcm employs a bitmask representation (e.g., 15, which corresponds to binary 1111, indicates the activation of all four RF channels). It is important to note that multi-channel transmission only represents the configuration of physical layer resources and is not equivalent to MIMO transmission technology. The encoding rules for txcm are as follows:
* 1 (binary 01): Only the 1st transmit channel, corresponding to channelList as [0];
* 2 (binary 10): Only the 2nd transmit channel, corresponding to channelList as [1];
* 3 (binary 11): Both the 1st and 2nd transmit channels, corresponding to channelList as [0,1];
* 4 (binary 100): The 3rd transmit channel, corresponding to channelList as [2];

### 4.5.2. Multi-Channel (RF Chain) and MIMO Tx with NI USRP Devices
PyPicoScenes supports multi-channel transmission using NI USRP devices, either by a single device or by combining multiple devices.

#### 4.5.2.1. Multi-Channel (RF Chain) Tx for 1-STS Frame with NI USRP Device
Assuming your USRP device IDs are usrp192.168.30.2 and usrp192.168.70.2, you can use the following codes to transmit a 1-STS frame using multiple antennas.


```python
from PyPicoScenes import *
from buildFrames import *
import random
import time

def transmit_frame(nicName:str = 'usrp', parameters=None):
    assert parameters, "parameters can't be None"
    # Initialize PicoScenes platform
    picoscenes_start()
    # Retrieve SDR/NIC device handle
    nic = getNic(nicName)
    # Get front-end controller instance
    frontEnd = nic.getTypedFrontEnd[AbstractSDRFrontEnd]()

    # === Transmitter Configuration ===
    # Configure TX channels [0,1,2,3] (txcm=15)
    txChannelList = [0,1,2,3]
    frontEnd.setTxChannels(txChannelList)
    nic.getUserSpecifiedTxParameters().txcm = frontEnd.getTxChainMask()

    ## Clock synchronization configuration
    frontEnd.setClockSource("external")  # Default: "internal"
    frontEnd.setTimeSource("external")   # Default: "internal"

    ## Set RF center frequency to 5300 MHz
    frontEnd.setCarrierFrequency(5300e6)

    ## Configure TX power (75% of maximum capability)
    if (frontEnd.getTxChainMask() != 0):
        frontEnd.setTxpower(0.75)  # Relative power mode (0.0-1.0)
    
    ''' Alternative: Set absolute TX power to 20 dBm
    if (frontEnd.getTxChainMask() != 0):
        frontEnd.setTxpower(20)    # Absolute power mode (dBm)
    '''
    
    ## Automatic Gain Control configuration (disabled by default)
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setAGC(False)

    ## Antenna port configuration (default: "TX/RX")
    frontEnd.setTxAntennas(["TX/RX", "TX/RX"])

    ## Multi-thread RX decoding configuration (default: single thread)
    frontEnd.setNumThreads4RxDecoding(1)
    
    ## Configure packet format as EHT Single-User
    ### Set baseband sampling rate to 40 MHz
    if (not frontEnd.getHardwareSupportedTxChannels().empty()):
        frontEnd.setTxSamplingRate(40e6)
    ### Set resampling ratio (1: no resampling)
    frontEnd.setTxResampleRatio(1)
    txParameters = nic.getUserSpecifiedTxParameters()
    ### Packet format: EHT SU
    txParameters.frameType = PacketFormatEnum.PacketFormat_EHTSU
    txParameters.guardInterval = GuardIntervalEnum.GI_3200
    ### Channel bandwidth: 40 MHz
    txParameters.cbw = ChannelBandwidthEnum.CBW_40
    ### Forward Error Correction: LDPC
    txParameters.coding[0] = ChannelCodingEnum.LDPC

    ''' ## Alternative configuration: VHT format with 40MHz bandwidth
    ### Set baseband sampling rate to 40 MHz
    if (not frontEnd.getHardwareSupportedTxChannels().empty()):
        frontEnd.setTxSamplingRate(40e6)
    ### Set resampling ratio (1: no resampling)
    frontEnd.setTxResampleRatio(1)
    txParameters = nic.getUserSpecifiedTxParameters()
    ### Packet format: VHT
    txParameters.frameType = PacketFormatEnum.PacketFormat_VHT
    txParameters.guardInterval = GuardIntervalEnum.GI_800
    ### Channel bandwidth: 40 MHz
    txParameters.cbw = ChannelBandwidthEnum.CBW_40
    ### Forward Error Correction: LDPC
    txParameters.coding[0] = ChannelCodingEnum.LDPC
    '''

    # Apply TX parameters to NIC
    cppyy.gbl.setTxParameters(nic, txParameters)
    # Start TX service
    nic.startTxService()

    # Transmission parameters
    cf_repeat = 1000       # Number of frames to transmit
    tx_delay_us = 5e3      # Inter-frame delay in microseconds

    # Frame transmission loop
    for i in range(int(cf_repeat)):
        taskId = random.randint(9999, 65535)
        txframe = buildBasicFrame(taskId, EchoProbePacketFrameType.SimpleInjectionFrameType, nic, parameters)
        nic.transmitPicoScenesFrameSync(txframe)
        time.sleep(tx_delay_us/1e6)

    # Cleanup sequence
    nic.stopRxService()    # Stop RX service if running
    nic.stopTxService()    # Stop TX service
    picoscenes_stop()      # Shutdown PicoScenes platform
    picoscenes_wait()      # Block until shutdown completes
    
parameters = EchoProbeParameters()
transmit_frame("usrp192.168.30.2,192.168.70.2", parameters)
```

#### 4.5.2.2. Multi-Channel (RF Chain) Tx for MIMO Frame with NI USRP Device
Assuming your USRP device ID is usrp192.168.30.2,192.168.70.2, you can use the following codes to transmit a MIMO frame by multiple antennas.


```python
from PyPicoScenes import *
from buildFrames import *
import random
import time

def transmit_frame(nicName:str = 'usrp', parameters=None):
    assert parameters, "parameters can't be None"
    # Start PicoScenes platform
    picoscenes_start()
    
    # Get device handles
    nic = getNic(nicName)
    frontEnd = nic.getTypedFrontEnd[AbstractSDRFrontEnd]()

    # === Transmitter Configuration ===
    # Configure TX channels [0,1,2,3] (txcm=15)
    txChannelList = [0,1,2,3]
    frontEnd.setTxChannels(txChannelList)
    nic.getUserSpecifiedTxParameters().txcm = frontEnd.getTxChainMask()

    # Clock synchronization (external reference)
    frontEnd.setClockSource("external")  # Default: "internal"
    frontEnd.setTimeSource("external")   # Default: "internal"

    # RF configuration
    frontEnd.setCarrierFrequency(5300e6)  # 5.3 GHz center frequency
    
    # Power configuration (75% of maximum)
    if (frontEnd.getTxChainMask() != 0):
        frontEnd.setTxpower(0.75)  # Relative power mode
    
    ''' Alternative: Absolute power setting (20 dBm)
    if (frontEnd.getTxChainMask() != 0):
        frontEnd.setTxpower(20)    # Absolute power in dBm
    '''
    
    # Receiver configuration
    if (frontEnd.getRxChainMask() != 0):
        frontEnd.setAGC(False)  # Disable automatic gain control
    
    # Antenna configuration
    frontEnd.setTxAntennas(["TX/RX", "TX/RX"])  # Default antenna ports
    
    # Processing configuration
    frontEnd.setNumThreads4RxDecoding(1)  # Single-threaded RX processing
    
    # === Packet Format Configuration ===
    # EHT Single-User format with 40MHz bandwidth
    if (not frontEnd.getHardwareSupportedTxChannels().empty()):
        frontEnd.setTxSamplingRate(40e6)  # Baseband sampling rate
    
    frontEnd.setTxResampleRatio(1)  # No resampling
    txParameters = nic.getUserSpecifiedTxParameters()
    
    # EHT SU parameters
    txParameters.frameType = PacketFormatEnum.PacketFormat_EHTSU
    txParameters.guardInterval = GuardIntervalEnum.GI_3200  # 3.2μs GI
    txParameters.cbw = ChannelBandwidthEnum.CBW_40  # 40MHz channel
    txParameters.coding[0] = ChannelCodingEnum.LDPC  # LDPC coding
    txParameters.numSTS[0] = 4  # 4 spatial streams

    ''' ## Alternative Configuration 1: VHT format
    if (not frontEnd.getHardwareSupportedTxChannels().empty()):
        frontEnd.setTxSamplingRate(40e6)
    frontEnd.setTxResampleRatio(1)
    txParameters = nic.getUserSpecifiedTxParameters()
    txParameters.frameType = PacketFormatEnum.PacketFormat_VHT
    txParameters.guardInterval = GuardIntervalEnum.GI_800  # 0.8μs GI
    txParameters.cbw = ChannelBandwidthEnum.CBW_40
    txParameters.coding[0] = ChannelCodingEnum.LDPC
    '''
    
    ''' ## Alternative Configuration 2: EHTSU with 20MHz bandwidth
    if (not frontEnd.getHardwareSupportedTxChannels().empty()):
        frontEnd.setTxSamplingRate(20e6)
    frontEnd.setTxResampleRatio(1)
    txParameters = nic.getUserSpecifiedTxParameters()
    txParameters.frameType = PacketFormatEnum.PacketFormat_EHTSU
    txParameters.guardInterval = GuardIntervalEnum.GI_3200
    txParameters.cbw = ChannelBandwidthEnum.CBW_20  # 20MHz channel
    txParameters.coding[0] = ChannelCodingEnum.LDPC
    '''
    
    # Apply configuration and start transmission
    cppyy.gbl.setTxParameters(nic, txParameters)
    nic.startTxService()

    # Transmission parameters
    cf_repeat = 1000      # Number of frames to transmit
    tx_delay_us = 5e3     # 5ms inter-frame interval
    
    # Main transmission loop
    for i in range(int(cf_repeat)):
        taskId = random.randint(9999, 65535)
        txframe = buildBasicFrame(taskId, EchoProbePacketFrameType.SimpleInjectionFrameType, nic, parameters)
        nic.transmitPicoScenesFrameSync(txframe)
        time.sleep(tx_delay_us/1e6)

    # Cleanup sequence
    nic.stopRxService()  # Stop receive service
    nic.stopTxService()  # Stop transmit service
    picoscenes_stop()    # Shutdown platform
    picoscenes_wait()    # Wait for shutdown completion
    
parameters = EchoProbeParameters()
transmit_frame("usrp192.168.30.2,192.168.70.2", parameters)
```

## 4.6. WiFi Packet Reception & CSI Measurement with AX210/AX200 NICs
To enable WiFi packet reception using Intel AX210/AX200 NICs, ​​channel and bandwidth configuration must be performed via command-line tools​​ following these steps:
1. Identify NIC's PHYPath ID​​
Execute `array_status` to list available network interfaces and locate the target NIC's <PHYPath_ID>.
Example output snippet(Here, <PHYPath_ID> is 4):
```bash
    Device Status of Wi-Fi NIC array "all":
    PhyPath DEV PHY [MON] DEV_MacAddr [MON_MacAddr] [CF_Control] [BW] [CF] ProductName
    4 wlp4s0 phy0 f0:d4:15:c9:ce:a8 Wi-Fi 6 AX210/AX211/AX411 160MHz 
```

2. ​​Configure Channel Parameters​​  
Put the NIC into monitor mode by executing the command array_prepare_for_picoscenes 4 <CHANNEL_CONFIG>. Replace <CHANNEL_CONFIG> with the desired channel configuration, specified in the same format as the *freq* setting of the Linux *iw set freq* command. For example, it could be "2412 HT20", "5200 HT40-", "5745 80 5775", and so on. Refer to [Wi-Fi Channelization](https://ps.zpj.io/channels.html) for more details.
```bash
    array_prepare_for_picoscenes 4 <CHANNEL_CONFIG>
```

### 4.6.1. Monitor Wi-Fi Traffic & Measure CSI for 802.11a/g/n/ac/ax/be Frames
Before capturing WiFi packets using NICs, configure channel parameters via the array_prepare_for_picoscenes command. Examples:
```bash
    # Monitor 2422 MHz (HT20)
    array_prepare_for_picoscenes 4 "2422 HT20"

    # Monitor 5240 MHz (HT20)  
    array_prepare_for_picoscenes 4 "5240 HT20"

    # Monitor 5200-5210 MHz (VHT80)
    array_prepare_for_picoscenes 4 "5200 80 5210"
```
Then execute the following code to capture WiFi packets and measure CSI:


```python
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

recv_frame("4")
```

## 4.7. Transmitting WiFi Packets Using AX210/AX200 NICs
To transmit WiFi packets using the NIC, you first need to configure the channel and bandwidth through the command line. The specific steps are as follows:
1. First, use ​​array_status​​ to check the NIC's <PHYPath_ID> (e.g., assume it is 4);
2. Then execute the ​​array_prepare_for_picoscenes​​ <PHYPath_ID> <CHANNEL_CONFIG> command to configure the NIC. For example:
```bash
    array_prepare_for_picoscenes 4 "2412 HT20"
```
Where<PHYPath_ID> represents the NIC's identifier, and <CHANNEL_CONFIG> specifies the WiFi channel configuration. For detailed channel configuration references, see [here](https://ps.zpj.io/channels.html).

### 4.7.1. Transmitting WiFi Packets in 802.11a/g/n/ac/ax/be Formats
After completing NIC configuration, execute the following code to transmit WiFi packets in the TX_CBW_20_HT format.


```python
from PyPicoScenes import *
from buildFrames import *
import random
import time

def transmit_frame(nicName:str = '4', parameters=None):
    assert parameters, "parameters can't be None"
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
        txframe = buildBasicFrame(taskId, EchoProbePacketFrameType.SimpleInjectionFrameType, nic, parameters)
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

parameters = EchoProbeParameters()
transmit_frame("4", parameters)
```

### 4.7.2. Packet Injection with MCS Setting and Antenna Selection
PicoScenes allows users to specify the MCS (Modulation and Coding Scheme) value and Tx/Rx antenna selection for AX210/AX200 NICs. The following instructions demonstrate how to transmit WiFi packets using Antenna 2 with MCS 5 in TX_CBW_80_VHT_LDPC format. First configure the NIC's channel and bandwidth via the command line:
```bash
    array_prepare_for_picoscenes 4 "5520 80 5530"
```
Then execute the following code:


```python
from PyPicoScenes import *
from buildFrames import *
import random
import time

def transmit_frame(nicName:str = '4', parameters=None):
    assert parameters, "parameters can't be None"
    # Start PicoScenes platform
    picoscenes_start()
    # Get network interface card
    nic = getNic(nicName)

    ## Set txcm to 2
    nic.getTypedFrontEnd[MAC80211CSIExtractableFrontEnd]().setTxChainMask(2)
    
    ## Transmit packets in TX_CBW_80_VHT_LDPC format
    txParameters = nic.getUserSpecifiedTxParameters()
    txParameters.frameType = PacketFormatEnum.PacketFormat_VHT
    txParameters.guardInterval = GuardIntervalEnum.GI_800
    txParameters.cbw = ChannelBandwidthEnum.CBW_80
    txParameters.coding[0] = ChannelCodingEnum.LDPC
    
    ## Set MCS to 5
    txParameters.mcs[0] = 5
    
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
        txframe = buildBasicFrame(taskId, EchoProbePacketFrameType.SimpleInjectionFrameType, nic, parameters)
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

parameters = EchoProbeParameters()
transmit_frame("4", parameters)
```

### 4.7.3. Specifying Channel and Bandwidth in Real-time
PyPicoScenes provides APIs for real-time channel and bandwidth configuration of NICs without re-executing the array_prepare_for_picoscenes command. For example, assuming you have an AX210/AX200 NIC with ID <4> working at an 80 MHz CBW channel “5180 80 5210” (refer to Wi-Fi [Channelization](https://ps.zpj.io/channels.html) for details), executing the following code will dynamically switch it to the "5640 80 5610" channel configuration.


```python
from PyPicoScenes import *
from buildFrames import *
import random
import time

def transmit_frame(nicName:str = '4', parameters=None):
    # Start PicoScenes platform
    picoscenes_start()
    # Get network interface card
    nic = getNic(nicName)

    ## Reconfigure NIC's channel
    control = 5640e6
    rxcbw = 80e6
    freq = 5610e6
    nic.getFrontEnd().setChannelAndBandwidth(control, rxcbw, freq)
    
    ## Set txcm to 2
    nic.getTypedFrontEnd[MAC80211CSIExtractableFrontEnd]().setTxChainMask(2)
    
    ## Transmit packets in TX_CBW_160_HESU format
    txParameters = nic.getUserSpecifiedTxParameters()
    txParameters.frameType = PacketFormatEnum.PacketFormat_HESU
    txParameters.guardInterval = GuardIntervalEnum.GI_3200
    txParameters.cbw = ChannelBandwidthEnum.CBW_160
    txParameters.coding[0] = ChannelCodingEnum.LDPC
    
    ''' ## Transmit packets in TX_CBW_160_VHT format
    txParameters = nic.getUserSpecifiedTxParameters()
    txParameters.frameType = PacketFormatEnum.PacketFormat_VHT
    txParameters.guardInterval = GuardIntervalEnum.GI_800
    txParameters.cbw = ChannelBandwidthEnum.CBW_160
    txParameters.coding[0] = ChannelCodingEnum.BCC
    '''
    
    ## Set MCS to 5
    txParameters.mcs[0] = 5
    cppyy.gbl.setTxParameters(nic, txParameters)
    
    # Start NIC service
    nic.startTxService()

    cf_repeat = 1000
    tx_delay_us = 5e3

    for i in range(int(cf_repeat)):
        taskId = random.randint(9999, 65535)
        txframe = buildBasicFrame(taskId, EchoProbePacketFrameType.SimpleInjectionFrameType, nic, parameters)
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

parameters = EchoProbeParameters()
transmit_frame("4", parameters)
```

## 3.5. Important Notes
PyPicoScenes leverages `cppyy`'s dynamic binding technology to ​​efficiently encapsulate​​ PicoScenes' C++ APIs. Developers can directly invoke low-level APIs in Python scripts by including the relevant header files (e.g., `include("PicoScenes/SystemTools.hxx")`) and loading dynamic libraries (e.g., `load_library("libSystemTools")`), enabling core functionalities like `​​wireless signal transmission/reception​`​ and `​​CSI file parsing​`​. The Python APIs are ​​`identical`​​ to their native C++ counterparts, with usage details documented in the [PicoScenes Native API Reference](https://ps.zpj.io/api_docs/). Powered by cppyy's real-time parsing mechanism, Python can directly manipulate hardware control logic (e.g., configuring USRP sampling rates or WiFi channel parameters) while maintaining ​​strict behavioral consistency​​ with the C++ implementation. Developers must validate dynamic library paths and environmental dependencies during cross-platform deployments.
