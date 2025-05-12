import struct
import numpy as np
from PyPicoScenes.PyPicoScenes import *
import os

def parseCSIFile(filename: str = "", pos: int = 0, num: int = 0):
    res = []
    count = 0
    try:
        with open(filename, "rb") as f:
            # 获取文件总长度
            f.seek(0, os.SEEK_END)
            lens = f.tell()
            f.seek(0, os.SEEK_SET)
            if num == 0:
                num = lens - pos  # 读取剩余全部内容
            while pos < (lens - 4) and count < num:
                header = f.read(4)
                if len(header) < 4:
                    break
                # 解析字段长度（需根据实际字节序调整）
                field_len = struct.unpack("<I", header)[0] + 4 # 假设小端序
                # 回退指针并读取完整字段
                f.seek(-4, os.SEEK_CUR)

                data = f.read(field_len)
                if len(data) < field_len:
                    break

                frame = ModularPicoScenesRxFrame.fromBuffer(np.frombuffer(data, dtype=np.uint8), field_len, True)
                if frame:
                    res.append(frame)
                pos += field_len
                count += 1

    except Exception as e:
        print(f"Failed to parse csi file.: {e}")
        return []
    return res

if __name__ == "__main__":
    fileName = "rx_by_usrpN210.csi"
    res = parseCSIFile(fileName)
    print(res[0])
    pass