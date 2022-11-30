'''
2022 © MaoHuPi
image2midi/video2flMidiVideo.py
'''

des = '''
video2fmv
by maohupi

arguments
-i: input file path(must be a jpeg file)
-o: output file path(will be a midi file)
-m: convert mode('gate' or 'edge')
-r: output video frame rate(must be an integer)
-y, -n: overwrite confirm(to overwrite or not)
-h: help(see all of the arguments)
'''

import os
import sys
import time
import shutil
import keyboard
import pyperclip
import threading
import PIL.ImageGrab

path = '.' if os.path.isfile('./'+os.path.basename(__file__)) else os.path.dirname(os.path.abspath(__file__))
def copyFile(fromPath, toPath):
    file = open(fromPath, 'rb')
    data = file.read()
    file.close()
    file = open(toPath, 'wb+')
    file.write(data)
    file.close()

''' correctPredict start '''
import cv2
import numpy as np
modelDir = path + '/correctPredictModel'
# def correctPredictFunction():
#     from keras.models import load_model
#     model = load_model(modelDir + '/keras_model.h5')
#     labels = open(modelDir + '/labels.txt', 'r').readlines()
#     def correctPredict(image):
#         image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
#         image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
#         image = (image / 127.5) - 1
#         probabilities = model.predict(image)
#         print(probabilities)
#         return(labels[np.argmax(probabilities)])
#     return(correctPredict)
def correctPredictFunction():
    def correctPredict(image):
        image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        errorColors = [
            {'color': [248, 154, 154], 'delta': 80, 'number': 100}, 
            {'color': [0, 104, 104], 'delta': 10, 'number': 100}, 
        ]
        dList = []
        for e in errorColors:
            errorNum = 0
            for r in image:
                for c in r:
                    d = False
                    for i in range(0, 3):
                        numberDelta = abs(c[i] - e['color'][i])
                        d = (d**2 + numberDelta**2)**0.5 if type(d) != bool or d != False else numberDelta
                    if d < e['delta']:
                        errorNum += 1
                    dList.append(d)
            if errorNum > e['number']:
                print('errorNum: %d, min: %d, color: %s'%(errorNum, int(min(*dList)), ','.join([str(n) for n in e['color']])))
                return('1 false')
        print('errorNum: %d, min: %d'%(errorNum, int(min(*dList))))
        return('0 true')
    return(correctPredict)
correctPredict = correctPredictFunction()
testPath = False
# testPath = "./modelTestImage/e5.png"
if type(testPath) == str:
    try:
        ssImage = cv2.imread(testPath)
        print(correctPredict(ssImage).lower().find('true') > -1)
    except KeyboardInterrupt: pass
    exit()
''' end '''

args = {}
argTypes = {
    'input': ['i', 'input', 'image', 'img'], 
    'output': ['o', 'output', 'midi', 'mid'], 
    'mode': ['m', 'mode', 'mod'], 
    'rate': ['r', 'rate', 'framerate'], 
    'start': ['s', 'start', 'startframe'], 
    'end': ['e', 'end', 'endframe'], 
    'length': ['l', 'length', 'framelength'], 
    'yes': ['y', 'yes', 'skip'], 
    'no': ['n', 'no', 'dontskip'], 
    'help': ['h', 'help', 'description', 'des']
}
for i in range(1, len(sys.argv)):
    key = sys.argv[i]
    value = sys.argv[i+1] if i+1 < len(sys.argv) else ''
    if key.find('-') == 0:
        key = key.replace('-', '').lower()
        for argType in argTypes:
            if key in argTypes[argType]:
                args[argType] = value

if 'help' in args:
    print(des)
if 'input' not in args:
    exit()

startFrame = int(args['start']) if 'start' in args else 1
endFrame = int(args['end']) if 'end' in args else False
frameLength = int(args['length']) if 'length' in args else False
frameRate = int(args['rate']) if 'rate' in args else 60
videoPath = path + '/video2fmv_input.mp4'
imageDir = path + '/video2fmv_input'
inputPath = args['input'] if 'input' in args else path + '/input.mp4'
outputDir = path + '/video2fmv_output'
screenShotName = '/screenShot_%d.png'
videoPathO = path + '/video2fmv_output.mp4'
outputPath = args['output'] if 'output' in args else path + '/output.mp4'

