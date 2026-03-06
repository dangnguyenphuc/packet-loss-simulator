import pandas as pd
import os
import shutil
import wave

data = []
leadFolder = "audio/"
# tmpFolder = "tmp/"
MIN_DURATION = 16

subFolders = os.listdir(leadFolder)
subFolders.sort()

def getAudioDuration(filePath: str) -> float:
    try:
        with wave.open(filePath, "rb") as wavFile:
            frames = wavFile.getnframes()
            rate = wavFile.getframerate()
            duration = frames / float(rate)
        return round(duration, 2)
    except:
        return -1

for subFolder in subFolders:

    # get main audio file inside subFolder
    speakerAudioFile = [f for f in os.listdir(leadFolder + subFolder) if f.startswith("speaker")]
    if len(speakerAudioFile) == 0:
        continue
    filePath = leadFolder + subFolder + "/" + speakerAudioFile[0]
    if (getAudioDuration(filePath) < MIN_DURATION): continue
    data.append(
        {"target_file": filePath}
    )
    
df = pd.DataFrame(data)
df.to_csv("input_file.csv", index=False)