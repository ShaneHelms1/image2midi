'''
2022 © MaoHuPi
image2midi/video2flMidiVideo.py
'''

des = '''
video2midi
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

frameRate = int(args['rate']) if 'rate' in args else 60
videoPath = path + '/video2midi_input.mp4'
imageDir = path + '/video2midi_input'
inputPath = args['input'] if 'input' in args else path + '/input.mp4'
outputDir = path + '/video2midi_output'
screenShotName = '/screenShot_%d.png'
videoPathO = path + '/video2midi_output.mp4'
outputPath = args['output'] if 'output' in args else path + '/output.mp4'
copyFile(inputPath, videoPath)
if not os.path.isdir(imageDir):
    os.mkdir(imageDir)
if not os.path.isdir(outputDir):
    os.mkdir(outputDir)
os.system('ffmpeg -i "{videoPath}" -vf fps={frameRate} "{imageDir}/%d.png"'.format(videoPath = videoPath, imageDir = imageDir, frameRate = frameRate))
os.unlink(videoPath)

imageNames = sorted(os.listdir(imageDir), key = lambda name: int(name.replace('.png', '')))
midiPaths = []
for imageName in imageNames:
    imagePath = imageDir + '/' + imageName
    midiPath = outputDir + '/' + imageName + '.mid'
    os.system('python "{path}/main.py" -m gate -y -i "{imagePath}" -o "{midiPath}"'.format(path = path, imagePath = imagePath, midiPath = midiPath))
    midiPaths.append(midiPath)

frameIndex = 60
for midiPath in midiPaths:
    print(os.path.abspath(midiPath))
    def flOpen():
        os.system('"C:\Program Files\Image-Line\FL Studio 20\FL64.exe" {midiPath}'.format(midiPath = os.path.abspath(midiPath)))
    t = threading.Thread(target = flOpen)
    t.start()

    time.sleep(2)
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
shutil.rmtree(videoPathO)