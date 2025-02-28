from mat_file_to_dict import loadmat
import numpy as np
from scipy.io import savemat
import pprint

def input_data(file):
    data = loadmat(file)
    return data

def timeEventIndex(sigVal):
    # sigVal: The first column of the two-dimensional array signal is the time axis
    # Handling events that occur at repeated times
    # Returns the recurrence start and end time indices
    sigVal = np.array(sigVal)  # Ensure it's a NumPy array
    
    if sigVal.ndim == 1:
        time_array = sigVal
    else:
        time_array = sigVal[:, 0]  # Use the first column as the time axis

    startIndex = []
    endIndex = []

    i = 1
    while i < len(time_array):
        # Discovering time mutations
        if time_array[i] < time_array[i - 1]:  
            start_idx = i
            original_value = time_array[i - 1]  
            while i < len(time_array) and time_array[i] != original_value:
                i += 1
            if i < len(time_array):  
                end_idx = i
                startIndex.append(start_idx)
                endIndex.append(end_idx)
        i += 1  # Keep cycling
    return startIndex, endIndex

def reTimerepeated_can(startIndex, endIndex, sigName, sigVal):
    if startIndex:
        print(f"Signal: {sigName}")
        print(f"startIndex: {startIndex}")
        print(f"endIndex: {endIndex}")
        indices_to_delete = []
        for start, end in zip(startIndex, endIndex):
            indices_to_delete.extend(range(start, end))
        cleaned_sigVal = np.delete(sigVal, indices_to_delete, axis=0)
        return cleaned_sigVal
    return sigVal  # Return original if no indices to delete

def remove_rows_in_arrays(d, start, end):
    """ 递归遍历字典，删除 NumPy 2D+ 数组中 start 到 end 的行 """
    if not start or not end:  # 检查是否为空
        print(f"[Warning] Skipping key due to empty startIndex or endIndex: {d.keys()}")
        return  

    if isinstance(d, dict):
        for key, value in d.items():
            if isinstance(value, np.ndarray) and value.ndim >= 2:
                d[key] = np.delete(value, np.s_[start[0]-1:end[0]], axis=0)
            elif isinstance(value, dict):  
                remove_rows_in_arrays(value, start, end)

def ensure_2d(data):
    """ 数组转换为 2D 数组 """
    for key, value in data.items():
        if isinstance(value, np.ndarray):
            if value.ndim == 1:
                data[key] = value.reshape(-1, 1)  # 转换为 2D 数组，形状为 (n, 1)
        elif isinstance(value, dict):
            ensure_2d(value)  # 递归处理嵌套字典

def main(data):
    ensure_2d(data)
    for sigName, sigVal in data.items():
        if "mudp" not in sigName:
            # Handle can signals
            if not isinstance(sigVal, np.ndarray) or sigVal.shape[1] < 1:
                continue  # Skip non-array or insufficient column data
            startIndex, endIndex = timeEventIndex(sigVal)
            cleaned_sigVal = reTimerepeated_can(startIndex, endIndex, sigName, sigVal)
            data[sigName] = cleaned_sigVal  # Update the original data

        if "mudp" in sigName:
            # Handle mudp data
            if isinstance(data, dict) and "mudp" in data:
                mudp_data = data["mudp"]
                for name, value in mudp_data.items():
                    if not isinstance(value, dict):
                        print(f"Warning: {name} Stream not found from any sources!!")
                    elif "vis" in name:
                        # Get vis stream cTime
                        vis_cTime = value["header"]["cTime"]
                        startIndex, endIndex = timeEventIndex(vis_cTime)
                        remove_rows_in_arrays(value, startIndex, endIndex)
                    elif "fus" in name:
                        fus_cTime = value["header"]["cTime"]
                        startIndex, endIndex = timeEventIndex(fus_cTime)
                        remove_rows_in_arrays(value, startIndex, endIndex)
                    elif "VSE" in name:
                        vse_cTime = value["header"]["cTime"]
                        startIndex, endIndex = timeEventIndex(vse_cTime)
                        remove_rows_in_arrays(value, startIndex, endIndex)
                    elif "tsel" in name:
                        tsel_cTime = value["header"]["cTime"]
                        startIndex, endIndex = timeEventIndex(tsel_cTime)
                        remove_rows_in_arrays(value, startIndex, endIndex)
                    elif "vehCal" in name:
                        vehCal_cTime = value["header"]["cTime"]
                        startIndex, endIndex = timeEventIndex(vehCal_cTime)
                        remove_rows_in_arrays(value, startIndex, endIndex)
                    elif "SPP" in name:
                        SPP_cTime = value["header"]["cTime"]
                        startIndex, endIndex = timeEventIndex(SPP_cTime)
                        remove_rows_in_arrays(value, startIndex, endIndex)
                    elif "OTP" in name:
                        OTP_cTime = value["header"]["cTime"]
                        startIndex, endIndex = timeEventIndex(OTP_cTime)
                        remove_rows_in_arrays(value, startIndex, endIndex)
                    elif "eyeq" in name:
                        eyeq_cTime = value["AppDiag"]["header"]["cTime"]
                        startIndex, endIndex = timeEventIndex(eyeq_cTime)
                        remove_rows_in_arrays(value, startIndex, endIndex)

if __name__ == "__main__":
    file = "mat_file/matlab.mat"
    data = input_data(file)
    main(data)
    savemat("cleaned_matlab.mat", data,long_field_names=True)
