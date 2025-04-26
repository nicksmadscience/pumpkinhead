# example1.py
# play a sound to the left, to the right and to the center

serialEnabled = True

# import the time standard module
import time

# import the pygame module
import pygame

import asyncore
import socket
from threading import Thread
if serialEnabled: import serial
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








#if serialEnabled:
#    pumpkincontroller = serial.Serial("/dev/ttyUSB0", baudrate=115200)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'


#print sys.argv[1]

for arg in sys.argv:
    print arg


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
    print "resetting pixels"
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
print "ROBOT MODE IS: " + robotMode
if robotMode == "cdrc":
    import opc

    numLEDs = 40
    client = opc.Client('localhost:7890')

    # pixels = [ (0,0,0) ] * 40
    # for i in range(0, 40):
    #     pixels[i] = (64, 64, 64)
    # client.put_pixels(pixels)

    # while True:
    #         for i in range(numLEDs):
    #                 pixels = [ (0,0,0) ] * numLEDs
    #                 pixels[i] = (64, 64, 64)
    #                 client.put_pixels(pixels)
    #                 time.sleep(0.01)



soundstart = time.time()
#with open('cdrcsequences.txt', 'r') as the_file:
with open(sys.argv[1], 'r') as the_file:
    print "opening sequence file: " + sys.argv[1]
    sequenceConstant = json.load(the_file)

# # sequenceConstant = {'sequence1':
# #                         {'1': {'time': 1, 'jaw': 100, 'pan': 60, 'tilt': 90},
# #                          '2': {'time': 2, 'jaw': 90,  'pan': 90, 'tilt': 80}}  # keyed for JSON compatibility
# #                    }
sequence = {}
sequenceRunning = False

sounds = {}
def loadSounds():
    global sounds, sequenceConstant
    for soundKey, sound in sequenceConstant.iteritems():
        #print "sound for " + soundKey + ": " + sound['audio']
        try:
            sounds[soundKey] = pygame.mixer.Sound(sound['audio'])
        except:
            print "unable to load sound for " + soundKey + " (" + sound['audio'] + ")"
        else:
            print "loaded sound for " + soundKey + ": " + sound['audio']
    #print sounds


def playsound(_sound):
    global sounds, sequenceConstant
    print "playing sound"

    pygame.mixer.stop()

    channel = sounds[_sound].play()
    # set the volume of the channel
    # so the sound is only heard to the left
    #channel.set_volume(1, 0)
    # wait for 1 second
    #time.sleep(4)

def parsePlaySequence(_incoming):
    global sequence, sequenceConstant, sequenceRunning
    print "incoming: " + str(_incoming)
    playsequence_locator = _incoming.find('playsequence')
    print "incoming to playsequence locator: " + str(_incoming[playsequence_locator:])
    sound_locator = playsequence_locator + 13
    print "incoming to sound locator: " + str(_incoming[sound_locator:])
    sound_demarcator = _incoming[sound_locator:].find(']')
    print "sound_demarcator: " + str(sound_demarcator)
    soundToPlay = _incoming[sound_locator:sound_demarcator + sound_locator]

    playSequence(soundToPlay)


def playSequence(_sequence):
    global robotMode, sequenceRunning, sequenceConstant, soundstart, sequence, cdrc_emotion, cdrc_jaw, cdrc_awakeAsleep, cdrc_emotionMask, cdrc_eyelidMask, cdrc_pupilMask
    
    try:
        sequence = sequenceConstant[_sequence]['sequence'][:] # Make a copy!
    except Exception as inst:
        print bcolors.FAIL
        print "couldn't play sequence \"" + str(_sequence) + "\" (" + str(type(_sequence)) + ")"
        print type(inst)     # the exception instance
        print inst.args      # arguments stored in .args
        print inst           # __str__ allows args to printed directly
        print bcolors.ENDC
        return

    # sequence = sequenceConstant['sequence1']['sequence']
    soundstart = time.time()
    #print "this is happening"
    sequenceRunning = True
    sendSomething(robotMode + " playing sequence " + str(_sequence) + "\n")
    if robotMode == "pumpkin":
        print "*** sequence: " + str(_sequence) + " ***"
        if _sequence == "7":
            #print "it equals 7"
            servos.moveServo(0, 60)  # hack for the video
            servos.moveServo(1, 90)
        else:
            servos.moveServo(0, 90)
            servos.moveServo(1, 90) # make the pumpkin look dead center when a sequence starts
    elif robotMode == "cdrc":
        resetCdrcPixels()

    playsound(_sequence)


def sendSomething(_message):
    for sock in interface.connections:
        sock.send(_message)


