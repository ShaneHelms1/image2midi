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
        time.sleep(0.8)
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

    screenShot = PIL.ImageGrab.grab().save(outputDir + '/' + screenShotName%(frameIndex), 'PNG')
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