if os.path.isdir(imageDir):
    shutil.rmtree(imageDir)
if os.path.isdir(outputDir):
    shutil.rmtree(outputDir)

copyFile(inputPath, videoPath)
if not os.path.isdir(imageDir):
    os.mkdir(imageDir)
if not os.path.isdir(outputDir):
    os.mkdir(outputDir)
os.system('ffmpeg -i "{videoPath}" -vf fps={frameRate} "{imageDir}/%d.png"'.format(videoPath = videoPath, imageDir = imageDir, frameRate = frameRate))
os.unlink(videoPath)

imageNames = sorted(os.listdir(imageDir), key = lambda name: int(name.replace('.png', '')))
midiPaths = []
if endFrame == False:
    if frameLength != False:
        endFrame = startFrame + frameLength
    else:
        endFrame = len(imageNames)
if endFrame > len(imageNames):
    endFrame = len(imageNames)

for i in range(startFrame-1, endFrame):
    imageName = imageNames[i]
    imagePath = imageDir + '/' + imageName
    midiPath = outputDir + '/' + imageName + '.mid'
    os.system('python "{path}/main.py" -m gate -y -i "{imagePath}" -o "{midiPath}"'.format(path = path, imagePath = imagePath, midiPath = midiPath))
    midiPaths.append(midiPath)

frameIndex = 1
for midiPath in midiPaths:
    print(os.path.abspath(midiPath))
    fastMode = True
    screenShotPath = outputDir + '/' + screenShotName%(frameIndex)
    for _ in range(0, 10):
        if fastMode:
            keyboard.press_and_release('ctrl+m')
            time.sleep(0.3)
            keyboard.press_and_release('alt+n')
            time.sleep(0.1)
            keyboard.press_and_release('ctrl+a')
            pyperclip.copy(os.path.abspath(midiPath))
            keyboard.press_and_release('ctrl+v')
            time.sleep(0.1)
            keyboard.press_and_release('alt+o')
            time.sleep(0.5)
            keyboard.press_and_release('esc')
            time.sleep(0.2)
            keyboard.press_and_release('f7')
            time.sleep(1)
        else:
            def flOpen():
                os.system('"C:\Program Files\Image-Line\FL Studio 20\FL64.exe" {midiPath}'.format(midiPath = os.path.abspath(midiPath)))
            t = threading.Thread(target = flOpen)
            t.start()
            time.sleep(4)
            keyboard.press_and_release('n')
            time.sleep(0.5)
            keyboard.press_and_release('enter')
            time.sleep(2)
            keyboard.press_and_release('f7')
            time.sleep(0.5)
        screenShot = PIL.ImageGrab.grab().save(screenShotPath, 'PNG')
        ssImage = cv2.imread(screenShotPath)
        req = correctPredict(ssImage)
        if req and str(req).find('true') > -1:
            break
        else:
            print('time %d: %s'%(_, midiPath))
    frameIndex += 1
    # keyboard.wait('right')

os.system('ffmpeg -f image2 -framerate {frameRate} -i "{inputPath}" -loop "0" "{videoPath}" -y'.format(videoPath = videoPathO, inputPath = os.path.abspath(outputDir + '/' + screenShotName), frameRate = frameRate))
flag = True
if os.path.isfile(outputPath):
    if 'yes' in args:
        flag = True
    elif 'no' in args:
        flag = False
    else:
        flag = input('File \'{filePath}\' already exists. Overwrite? [y/N]'.format(filePath = outputPath))
        flag = not (flag.lower().find('n') > -1)
if flag:
    copyFile(videoPathO, outputPath)

shutil.rmtree(imageDir)
shutil.rmtree(outputDir)
os.unlink(videoPathO)