from PyPicoScenes.PyPicoScenes import *
from PyPicoScenes.buildFrames import *
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

if __name__ == "__main__":
    parameters = EchoProbeParameters()
    transmit_frame("4", parameters)