def allPixelsFull():
    print "all pixels full"
    pixels = [ (255, 255, 255) ] * 40
    client.put_pixels(pixels)

if robotMode == "cdrc":
    allPixelsFull()


def parseIncoming(_incoming):
    commandIsForUs = False
    global sequenceConstant
    
    if _incoming.find('playsequence') != -1:
        parsePlaySequence(_incoming)
        commandIsForUs = True

    if _incoming.find('printSequences') != -1:
        print sequenceConstant
        commandIsForUs = True

    if _incoming.find('stopaudio') != -1:
        pygame.mixer.stop()
        stopSequence()
        commandIsForUs = True

    if _incoming.find('ping') != -1:
        sendSomething("pong\n")
        commandIsForUs = True

    if _incoming.find('resetpixels') != -1:
        resetCdrcPixels()
        commandIsForUs = True

    if _incoming.find('allpixelsfull') != -1:
        allPixelsFull()
        commandIsForUs = True

    if commandIsForUs == True:
        print bcolors.OKGREEN + time.strftime("%Y-%m-%d %H:%I:%S") + " received: " + _incoming + bcolors.ENDC
    else:
        print bcolors.OKBLUE + "received: " + _incoming + bcolors.ENDC



class ConnHandler(asyncore.dispatcher):

    #def __init__(self, addr, conn, server):
    def __init__(self, conn, server):
        asyncore.dispatcher.__init__(self, conn)
        #self.client_ipaddr = addr[0]
        self.conn = conn
        self.server = server
        self.obuffer = []
        self.write("Welcome to the pumpkin head robot!\r\n")

    def write(self, data):
        self.obuffer.append(data)
        print self.obuffer

    def shutdown(self):
        print "shutdown"
        self.obuffer.append(None)

    def handle_read(self):
        # a = 0
        # print self.server.connections
        # for connection in self.server.connections:
        #     a += 1
        #     print connection
        # print "number of connections: " + str(a)
        data = self.recv(4096)
        if data == '\x04':
            data = "exit"

        data = data.strip()

        #print bcolors.OKBLUE + data + bcolors.ENDC
        parseIncoming(data)


    def writable(self):
        return self.obuffer

    # def handle_error(self):f
    #     print "HANDLE ERROR!!!"
    #     a = 0
    #     print self.server.connections
    #     for connection in self.server.connections:
    #         a += 1
    #         print connection
    #     print "number of connections: " + str(a)
    #     print "THIS CONCLUDES HANDLE ERROR"
    #     time.sleep(1)

    def handle_write(self):
        if self.obuffer[0] is None:
            print "closing because self.obuffer[0] is None (???)"
            self.close()
            return

        sent = self.send(self.obuffer[0])
        if sent >= len(self.obuffer[0]):
            self.obuffer.pop(0)
        else:
            self.obuffer[0] = self.obuffer[0][sent:]

    def handle_close(self):
        print "handle_close"
        a = 0
        # print self.server.connections
        for connection in self.server.connections:
            a += 1
            # print connection
        # print "number of connections: " + str(a)
        # print "end handle_close"
        if a > 0:
            try:
                self.server.connections.remove(self)
            except:
                print "** this is a thing that once crashed the program; maybe it won't now?"
        #setDefaultStatus()  # the brain is disconnected; no point in asserting that we know what the heck is going on until we reconnect
        self.close()





class localserver(asyncore.dispatcher):
    conn_handler = ConnHandler

    #def __init__(self, _connection):
    def __init__(self):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        #self.create_socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.set_reuse_addr()
        #self.bind(_connection)
        self.bind(('', 5000))
        self.listen(5)
        self.connections = []

    def handle_accept(self):
        conn, addr = self.accept()

        self.connections.append(self.conn_handler(conn, self))

    def shutdown(self):
        print "localserver.shutdown is calling for a close()"
        self.close()
        for conn in self.connections:
            conn.write("\r\nShutting down...\r\n")
            conn.shutdown()



def asyncoreLoop():
    print "begin asyncore loop"
    asyncore.loop(use_poll=True)

