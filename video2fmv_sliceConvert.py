'''
2022 © MaoHuPi
image2midi/video2fmv_sliceConvert.py
'''

import os
import sys
import math
import time
import shutil
import keyboard
import pyautogui
import winsound
import threading

path = '.' if os.path.isfile('./'+os.path.basename(__file__)) else os.path.dirname(os.path.abspath(__file__))

inputFile = r""
workDir = path + '/video2fmv_sliceConvert'
outputFile = path + '/output.mp4'
sliceAction = -1
frameRate = 60
sliceLength = 60
level = 5
print(level)

doneList = []

try:
    if level == 1:
        if os.path.isdir(workDir):
            shutil.rmtree(workDir)
        os.mkdir(workDir)
        os.system('ffmpeg -i "{inputFile}" -vf fps={frameRate} "{workDir}/frame_%d.png"'.format(inputFile = inputFile, workDir = workDir, frameRate = frameRate))
    elif level == 2:
        frameLength = len([name for name in os.listdir(workDir) if name.find('frame_') == 0])
        s = 1
        for i in range(0, math.ceil(frameLength/sliceLength)):
            os.system('ffmpeg -f image2 -start_number {start_number} -framerate {frameRate} -i "{inputPath}" -frames:v {sliceLength} -loop "0" "{videoPath}" -y'.format(start_number = i*sliceLength, sliceLength = min(i+sliceLength, frameLength) - i, videoPath = workDir + '/slice_%d.mp4'%(s), inputPath = os.path.abspath(workDir + '/frame_%d.png'), frameRate = frameRate))
            s += 1
    elif level == 3:
        def video2fmv(i):
            os.system('python "{path}/video2fmv.py" -i "{sliceName}" -o "{outputPath}" -r {frameRate} -mode "gate" -y'.format(path = path, sliceName = workDir + '/' + sliceNames[i], outputPath = workDir + '/done_' + sliceNames[i], frameRate = frameRate))
            print(i)
        sliceNames = sorted([name for name in os.listdir(workDir) if name.find('slice_') == 0], key = lambda name: int(name.replace('slice_', '').replace('.mp4', '')))
        sliceNum = len(sliceNames)
        if sliceAction > 0:
            for i in range(sliceAction-1, sliceNum):
                video2fmv(i)
                doneList.append(sliceNames[i])
        elif sliceAction == -1:
            for i in range(0, sliceNum):
                if not os.path.isfile(workDir + '/done_' + sliceNames[i]):
                    video2fmv(i)
                    doneList.append(sliceNames[i])
        else:
            print('sliceAction must be \'-1\' or \'a positive number\'')
        # python video2fmv.py -i "video2fmv_sliceConvert/slice_3.mp4" -o "video2fmv_sliceConvert/done_slice_3.mp4" -y
    elif level == 4:
        doneNames = sorted([name for name in os.listdir(workDir) if name.find('done_slice_') == 0], key = lambda name: int(name.replace('done_slice_', '').replace('.mp4', '')))
        doneNames = list(map(lambda n: workDir + '/' + n, doneNames))
        textPath = path + '/merge_video.txt'
        textFile = open(textPath, 'w+', encoding = 'utf-8')
        textFile.write('\n'.join(list(map(lambda p: 'file \'%s\''%(p.replace('./', '')), doneNames))))
        textFile.close()
        os.system('ffmpeg -f concat -safe 0 -i "{textPath}" -c copy "{outputFile}" -y'.format(textPath = textPath, outputFile = outputFile))
    elif level == 5:
        os.system('ffmpeg -i "{inputFile}" -i "{outputFile}" -map 0:a -map 1:v -c copy "{outputFile}_audio.mp4" -y'.format(inputFile = inputFile, outputFile = outputFile))
    winsound.Beep(540, 100)
    winsound.Beep(440, 100)
except KeyboardInterrupt:
    winsound.Beep(540, 100)
    winsound.Beep(440, 100)
# except:
#     winsound.Beep(540, 50)
#     winsound.Beep(540, 50)
#     winsound.Beep(540, 100)
print(doneList)