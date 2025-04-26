



# import the time standard module
import time

# import the pygame module
import pygame

from threading import Thread
import json

# for choosing between cdrc and the pumpkin head via the command line
import sys

# for the jaw
#import alsaaudio, audioop

# for logarithmic function
import math

# for random pumpkin head movement!
import random
import datetime

serialEnabled = sys.argv[2] == "pumpkin"
if serialEnabled:
    print ("serial is enabled!!1")
    import serial

from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer
PORT_NUMBER = 8082



## CDRC SETUP ##
# screen
# sudo /usr/local/bin/fcserver
# (exit screen)
# cd cdrc
# python pumpkinhead.py cdrcsequences.txt cdrc

## PUMPKIN SETUP ##
# cd pumpkinhead
# python pump*py pump*txt pumpkin



class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'



for arg in sys.argv:
    print (arg)


masterPixelMultiplier = 0.125
masterPixelColor      = [255, 255, 255]
cdrc_emotion       = 64
cdrc_jaw           = 0
cdrc_awakeAsleep   = 0
cdrc_eyesLeftRight = 0
cdrc_eyelids       = 0
cdrc_emotionMask   = [1 for x in range(0, 32)]
cdrc_eyelidMask    = [1 for x in range(0, 32)]
cdrc_pupilMask     = [1 for x in range(0, 32)]


def resetCdrcPixels():
    global masterPixelMultiplier, masterPixelColor, cdrc_emotion, cdrc_jaw, cdrc_awakeAsleep, cdrc_eyesLeftRight, cdrc_eyelids, cdrc_emotionMask, cdrc_eyelidMask, cdrc_pupilMask
    #masterPixelMultiplier = 0.125
    print ("resetting pixels")
    masterPixelColor      = [255, 255, 255]
    cdrc_emotion       = 64
    cdrc_jaw           = 0
    cdrc_awakeAsleep   = 0
    cdrc_eyesLeftRight = 0
    cdrc_eyelids       = 0
    cdrc_emotionMask   = [1 for x in range(0, 32)]
    cdrc_eyelidMask    = [1 for x in range(0, 32)]
    cdrc_pupilMask     = [1 for x in range(0, 32)]


robotMode = sys.argv[2]  # choose between micro maestro or fadecandy mode
print ("ROBOT MODE IS: " + robotMode)
if robotMode == "cdrc":
    import opc

    numLEDs = 40
    client = opc.Client('localhost:7890')



soundstart = time.time()
#with open('cdrcsequences.txt', 'r') as the_file:
with open(sys.argv[1], 'r') as the_file:
    print ("opening sequence file: " + sys.argv[1])
    sequenceConstant = json.load(the_file)

sequence = {}
sequenceRunning = False
sequenceThatIsCurrentlyRunning = "none"

sounds = {}
def loadSounds():
    global sounds, sequenceConstant
    for soundKey, sound in sequenceConstant.iteritems():
        #print ("sound for " + soundKey + ": " + sound['audio'])
        try:
            sounds[soundKey] = pygame.mixer.Sound(sound['audio'])
        except:
            print ("unable to load sound for " + soundKey + " (" + sound['audio'] + ")")
        else:
            print ("loaded sound for " + soundKey + ": " + sound['audio'])
    #print (sounds)


def playsound(_sound):
    print ("playsound(" + str(_sound) + ")")
    global sounds, sequenceConstant
    print ("playing sound")

    pygame.mixer.stop()

    channel = sounds[_sound].play()