def sequenceLoop():
    global robotMode, masterPixelColor, masterPixelMultiplier, cdrc_emotion, cdrc_jaw, cdrc_awakeAsleep, cdrc_emotionMask, cdrc_eyelidMask, cdrc_pupilMask, cdrc_eyesLeftRight, cdrc_eyelids
    print "begin sequence loop"
    nextMovement = datetime.datetime.now() + datetime.timedelta(seconds=3)
    global soundstart, sequence, sequenceRunning
    while 1:
        #time.sleep(0.01)
        if sequenceRunning:
            #print "sequenceRunning: " + str(sequenceRunning)
            if len(sequence) > 0:
                thisTime = time.time() - soundstart + 0.1  # the extra 0.1 is to sync up the audio with the animation
                #print thisTime
                #animationFramesThisPlaybackFrame = 0
                for entryIndex, entry in enumerate(sequence):
                #for entryKey in sequence.keys():
                    #entry = sequence[entryKey]
                    if thisTime > entry['time'] and thisTime < entry['time'] + 0.2:  # if it falls more than 0.2 seconds behind, skip it; we can afford to skip frames
                        #animationFramesThisPlaybackFrame += 1
                        print "****"
                        print "time: " + str(thisTime)
                        print "time in file: " + str(entry['time'])

                        #print entry
                        if serialEnabled and robotMode == "pumpkin":
                            if 'jaw' in entry:
                                #jaw = pow(max(entry['jaw'] - 16, 0), 3) / 200
                                #jaw = max(entry['jaw'] - 24, 0) * 3
                                jaw = entry['jaw'] * 1.3
                                servos.moveServo(2, jaw)
                                #print jaw

                            if 'pan' in entry:
                                servos.moveServo(0, entry['pan'])
                                print "pan: " + str(entry['pan'])

                            if 'tilt' in entry:
                                tilt = entry['tilt']
                                tilt = tilt - 10
                                if tilt > 105:
                                    tilt = 105
                                servos.moveServo(1, tilt)
                                print "tilt: " + str(tilt)
                        elif robotMode == "cdrc":
                            pixels = range(40)

                            if 'jaw' in entry:
                                cdrc_jaw = entry['jaw']
                                print "cdrc_jaw: " + str(cdrc_jaw)

                            if 'awakeAsleep' in entry:
                                cdrc_awakeAsleep = entry['awakeAsleep']
                                print "cdrc_awakeAsleep: " + str(cdrc_awakeAsleep)

                                if cdrc_awakeAsleep == 127:
                                    masterPixelMultiplier = 0.5
                                elif cdrc_awakeAsleep == 0:
                                    masterPixelMultiplier = 0.125

                            if 'emotion' in entry:
                                cdrc_emotion = entry['emotion']
                                print "cdrc_emotion: " + str(cdrc_emotion)

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

                                print "emotion index: " + str(emotionIndex)

                            if 'eyesLeftRight' in entry:
                                cdrc_eyesLeftRight = entry['eyesLeftRight']
                                print "cdrc_eyesLeftRight: " + str(cdrc_eyesLeftRight)

                                pupilIndex = cdrc_eyesLeftRight / (8192 / 4)
                                print pupilIndex
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

                                print "pupil index: " + str(pupilIndex)

                            drawEyes = False
                            if 'eyesUp' in entry:
                                cdrc_eyelids = -entry['eyesUp']
                                print "cdrc_eyelids: " + str(cdrc_eyelids)
                                drawEyes = True

                            if 'eyesDown' in entry:
                                cdrc_eyelids = entry['eyesDown']
                                # print "cdrc_eyelids: " + str(cdrc_eyelids)
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

                                print "eyelid index: " + str(eyelidIndex)
                                # print cdrc_eyelidMask


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

                                #print cdrc_pupilMask



                                # if cdrc_eyesLeftRight < 60:
                                #     pupilIndex = cdrc_eyesLeftRight / 8
                                #     print pupilIndex
                                #     for i in range(0, pupilIndex):
                                #         cdrc_pupilMask[7 - i]  = 1
                                #         cdrc_pupilMask[8 + i]  = 1
                                #         cdrc_pupilMask[23 - i] = 1
                                #         cdrc_pupilMask[24 + i] = 1
                                # elif cdrc_eyesLeftRight > 68:
                                #     pupilIndex = (cdrc_eyesLeftRight / 8) - 64
                                #     print pupilIndex
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


                            #print "resulting color: " + str(resultingColor) + "(" + str(type(resultingColor)) + ")"

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
                            print bcolors.FAIL
                            print "Error deleting old sequence!"
                            print type(inst)     # the exception instance
                            print inst.args      # arguments stored in .args
                            print inst           # __str__ allows args to printed directly
                            print bcolors.ENDC
                            stopSequence()
                            #return

                        break  #I'm gonna try doing this to kill the flickering
                    # else:
                    #     print "****"
                    #     print "skipping " + str(entry['time'])
                #time.sleep(0.02)
                #print "animation frames this playback frame: " + str(animationFramesThisPlaybackFrame)
            else:
                #print "sequence length is less than zero"
                #print sequence
                stopSequence()
                # sequenceRunning = False
                # sendSomething(robotMode + " sequence finished\n")
                # if robotMode == "cdrc":  # dim the lights
                #     pixels = [ (32, 32, 32) ] * 40
                #     client.put_pixels(pixels)
        else:  # random head movement
            if robotMode == "pumpkin":
                if datetime.datetime.now() > nextMovement:
                    print "time for random motion"
                    nextMovement = datetime.datetime.now() + datetime.timedelta(seconds=random.randrange(3, 8))
                    servos.moveServo(0, random.randrange(85, 95))
                    servos.moveServo(1, random.randrange(85, 95))



