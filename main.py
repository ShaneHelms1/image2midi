'''
2022 © MaoHuPi
image2midi/main.py
'''

import os
import sys
import numpy
import cv2
import mido

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
    'yes': ['y', 'yes', 'skip'], 
    'no': ['n', 'no', 'dontskip']
}
for i in range(1, len(sys.argv)):
    key = sys.argv[i]
    value = sys.argv[i+1] if i+1 < len(sys.argv) else ''
    if key.find('-') == 0:
        key = key.replace('-', '').lower()
        for argType in argTypes:
            if key in argTypes[argType]:
                args[argType] = value

imagePath = path + '/image2midi_input.jpg'
inputPath = args['input'] if 'input' in args else path + '/input.jpg'
midiPath = path + '/image2midi_output.mid'
outputPath = args['output'] if 'output' in args else path + '/output.mid'
copyFile(inputPath, imagePath)
image = cv2.imread(imagePath)
# print(image)
row = 127
height, width, colorNum = image.shape
widthPerHeight = width/height

dots = [[image[r*int(height/row)][c*int(height/row)] for c in range(int(row*widthPerHeight))] for r in range(row)]
dotsImage = numpy.array(dots)
cv2.imshow('dotsImage', dotsImage)
cv2.waitKey(1)

if 'mode' in args:
    if args['mode'] in ['default', 'fill', 'gate']: pass
    elif args['mode'] in ['edge', 'laplacian']:
        dotsImage = cv2.cvtColor(dotsImage, cv2.COLOR_BGR2GRAY)
        dotsImage = cv2.medianBlur(dotsImage, 7)
        dotsImage = cv2.Laplacian(dotsImage, -1, 1, 5)
        cv2.imshow('dotsImageLaplacian', dotsImage)
        cv2.waitKey(1)

dots = [[(c if type(c) == int else sum(c)/3) > 255/2 for c in r] for r in dotsImage.tolist()]

def addNoteMsg(_type, note, length, track, velocity=1.0, channel=0):
    global bpm
    meta_time = 60 * 60 * 10 / bpm
    track.append(mido.Message('note_on' if _type else 'note_off', note=note, velocity=round(64*velocity), time=round(meta_time*length), channel=channel))

midi = mido.MidiFile()
track = mido.MidiTrack()
midi.tracks.append(track)
bpm = 240
# print(dots)
rMax = len(dots)
playing = {}
lastTime = 0
for c in range(len(dots[0])):
    first = True
    for r in range(len(dots)):
        if dots[r][c] != (playing[r] if r in playing else False):
            if dots[r][c]:
                addNoteMsg(True, rMax-r, length = 0.5*(c - lastTime), track = track)
                lastTime = c
                playing[r] = True
            else:
                addNoteMsg(False, rMax-r, length = 0.5*(c - lastTime) if first else 0, track = track)
                lastTime = c
                if first:
                    first = False
                playing[r] = False
first = True
for note in playing:
    if playing[note]:
        addNoteMsg(False, rMax-note, length = 0.5*(c - lastTime) if first else 0, track = track)
        lastTime = c
        if first:
            first = False
        playing[r] = False
midi.save(midiPath)
if os.path.isfile(outputPath):
    flag = False
    if 'yes' in args:
        flag = True
    elif 'no' in args:
        flag = False
    else:
        flag = input('File \'{filePath}\' already exists. Overwrite? [y/N]'.format(filePath = outputPath))
        flag = not (flag.lower().find('n') > -1)
    if flag:
        copyFile(midiPath, outputPath)

os.unlink(imagePath)
os.unlink(midiPath)
