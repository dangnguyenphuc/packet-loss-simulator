import os
import shutil
import soundfile as sf
import pandas as pd
from plc_mos import PLCMOSEstimator
import wave
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

PACKET_LOSS_TOOL_DIR = "/home/dangnp/workspace/tools/loss-simulator/PLCMOS/audio"
AUDIO_RECORDING_DIR = "./audio"
REFORMATTED_DIR = "./score"

MIN_AUDIO_DURATION = 20
MAX_AUDIO_DURATION_OFFSET = 2
AUDIO_FILE_NAME = [
                    "plc", 
                    "normal", 
                   "plc-opus_1.5"
                   ]
AUDIO_FILE_TYPE = ".wav"
EVAL_COMPLEXITY = [6,7,8,9,10]
EVAL_DEC_COMPLEXITY = [5,6,7,8,9,10]
EVAL_DRED = [0, 30, 50, 70, 85, 100]

SCORE_OUTPUT_FILE_NAME = "output.xlsx"
TMP_SCORE_OUTPUT_FILE_NAME = "tmp.xlsx"
processedTestcases = {}

def getAudioDuration(filePath: str) -> float:
        try:
            with wave.open(filePath, "rb") as wavFile:
                frames = wavFile.getnframes()
                rate = wavFile.getframerate()
                duration = frames / float(rate)
            return round(duration, 2)
        except:
            return -1

# processLock = Lock()

# def processAudioDirectory(dir, audioFolder, generatedFolderName, minAudioDuration, offset):
#     dirPath = os.path.join(audioFolder, dir)

#     targetFiles = [
#         f for f in os.listdir(dirPath)
#         if f.startswith("speak") and f.endswith(".wav")
#     ]

#     for audio in targetFiles.copy():
#         audioFilePath = os.path.join(dirPath, audio)
#         if getAudioDuration(audioFilePath) < minAudioDuration - offset:
#             targetFiles.remove(audio)

#     if len(targetFiles) <= 0:
#         return

#     params = dir.split("_")
#     curCom = params[0].lower()
#     curDecCom = params[1].lower()
#     curDred = params[3].lower()
#     curNetworkType = params[4].lower()
#     curNetworkLoss = params[5].lower()

#     curPath = os.path.join(
#         generatedFolderName,
#         curNetworkType,
#         curCom,
#         curDecCom,
#         curNetworkLoss,
#         curDred
#     )

#     os.makedirs(curPath, exist_ok=True)
#     curAudioPath = os.path.join(curPath, "audio.wav")

#     with processLock:
#         if curPath in processedTestcases:
#             print(f"Duplicate: {curPath}")
#             cpuCount = len([f for f in os.listdir(curPath) if f.startswith("cpu")])
#             memCount = len([f for f in os.listdir(curPath) if f.startswith("mem")])
#             shutil.copy2(os.path.join(dirPath, "cpu.txt"), os.path.join(curPath, f"cpu{cpuCount}.txt"))
#             shutil.copy2(os.path.join(dirPath, "mem.txt"), os.path.join(curPath, f"mem{memCount}.txt"))
#             return

#         shutil.copy2(os.path.join(dirPath, targetFiles[0]), curAudioPath)
#         shutil.copy2(os.path.join(dirPath, "cpu.txt"), os.path.join(curPath, "cpu0.txt"))
#         shutil.copy2(os.path.join(dirPath, "mem.txt"), os.path.join(curPath, "mem0.txt"))
#         processedTestcases[curPath] = dir

# def reformatAudioFolderDred(audioFolder, generatedFolderName, minAudioDuration=MIN_AUDIO_DURATION, offset=MAX_AUDIO_DURATION_OFFSET):
#     os.makedirs(generatedFolderName, exist_ok=True)
#     subDirectories = os.listdir(audioFolder)
    
#     with ThreadPoolExecutor(max_workers=8) as executor:
#         futures = [
#             executor.submit(processAudioDirectory, dir, audioFolder, generatedFolderName, minAudioDuration, offset)
#             for dir in subDirectories
#         ]
#         for future in futures:
#             future.result()

# processedTestcases = {}
# reformatAudioFolderDred("audio", "dred")

excel_lock = Lock()

def process_dred_condition(args):
    """Process a single dred condition and return results"""
    sourceDir, networkType, enc, dec, loss, dred, targetAudioFile = args
    filePath = os.path.join(sourceDir, networkType, enc, dec, loss, dred, targetAudioFile)
    
    if not os.path.exists(filePath):
        return None
    
    try:
        plcmos = PLCMOSEstimator()
        data, sr = sf.read(filePath)
        mos = plcmos.run(data, sr)
        print(filePath, mos)
        return (f"{enc}_{dec}_{loss}", dred, mos)
    except Exception as e:
        print(f"Error: {filePath} -> {e}")
        return None

def scoringDred(
    sourceDir="dred",
    targetAudioFile="audio.wav",
    outputFile=SCORE_OUTPUT_FILE_NAME
):
    plcmos = PLCMOSEstimator()
    networkTypeDirs = sorted(os.listdir(sourceDir))

    for networkType in networkTypeDirs:
        table = {}
        networkPath = os.path.join(sourceDir, networkType)
        
        # Prepare all tasks
        tasks = []
        encDirs = sorted(os.listdir(networkPath), key=lambda x: int(x.split("-")[-1]))
        
        for enc in encDirs:
            encPath = os.path.join(networkPath, enc)
            decDirs = sorted(os.listdir(encPath), key=lambda x: int(x.split("-")[-1]))
            
            for dec in decDirs:
                decPath = os.path.join(encPath, dec)
                lossDirs = sorted(os.listdir(decPath), key=lambda x: int(x.split("-")[-1]))
                
                for loss in lossDirs:
                    lossPath = os.path.join(decPath, loss)
                    dredDirs = sorted(os.listdir(lossPath), key=lambda x: int(x.split("-")[-1]))
                    
                    for dred in dredDirs:
                        tasks.append((sourceDir, networkType, enc, dec, loss, dred, targetAudioFile))
        
        # Process with multithreading
        with ThreadPoolExecutor(max_workers=4) as executor:
            results = executor.map(process_dred_condition, tasks)
            
            for result in results:
                if result:
                    row_key, dred, mos = result
                    if row_key not in table:
                        table[row_key] = {}
                    table[row_key][dred] = mos
        
        # Write to Excel (single-threaded with lock)
        if table:
            df = pd.DataFrame.from_dict(table, orient="index")
            df = df.reindex(sorted(df.columns, key=lambda x: int(x.split("-")[-1])), axis=1)
            df.index.name = "Condition"
            
            with excel_lock:
                if os.path.exists(outputFile):
                    with pd.ExcelWriter(outputFile, mode="a", engine="openpyxl", if_sheet_exists="replace") as writer:
                        df.to_excel(writer, sheet_name=networkType)
                else:
                    with pd.ExcelWriter(outputFile, mode="w", engine="openpyxl") as writer:
                        df.to_excel(writer, sheet_name=networkType)

scoringDred()