def stopSequence():
    global sequenceRunning, robotMode
    sequenceRunning = False
    sendSomething(robotMode + " sequence finished\n")
    if robotMode == "cdrc":  # dim the lights
        pixels = [ (32, 32, 32) ] * 40
        client.put_pixels(pixels)
    elif robotMode == "pumpkin":
        servos.moveServo(2, 0)  # close that mouth



# class ServoController:
#     def __init__(self):
#         usbPort = '/dev/ttyACM0'
#         self.sc = serial.Serial(usbPort)

#     def closeServo(self):
#         self.sc.close()

#     def setAngle(self, n, angle):
#         if angle > 180 or angle <0:
#            angle=90
#         byteone=int(254*angle/180)
#         bud=chr(0xFF)+chr(n)+chr(byteone)
#         self.sc.write(bud)

#     def setPosition(self, servo, position):
#         position = position * 4
#         poslo = (position & 0x7f)
#         poshi = (position >> 7) & 0x7f
#         chan  = servo &0x7f
#         data =  chr(0xaa) + chr(0x00) + chr(0x04) + chr(chan) + chr(poslo) + chr(poshi)
#         self.sc.write(data)

#     def getPosition(self, servo):
#         chan  = servo &0x7f
#         data =  chr(0xaa) + chr(0x00) + chr(0x10) + chr(chan)
#         self.sc.write(data)
#         w1 = ord(self.sc.read())
#         w2 = ord(self.sc.read())
#         return w1, w2

#     def getErrors(self):
#         data =  chr(0xaa) + chr(0x00) + chr(0x21)
#         self.sc.write(data)
#         w1 = ord(self.sc.read())
#         w2 = ord(self.sc.read())
#         return w1, w2

#     def triggerScript(self, subNumber):
#         data =  chr(0xaa) + chr(0x00) + chr(0x21) + chr(0x27) + chr(subNumber)
#         self.sc.write(data)

# servos = ServoController()
# print servos.getPosition(0)
# servos.setPosition(0, 0)
# servos.setPosition(1, 0)
# servos.setPosition(2, 0)


class ServoController:
    def __init__(self, controllerPort):
        self.serialCon = serial.Serial(controllerPort, baudrate=9600)

    def moveServo(self, channel, target):
        #print "moving servo"
        # HACK
        #if channel == 1:
        #    print "target: " + str(target)
        if channel == 1 and target > 113:
            target = 113
            print target
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
    print "initializing servo controller"

    servos = ServoController('/dev/ttyACM0')
    servos.moveServo(0, 90)
    servos.moveServo(1, 90)
    servos.moveServo(2, 0)



# key_normal        = 106
# key_totd          = 105
# key_elevatorUp    = 108
# key_elevatorDown  = 103
# key_estop         = 22
# key_facp          = 24
# key_bigswitch     = 23


# def keyboardHandler(_key, _pressed):
#     print "Key " + str(_key) + " was " + ("pressed" if _pressed == True else "released")

#     if   _key == key_normal       and _pressed == True:
#         print("'normal' button pressed")
#         sendSomething("[normal]\n")
#     elif _key == key_totd         and _pressed == True:
#         print("'ToTD' button pressed")
#         sendSomething("[ToTD]\n")
#     elif _key == key_elevatorUp   and _pressed == True:
#         print("elevator up button pressed")
#         sendSomething("[elevatorUp]\n")
#     elif _key == key_elevatorDown and _pressed == True:
#         print("elevator down button pressed")
#         sendSomething("[elevatorDown]\n")
#     elif _key == key_estop        and _pressed == False:
#         print("emergency stop button down")
#         sendSomething("[estop]\n")
#     elif _key == key_facp:
#         print("facp switch switched")
#         sendSomething("[normal]\n")
#     elif _key == key_bigswitch:
#         if _pressed == False:
#             print("big switch is down")
#             sendSomething("[blacklight]\n")
#         else:
#             print ("big switch is up")
#             sendSomething("[normal]\n")

    #playSequence("sequence1")


