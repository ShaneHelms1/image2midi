'''
2022 © MaoHuPi
image2midi/video2fmv_sliceConvert.py
'''

import os
import sys
import math
import shutil

path = '.' if os.path.isfile('./'+os.path.basename(__file__)) else os.path.dirname(os.path.abspath(__file__))

inputFile = ''
workDir = path + '/video2fmv_sliceConvert'
outputfile = path + '/output.mp4'
sliceAction = 1
frameRate = 60
sliceLength = 60
level = 3

if level == 1:
    if os.path.isdir(workDir):
        shutil.rmtree(workDir)
    os.mkdir(workDir)
    os.system('ffmpeg -i "{inputFile}" -vf fps={frameRate} "{workDir}/frame_%d.png"'.format(inputFile = inputFile, workDir = workDir, frameRate = frameRate))
if level == 2:
    frameLength = len([name for name in os.listdir(workDir) if name.find('frame_') == 0])
    s = 1
    for i in range(0, math.ceil(frameLength/sliceLength)):
        # min(i+sliceLength, frameLength)
        os.system('ffmpeg -f image2 -start_number {start_number} -framerate {frameRate} -i "{inputPath}" -frames:v {sliceLength} -loop "0" "{videoPath}" -y'.format(start_number = i*sliceLength, sliceLength = sliceLength, videoPath = workDir + '/slice_%d.mp4'%(s), inputPath = os.path.abspath(workDir + '/frame_%d.png'), frameRate = frameRate))
        s += 1
if level == 3:
    sliceNames = sorted([name for name in os.listdir(workDir) if name.find('slice_') == 0], key = lambda name: int(name.replace('slice_', '').replace('.mp4', '')))
    sliceNum = len(sliceNames)
    for i in range(sliceAction-1, sliceNum):
        os.system('python "{path}/video2fmv.py" -i "{sliceName}" -o "{sliceName}done.mp4" -r {frameRate} -mode "gate" -y'.format(path = path, sliceName = workDir + '/' + sliceNames[i], frameRate = frameRate))
        print(i)