def playSequence(_sequence):
    print ("playSequence")
    global robotMode, sequenceRunning, sequenceConstant, soundstart, sequence, cdrc_emotion, cdrc_jaw, cdrc_awakeAsleep, cdrc_emotionMask, cdrc_eyelidMask, cdrc_pupilMask, sequenceThatIsCurrentlyRunning
    
    try:
        sequence = sequenceConstant[_sequence]['sequence'][:] # Make a copy!
    except Exception as inst:
        print (bcolors.FAIL)
        print ("couldn't play sequence \"" + str(_sequence) + "\" (" + str(type(_sequence)) + ")")
        print (type(inst))     # the exception instance
        print (inst.args)      # arguments stored in .args
        print (inst)           # __str__ allows args to printed directly
        print (bcolors.ENDC)
        return

    # sequence = sequenceConstant['sequence1']['sequence']
    soundstart = time.time()
    #print ("this is happening")
    sequenceRunning = True
    sequenceThatIsCurrentlyRunning = _sequence
    # sendSomething(robotMode + " playing sequence " + str(_sequence) + "\n")
    if robotMode == "pumpkin":
        print ("*** sequence: " + str(_sequence) + " ***")
        if _sequence == "7":
            #print ("it equals 7")
            servos.moveServo(0, 60)  # hack for the video
            servos.moveServo(1, 90)
        else:
            servos.moveServo(0, 90)
            servos.moveServo(1, 90) # make the pumpkin look dead center when a sequence starts
    elif robotMode == "cdrc":
        resetCdrcPixels()

    playsound(_sequence)



def allPixelsFull():
    print ("all pixels full")
    pixels = [ (255, 255, 255) ] * 40
    client.put_pixels(pixels)

if robotMode == "cdrc":
    allPixelsFull()