# def keyboardMonitor():
#     byte = []
#     key = open('/dev/input/event2', 'r')
#     while True:
#         for bit in key.read(1):
#             byte.append(ord(bit))
#             if len(byte) == 8:
#                 #print byte
#                 #if byte[2] in keyboardMap:
#                 if byte == [1, 0, byte[2], 0, 1, 0, 0, 0]:
#                     keyboardHandler(byte[2], True)
#                 elif byte == [1, 0, byte[2], 0, 0, 0, 0, 0]:
#                     keyboardHandler(byte[2], False)
#                 byte = []


# soundArray = []
# jawValue   = 0

serialPerSecond = 0
serialWrites    = 0

# def jawAudio():
#     global jawValue, serialPerSecond
#     while 1:
#         l,data = inp.read()
#         if l:
#             leftonly = audioop.tomono(data, 2, 1, 0)
#             # #print leftonly
#             amp = audioop.max(leftonly, 2)
#             #print amp
#             #amp = audioop.max(data, 2)
#             if True: #amp > 16000:
#                 jaw = (amp - 90) / 700
#                 #print jaw
#                 #jaw = (amp - 17000) / 400
#                 if jaw < 0: jaw = 0
#                 # if len(soundArray) > 2:
#                 #     soundArray.pop(0)
#                 # soundArray.append(jaw)
#                 # #print soundArray

#                 # jaw =  sum(soundArray) / len(soundArray)
#                 #print jaw
#                 #print "pre"
#                 if jaw < 30:
#                     jawValue = jaw
#                 else:
#                     jawValue = 30 + ((jaw - 30) / 3)
#                 # try:
#                 #     jawValue = jaw #math.log10(jaw) * 35 - 30
#                 # except:
#                 #     pass
#                 serialPerSecond += 1
#                 pumpkincontroller.write("#jawservo=" + str(jawValue + 10) + "\n")
#                 #print jawValue
#                 # if serialEnabled:
#                 #     try:
#                 #         pumpkincontroller.write("#jawservo=" + str(jaw) + "\n")
#                 #     except Exception as inst:
#                 #         print "serial error"
#                 #         print type(inst)     # the exception instance
#                 #         print inst.args      # arguments stored in .args
#                 #         print inst           # __str__ allows args to printed directly
#                 #print "post"
#         #time.sleep(.001)




# def jawWriter():
#     global jawValue, serialPerSecond, serialWrites
#     while 1:
#         if serialEnabled:
#             serialPerSecond += 1
#             serialWrites += 1
#             print "serial writes: " + str(serialWrites)
#             pumpkincontroller.write("#jawservo=" + str(jawValue) + "\n")
#             pumpkincontroller.drainOutput()
#             #print jawValue

#         time.sleep(0.01)


# # for the jaw
# inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE,alsaaudio.PCM_NONBLOCK)

# # Set attributes: Mono, 8000 Hz, 16 bit little endian samples
# inp.setchannels(2)
# inp.setrate(22050)
# inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)

# inp.setperiodsize(160)

#interface = localserver((socket.gethostname(), 5000))
interface = localserver()

# start pygame
pygame.mixer.pre_init(frequency=48000, buffer=1024, channels=2)
pygame.mixer.init()
# pygame.init()
# pygame.display.quit()

loadSounds()

# load a sound file into memory
# sound = pygame.mixer.Sound("audiosone 1.wav")





print "hello?"

try:
    asyncoreLoopThread = Thread(target=asyncoreLoop)
    asyncoreLoopThread.daemon = True
    asyncoreLoopThread.start()

    sequenceLoopThread = Thread(target=sequenceLoop)
    sequenceLoopThread.daemon = True
    sequenceLoopThread.start()


    # keyboardLoopThread = Thread(target=keyboardMonitor)
    # keyboardLoopThread.daemon = True
    # keyboardLoopThread.start()

    # jawAudioThread = Thread(target=jawAudio)
    # jawAudioThread.daemon = True
    # jawAudioThread.start()

    # jawWriterThread = Thread(target=jawWriter)
    # jawWriterThread.daemon = True
    # jawWriterThread.start()

    while 1:
        time.sleep(1)
        #sendSomething("pumpkin says hello")
        #print sequenceRunning
        #if robotMode == "cdrc":
        #    print cdrc_eyesLeftRight
        #print "serial per second: " + str(serialPerSecond)
        #serialPerSecond = 0

    #asyncore.loop(use_poll=True)

except KeyboardInterrupt:
    asyncore.close_all()