def sequenceLoop():
    global robotMode, masterPixelColor, masterPixelMultiplier, cdrc_emotion, cdrc_jaw, cdrc_awakeAsleep, cdrc_emotionMask, cdrc_eyelidMask, cdrc_pupilMask, cdrc_eyesLeftRight, cdrc_eyelids
    print ("begin sequence loop")
    nextMovement = datetime.datetime.now() + datetime.timedelta(seconds=3)
    global soundstart, sequence, sequenceRunning
    while 1:
        #time.sleep(0.01)
        if sequenceRunning:
            #print ("sequenceRunning: " + str(sequenceRunning))
            if len(sequence) > 0:
                thisTime = time.time() - soundstart + 0.1  # the extra 0.1 is to sync up the audio with the animation
                #print (thisTime)
                #animationFramesThisPlaybackFrame = 0
                for entryIndex, entry in enumerate(sequence):
                #for entryKey in sequence.keys():
                    #entry = sequence[entryKey]
                    if thisTime > entry['time'] and thisTime < entry['time'] + 0.2:  # if it falls more than 0.2 seconds behind, skip it; we can afford to skip frames
                        #animationFramesThisPlaybackFrame += 1
                        print ("****")
                        print ("time: " + str(thisTime))
                        print ("time in file: " + str(entry['time']))

                        #print (entry)
                        if serialEnabled and robotMode == "pumpkin":
                            if 'jaw' in entry:
                                #jaw = pow(max(entry['jaw'] - 16, 0), 3) / 200
                                #jaw = max(entry['jaw'] - 24, 0) * 3
                                jaw = entry['jaw'] * 1.3
                                servos.moveServo(2, jaw)
                                #print (jaw)

                            if 'pan' in entry:
                                servos.moveServo(0, entry['pan'])
                                print ("pan: " + str(entry['pan']))

                            if 'tilt' in entry:
                                tilt = entry['tilt']
                                tilt = tilt - 10
                                if tilt > 105:
                                    tilt = 105
                                servos.moveServo(1, tilt)
                                print ("tilt: " + str(tilt))
                        elif robotMode == "cdrc":
                            pixels = range(40)

                            if 'jaw' in entry:
                                cdrc_jaw = entry['jaw']
                                print ("cdrc_jaw: " + str(cdrc_jaw))

                            if 'awakeAsleep' in entry:
                                cdrc_awakeAsleep = entry['awakeAsleep']
                                print ("cdrc_awakeAsleep: " + str(cdrc_awakeAsleep))

                                if cdrc_awakeAsleep == 127:
                                    masterPixelMultiplier = 0.5
                                elif cdrc_awakeAsleep == 0:
                                    masterPixelMultiplier = 0.125

                            if 'emotion' in entry:
                                cdrc_emotion = entry['emotion']
                                print ("cdrc_emotion: " + str(cdrc_emotion))

                                if cdrc_emotion < 57:  # sad
                                    notblue = cdrc_emotion * 4
                                    masterPixelColor = (notblue, notblue, 255)
                                elif cdrc_emotion > 71:  # angry
                                    notred = 255 - ((cdrc_emotion - 64) * 4)
                                    masterPixelColor = (255, notred, notred)
                                else:  # deadband neutral
                                    masterPixelColor = (255, 255, 255)

                                # and now the eyes
                                emotionIndex = cdrc_emotion / (128 / 19)
                                if emotionIndex == 0:
                                    cdrc_emotionMask = (0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0)
                                elif emotionIndex == 1:
                                    cdrc_emotionMask = (0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0)
                                elif emotionIndex == 2:
                                    cdrc_emotionMask = (0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0)
                                elif emotionIndex == 3:
                                    cdrc_emotionMask = (0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0)
                                elif emotionIndex == 4:
                                    cdrc_emotionMask = (0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0)
                                elif emotionIndex == 5:
                                    cdrc_emotionMask = (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0)
                                elif emotionIndex >= 6 and emotionIndex <= 9:
                                    cdrc_emotionMask = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
                                elif emotionIndex == 12:
                                    cdrc_emotionMask = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
                                elif emotionIndex == 13:
                                    cdrc_emotionMask = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
                                elif emotionIndex == 14:
                                    cdrc_emotionMask = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
                                elif emotionIndex == 15:
                                    cdrc_emotionMask = (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
                                elif emotionIndex == 16:
                                    cdrc_emotionMask = (0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0)
                                elif emotionIndex >= 17:
                                    cdrc_emotionMask = (0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0)

                                print ("emotion index: " + str(emotionIndex))

                            if 'eyesLeftRight' in entry:
                                cdrc_eyesLeftRight = entry['eyesLeftRight']
                                print ("cdrc_eyesLeftRight: " + str(cdrc_eyesLeftRight))

                                pupilIndex = cdrc_eyesLeftRight / (8192 / 4)
                                print (pupilIndex)
                                if pupilIndex == -4:
                                    cdrc_pupilMask = (1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0)
                                elif pupilIndex == -3:
                                    cdrc_pupilMask = (1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1)
                                elif pupilIndex == -2:
                                    cdrc_pupilMask = (1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1)
                                elif pupilIndex == -1:
                                    cdrc_pupilMask = (1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1)
                                elif pupilIndex == 0:
                                    cdrc_pupilMask = (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)
                                elif pupilIndex == 1:
                                    cdrc_pupilMask = (1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1)
                                elif pupilIndex == 2:
                                    cdrc_pupilMask = (1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1)
                                elif pupilIndex == 3:
                                    cdrc_pupilMask = (1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1)
                                elif pupilIndex == 4:
                                    cdrc_pupilMask = (0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1)

                                print ("pupil index: " + str(pupilIndex))

                            drawEyes = False
                            if 'eyesUp' in entry:
                                cdrc_eyelids = -entry['eyesUp']
                                print ("cdrc_eyelids: " + str(cdrc_eyelids))
                                drawEyes = True

                            if 'eyesDown' in entry:
                                cdrc_eyelids = entry['eyesDown']
                                # print ("cdrc_eyelids: " + str(cdrc_eyelids))
                                drawEyes = True

                            if drawEyes == True:
                                eyelidIndex = cdrc_eyelids / (128 / 4)

                                if eyelidIndex == -8:
                                    cdrc_eyelidMask = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
                                elif eyelidIndex == -7:
                                    cdrc_eyelidMask = (0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0)
                                elif eyelidIndex == -6:
                                    cdrc_eyelidMask = (0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0)
                                elif eyelidIndex == -5:
                                    cdrc_eyelidMask = (0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0)
                                elif eyelidIndex == -4:
                                    cdrc_eyelidMask = (0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0)
                                elif eyelidIndex == -3:
                                    cdrc_eyelidMask = (0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0)
                                elif eyelidIndex == -2:
                                    cdrc_eyelidMask = (0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0)
                                elif eyelidIndex == -1:
                                    cdrc_eyelidMask = (0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0)
                                elif eyelidIndex == 0:
                                    cdrc_eyelidMask = (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1)
                                elif eyelidIndex == 1:
                                    cdrc_eyelidMask = (1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1)
                                elif eyelidIndex == 2:
                                    cdrc_eyelidMask = (1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1)
                                elif eyelidIndex == 3:
                                    cdrc_eyelidMask = (1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1)
                                elif eyelidIndex == 4:
                                    cdrc_eyelidMask = (1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1)
                                elif eyelidIndex == 5:
                                    cdrc_eyelidMask = (1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1)
                                elif eyelidIndex == 5:
                                    cdrc_eyelidMask = (1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1)
                                elif eyelidIndex == 6:
                                    cdrc_eyelidMask = (1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1)
                                elif eyelidIndex == 7:
                                    cdrc_eyelidMask = (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)

                                print ("eyelid index: " + str(eyelidIndex))
                                # print (cdrc_eyelidMask)


                                # if cdrc_eyesLeftRight < 200:
                                #     for i in range(0, 8):  # the part that's always on
                                #         cdrc_pupilMask[i] = 1
                                #         cdrc_pupilMask[i + 16] = 1

                                #     for i in range(0, pupilIndex):
                                #         cdrc_pupilMask[8 + i] = 1
                                #         cdrc_pupilMask[15 - i] = 1
                                #         cdrc_pupilMask[24 + i] = 1
                                #         cdrc_pupilMask[31 - i] = 1
                                # elif cdrc_eyesLeftRight > 200:
                                #     for i in range(0, 8):
                                #         cdrc_pupilMask[8 + i] = 1
                                #         cdrc_pupilMask[24 + i] = 1

                                #     for i in range(0, pupilIndex):
                                #         cdrc_pupilMask[i] = 1
                                #         cdrc_pupilMask[7 - i] = 1
                                #         cdrc_pupilMask[16 + i] = 1
                                #         cdrc_pupilMask[23 - i] = 1
                                # else:
                                #     for i in range(0, 32):
                                #         cdrc_pupilMask[i] = 1

                                #print (cdrc_pupilMask)



                                # if cdrc_eyesLeftRight < 60:
                                #     pupilIndex = cdrc_eyesLeftRight / 8
                                #     print (pupilIndex)
                                #     for i in range(0, pupilIndex):
                                #         cdrc_pupilMask[7 - i]  = 1
                                #         cdrc_pupilMask[8 + i]  = 1
                                #         cdrc_pupilMask[23 - i] = 1
                                #         cdrc_pupilMask[24 + i] = 1
                                # elif cdrc_eyesLeftRight > 68:
                                #     pupilIndex = (cdrc_eyesLeftRight / 8) - 64
                                #     print (pupilIndex)
                                #     for i in range(0, pupilIndex):
                                #         cdrc_pupilMask[0 + i]  = 1
                                #         cdrc_pupilMask[15 - i] = 1
                                #         cdrc_pupilMask[16 + i] = 1
                                #         cdrc_pupilMask[31 - i] = 1
                                # else:
                                #     for i in range(0, 32):
                                #         cdrc_pupilMask[i] = 1


                            # and now it is time to draw
                            # calculate the colors
                            resultingColor = (masterPixelColor[0] * masterPixelMultiplier,
                                masterPixelColor[1] * masterPixelMultiplier,
                                masterPixelColor[2] * masterPixelMultiplier)

                            # eyes
                            for i in range(0, 32):
                                pixels[i] = (resultingColor[0] * cdrc_emotionMask[i] * cdrc_pupilMask[i] * cdrc_eyelidMask[i],
                                    resultingColor[1] * cdrc_emotionMask[i] * cdrc_pupilMask[i] * cdrc_eyelidMask[i],
                                    resultingColor[2] * cdrc_emotionMask[i] * cdrc_pupilMask[i] * cdrc_eyelidMask[i])

                            # mouth
                            mouth1 = (0, 0, 0)
                            mouth2 = (0, 0, 0)
                            mouth3 = (0, 0, 0)
                            mouth4 = (0, 0, 0)


                            #print ("resulting color: " + str(resultingColor) + "(" + str(type(resultingColor)) + ")")

                            #if jaw > 5:
                            if cdrc_jaw > 1000:
                                mouth1 = resultingColor

                            #if jaw > 15: 
                            if cdrc_jaw > 2000:
                                mouth2 = resultingColor

                            #if jaw > 22:
                            if cdrc_jaw > 4000:
                                mouth3 = resultingColor

                            #ifcdrc_ jaw > 36:
                            if cdrc_jaw > 6000:
                                mouth4 = resultingColor

                            pixels[32] = mouth4
                            pixels[33] = mouth3
                            pixels[34] = mouth2
                            pixels[35] = mouth1
                            pixels[36] = mouth1
                            pixels[37] = mouth2
                            pixels[38] = mouth3
                            pixels[39] = mouth4

                            client.put_pixels(pixels)



                        try:
                            del sequence[entryIndex]  # delete the entry from the list so we can be more efficient as the clip progresses??
                        except Exception as inst:
                            print (bcolors.FAIL)
                            print ("Error deleting old sequence!")
                            print (type(inst))     # the exception instance)
                            print (inst.args)      # arguments stored in .args)
                            print (inst)           # __str__ allows args to printed directly)
                            print (bcolors.ENDC)
                            stopSequence()
                            #return

                        break  #I'm gonna try doing this to kill the flickering
                    # else:
                    #     print ("****")
                    #     print ("skipping " + str(entry['time']))
                #time.sleep(0.02)
                #print ("animation frames this playback frame: " + str(animationFramesThisPlaybackFrame))
            else:
                #print ("sequence length is less than zero")
                #print (sequence)
                stopSequence()
                # sequenceRunning = False
                # sendSomething(robotMode + " sequence finished\n")
                # if robotMode == "cdrc":  # dim the lights
                #     pixels = [ (32, 32, 32) ] * 40
                #     client.put_pixels(pixels)
        else:  # random head movement
            if robotMode == "pumpkin":
                if datetime.datetime.now() > nextMovement:
                    print ("time for random motion")
                    nextMovement = datetime.datetime.now() + datetime.timedelta(seconds=random.randrange(3, 8))
                    servos.moveServo(0, random.randrange(85, 95))
                    servos.moveServo(1, random.randrange(85, 95))



def stopSequence():
    global sequenceRunning, robotMode, sequenceThatIsCurrentlyRunning
    sequenceThatIsCurrentlyRunning = "none"
    sequenceRunning = False
    # sendSomething(robotMode + " sequence finished\n")
    if robotMode == "cdrc":  # dim the lights
        pixels = [ (32, 32, 32) ] * 40
        client.put_pixels(pixels)
    elif robotMode == "pumpkin":
        servos.moveServo(2, 0)  # close that mouth




class ServoController:
    def __init__(self, controllerPort):
        self.serialCon = serial.Serial(controllerPort, baudrate=9600)

    def moveServo(self, channel, target):
        if channel == 1 and target > 113:
            target = 113
            print (target)
        target = (self.map(target, 0, 180, 656, 2500) * 4) #Map the target angle to the corresponding PWM pulse.

        commandByte = chr(0x84)
        channelByte = chr(channel)
        lowTargetByte = chr(int(target) & 0x7F)
        highTargetByte = chr((int(target) >> 7) & 0x7F)

        command = commandByte + channelByte + lowTargetByte + highTargetByte
        self.serialCon.write(command)
        self.serialCon.flush()

        return target

    def map (self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

if robotMode == "pumpkin":
    print ("initializing servo controller")

    servos = ServoController('/dev/ttyACM0')
    servos.moveServo(0, 90)
    servos.moveServo(1, 90)
    servos.moveServo(2, 0)



serialPerSecond = 0
serialWrites    = 0

# if serialEnabled:
#     interface = localserver()

# start pygame
pygame.mixer.pre_init(frequency=48000, buffer=1024, channels=2)
pygame.mixer.init()

loadSounds()



# def parseIncoming(_incoming):
#     commandIsForUs = False
#     global sequenceConstant
    
#     if _incoming.find('playsequence') != -1:
#         parsePlaySequence(_incoming)
#         commandIsForUs = True

#     if _incoming.find('printSequences') != -1:
#         print (sequenceConstant)
#         commandIsForUs = True

#     if _incoming.find('stopaudio') != -1:
#         pygame.mixer.stop()
#         stopSequence()
#         commandIsForUs = True

#     if _incoming.find('ping') != -1:
#         # sendSomething("pong\n")
#         commandIsForUs = True

#     if _incoming.find('resetpixels') != -1:
#         resetCdrcPixels()
#         commandIsForUs = True

#     if _incoming.find('allpixelsfull') != -1:
#         allPixelsFull()
#         commandIsForUs = True

#     if commandIsForUs == True:
#         print (bcolors.OKGREEN + time.strftime("%Y-%m-%d %H:%I:%S") + " received: " + _incoming + bcolors.ENDC)
#     else:
#         print (bcolors.OKBLUE + "received: " + _incoming + bcolors.ENDC)



def requestHandler_index(_get):
    return "text/plain", "commands:\n\nplaysequence/x\nstopaudio\nping"

def requestHandler_playsequence(_get):
    print ("playsequence function activated woo")
    print (_get)
    playSequence(_get[2])
    return "text/plain", "playing sequence " + _get[2]


def requestHandler_stopaudio(_get):
    pygame.mixer.stop()
    stopSequence()
    commandIsForUs = True
    return "text/plain", "stopping audio"

def requestHandler_ping(_get):
    return "text/plain", "pong"

def requestHandler_getaudiostate(_get):
    global sequenceThatIsCurrentlyRunning
    return "text/plain", str(sequenceThatIsCurrentlyRunning)



httpRequests = {'playsequence'      : requestHandler_playsequence,
                'stopaudio'       : requestHandler_stopaudio,
                'ping'       : requestHandler_ping,
                'getaudiostate': requestHandler_getaudiostate,
                }

#This class will handles any incoming request from
#the browser 
class myHandler(BaseHTTPRequestHandler):
    
    #Handler for the GET requests
    def do_GET(self):
        elements = self.path.split('/')

        responseFound = False
        for httpRequest, httpHandler in httpRequests.iteritems():
            if elements[1].find(httpRequest) == 0: # in other words, if the first part matches
                contentType, response = httpHandler(elements)
                responseFound = True

                self.send_response(200)
                self.send_header("Access-Control-Allow-Origin", "*")
                self.send_header('Content-type', contentType)
                self.end_headers()

                self.wfile.write(response)
        if not responseFound:
            contentType, response = requestHandler_index('/')

            self.send_response(200)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header('Content-type', contentType)
            self.end_headers()

            self.wfile.write(response)
            
        return



print ("hello.")


sequenceLoopThread = Thread(target=sequenceLoop)
sequenceLoopThread.daemon = True
sequenceLoopThread.start()

while 1:
    server = HTTPServer(('', PORT_NUMBER), myHandler)
    print ('Started httpserver on port ' , PORT_NUMBER)

    server.serve_forever()
