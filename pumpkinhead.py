#!/usr/bin/env python 
"""Code that runs the Halloween robots CDRC and Pumpkinhead."""



import time
import pygame
import traceback
import serial


from threading import Thread
import json

# for choosing between cdrc and the pumpkin head via the command line
import sys

# for random pumpkin head movement!
import random
import datetime

from flask import Flask, Response






## CDRC SETUP ##
# screen
# sudo /usr/local/bin/fcserver
# (exit screen)
# cd cdrc
# python pumpkinhead.py cdrcsequences.txt cdrc

## PUMPKIN SETUP ##
# cd pumpkinhead
# python pump*py pump*txt pumpkin







class Robot():
    """Let's make a friggin' robot!  Can be a CDRC or a Pumpkinhead."""
    def __init__(self, robotMode, sequencefile, nohardware=False):
        self.robotMode = robotMode
        self.sequencefile = sequencefile
        self.nohardware = nohardware

        self.serialEnabled = False

        print ("ROBOT MODE IS: " + self.robotMode)

        self.initSound()
        self.loadSounds()

        if self.robotMode == "cdrc":
            self.resetCdrcPixels()
            self.initOPC()
            self.allPixelsFull()
        elif self.robotMode == "pumpkinhead":
            self.initServos()


    def initServos(self):
        """Set serial enabled and move servos to home positions."""
        self.serialEnabled = True
        if not self.nohardware:
            self.servos = ServoController('/dev/ttyACM0')
            self.servos.moveServo(0, 90)
            self.servos.moveServo(1, 90)
            self.servos.moveServo(2, 0)


            

    def resetCdrcPixels(self):
        """Set CDRC pixels to their default state."""
        print ("resetting self.pixels")
        self.mainPixelMultiplier = 1.0
        self.mainPixelColor      = [255, 255, 255]
        self.cdrc_emotion       = 64
        self.cdrc_jaw           = 0
        self.cdrc_awakeAsleep   = 0
        self.cdrc_eyesLeftRight = 0
        self.cdrc_eyelids       = 0
        self.cdrc_emotionMask   = [1 for x in range(0, 32)]
        self.cdrc_eyelidMask    = [1 for x in range(0, 32)]
        self.cdrc_pupilMask     = [1 for x in range(0, 32)]



    def initOPC(self):
        """Initialize the OpenPixelControl library (for use with a FadeCandy, which is now 
        unfortunately defunct.)"""
        if not self.nohardware:
            import opc
            self.client = opc.Client('localhost:7890')

    

    def initSound(self):
        """Get all the sound-related stuff initialized."""
        self.soundstart = time.time()
        with open(sys.argv[1], 'r') as the_file:
            print ("opening sequence file: " + sys.argv[1])
            self.sequenceConstant = json.load(the_file)

        self.sequence = {}
        self.sequenceRunning = False
        self.sequenceThatIsCurrentlyRunning = "none"

        pygame.mixer.pre_init(frequency=48000, buffer=1024, channels=2)
        pygame.mixer.init()


    def loadSounds(self):
        """Load all the .wav files of dialogue based on the provided json file."""
        self.sounds = {}
        for soundKey, sound in self.sequenceConstant.items():
            try:
                self.sounds[soundKey] = pygame.mixer.Sound(sound['audio'])
            except:
                traceback.print_exc()
                print ("unable to load sound for " + soundKey + " (" + sound['audio'] + ")")
            else:
                print ("loaded sound for " + soundKey + ": " + sound['audio'])





    def playsound(self, _sound):
        """Play the specified already-loaded sound (but stop any existing sounds first)."""
        print ("playsound(" + str(_sound) + ")")
        print ("playing sound")

        pygame.mixer.stop()

        self.channel = self.sounds[_sound].play()


    def playSequence(self, _sequence):
        """Simultaneously play an audio file and start a servo or LED sequence
        and pray they stay in sync (they do consistently enough that I'm not
        super concerned about keeping things more manually synced up).)"""

        print ("playSequence {s}".format(s=_sequence))
        
        try:
            self.sequence = self.sequenceConstant[_sequence]['sequence'][:] # Make a copy!
        except:
            print ("couldn't play sequence \"" + str(_sequence) + "\" (" + str(type(_sequence)) + ")")
            traceback.print_exc()
            return

        self.soundstart = time.time()
        self.sequenceRunning = True
        self.sequenceThatIsCurrentlyRunning = _sequence
        if self.robotMode == "pumpkin":
            print ("*** sequence: " + str(_sequence) + " ***")
            if not self.nohardware:
                if _sequence == "7":
                    self.servos.moveServo(0, 60)  # hack for the video
                    self.servos.moveServo(1, 90)
                else:
                    self.servos.moveServo(0, 90)
                    self.servos.moveServo(1, 90) # make the pumpkin look dead center when a sequence starts
        elif self.robotMode == "cdrc":
            self.resetCdrcPixels()

        self.playsound(_sequence)



    def allPixelsFull(self):
        """All pixels to full (white)."""
        print ("all pixels full")
        self.pixels = [ (255, 255, 255) ] * 40
        if not self.nohardware:
            self.client.put_pixels(self.pixels)




    def sequenceLoop(self):
        """Continuous, independently-threaded loop that serves as an animation player /
        frame progressor."""
        print ("begin sequence loop")
        self.nextMovement = datetime.datetime.now() + datetime.timedelta(seconds=3)
        while True:
            if self.sequenceRunning and len(self.sequence) > 0:
                thisTime = time.time() - self.soundstart + 0.1  # the extra 0.1 is to sync up the audio with the animation
                for frameIndex, frame in enumerate(self.sequence):
                    if thisTime > frame['time'] and thisTime < frame['time'] + 0.2:  # if it falls more than 0.2 seconds behind, skip it; we can afford to skip frames                                                    
                        print ("{rm} - time: {t}  time in file: {tif}".format(
                            rm=self.robotMode,
                            t=round(thisTime, 3),
                            tif= frame['time']
                        ))

                        if self.serialEnabled and self.robotMode == "pumpkin":
                            self.sequenceFramePumpkin(frame)
                            
                        elif self.robotMode == "cdrc":
                            self.sequenceFrameCDRC(frame)

                        try:
                            del self.sequence[frameIndex]  # delete the frame from the list so we can be more efficient as the clip progresses??
                        except:
                            print ("Error deleting old sequence!")
                            traceback.print_exc()
                            self.stopSequence()


            else:  # random head movement
                if self.robotMode == "pumpkin":
                    if datetime.datetime.now() > self.nextMovement:
                        print ("time for random motion")
                        self.nextMovement = datetime.datetime.now() + datetime.timedelta(seconds=random.randrange(3, 8))
                        if not self.nohardware:
                            self.servos.moveServo(0, random.randrange(85, 95))
                            self.servos.moveServo(1, random.randrange(85, 95))

            time.sleep(0.01)


    def sequenceFramePumpkin(self, frame):
        """Manages all animation frames for Pumpkinhead or similar servo-based bot."""
        if 'jaw' in frame:
            jaw = frame['jaw'] * 1.3
            if not self.nohardware:
                self.servos.moveServo(2, jaw)

        if 'pan' in frame:
            if not self.nohardware:
                self.servos.moveServo(0, frame['pan'])
            print ("pan: " + str(frame['pan']))

        if 'tilt' in frame:
            tilt = frame['tilt']
            tilt = tilt - 10
            if tilt > 105:
                tilt = 105
            if not self.nohardware:
                self.servos.moveServo(1, tilt)
            print ("tilt: " + str(tilt))


    def sequenceFrameCDRC(self, frame):
        """Manages all animation frames for CDRC or similar pixel-based bot."""
        self.pixels = [0] * 40

        if 'jaw' in frame:
            self.cdrc_jaw = frame['jaw']
            print ("cdrc_jaw: " + str(self.cdrc_jaw))

        if 'awakeAsleep' in frame:
            self.cdrc_awakeAsleep = frame['awakeAsleep']
            print ("cdrc_awakeAsleep: " + str(self.cdrc_awakeAsleep))

            if self.cdrc_awakeAsleep == 127:
                self.mainPixelMultiplier = 0.5
            elif self.cdrc_awakeAsleep == 0:
                self.mainPixelMultiplier = 0.125

        if 'emotion' in frame:
            self.cdrc_emotion = frame['emotion']
            print ("cdrc_emotion: " + str(self.cdrc_emotion))

            if self.cdrc_emotion < 57:  # sad
                notblue = self.cdrc_emotion * 4
                self.mainPixelColor = (notblue, notblue, 255)
            elif self.cdrc_emotion > 71:  # angry
                notred = 255 - ((self.cdrc_emotion - 64) * 4)
                self.mainPixelColor = (255, notred, notred)
            else:  # deadband neutral
                self.mainPixelColor = (255, 255, 255)

            # and now the eyes
            self.emotionIndex = int(self.cdrc_emotion / (128 / 19))
            emotions = {
                0:  (0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0),
                1:  (0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0),
                2:  (0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0),
                3:  (0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0),
                4:  (0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0),
                5:  (0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0),
                6:  (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
                7:  (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
                8:  (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
                9:  (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
                10: (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
                11: (1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
                12: (1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1),
                13: (1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1),
                14: (0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0),
                15: (0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0),
            }
            self.cdrc_emotionMask = emotions[self.emotionIndex]


        # eyes looking left and right
        if 'eyesLeftRight' in frame:
            self.cdrc_eyesLeftRight = frame['eyesLeftRight']

            self.pupilIndex = self.cdrc_eyesLeftRight / (8192 / 4)
            pupils = {
                -4: (1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0),
                -3: (1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1),
                -2: (1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1),
                -1: (1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1),
                0:  (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
                1:  (1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1),
                2:  (1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1),
                3:  (1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1),
                4:  (0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1)
            }
            self.cdrc_pupilMask = pupils[self.pupilIndex]
            print ("pupil index: " + str(self.pupilIndex))


        # eyes up or down
        drawEyes = False
        if 'eyesUp' in frame:
            cdrc_eyelids = -frame['eyesUp']
            print ("cdrc_eyelids: " + str(cdrc_eyelids))
            drawEyes = True

        if 'eyesDown' in frame:
            self.cdrc_eyelids = frame['eyesDown']
            drawEyes = True

        if drawEyes == True:
            eyelidIndex = cdrc_eyelids / (128 / 4)

            eyelids = {
                -8: (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0),
                -7: (0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0),
                -6: (0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0),
                -5: (0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0),
                -4: (0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0),
                -3: (0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0),
                -2: (0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0),
                -1: (0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0),
                0:  (1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1),
                1:  (1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,0,1,1,1,1,1,1,1),
                2:  (1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0,0,0,1,1,1,1,1,1),
                3:  (1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,0,0,0,0,0,0,1,1,1,1,1),
                4:  (1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1,1,1,1),
                5:  (1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,1,1,1),
                6:  (1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,1,1),
                7:  (1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1),
                8:  (0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0)
            }
            self.eyelidMask = eyelids[eyelidIndex]


        # and now it is time to draw
        # calculate the colors
        resultingColor = (self.mainPixelColor[0] * self.mainPixelMultiplier,
            self.mainPixelColor[1] * self.mainPixelMultiplier,
            self.mainPixelColor[2] * self.mainPixelMultiplier)

        # final processing
        for i in range(0, 32):
            self.pixels[i] = (resultingColor[0] * self.cdrc_emotionMask[i] * self.cdrc_pupilMask[i] * self.cdrc_eyelidMask[i],
                resultingColor[1] * self.cdrc_emotionMask[i] * self.cdrc_pupilMask[i] * self.cdrc_eyelidMask[i],
                resultingColor[2] * self.cdrc_emotionMask[i] * self.cdrc_pupilMask[i] * self.cdrc_eyelidMask[i])

        # mouth
        mouth1 = (0, 0, 0)
        mouth2 = (0, 0, 0)
        mouth3 = (0, 0, 0)
        mouth4 = (0, 0, 0)


        if self.cdrc_jaw > 1000:
            mouth1 = resultingColor
 
        if self.cdrc_jaw > 2000:
            mouth2 = resultingColor

        if self.cdrc_jaw > 4000:
            mouth3 = resultingColor

        if self.cdrc_jaw > 6000:
            mouth4 = resultingColor

        self.pixels[32] = mouth4
        self.pixels[33] = mouth3
        self.pixels[34] = mouth2
        self.pixels[35] = mouth1
        self.pixels[36] = mouth1
        self.pixels[37] = mouth2
        self.pixels[38] = mouth3
        self.pixels[39] = mouth4

        # and finally, write the pixels to the FadeCandy (once again and much to my disappointment, defunct)
        if not self.nohardware:
            self.client.put_pixels(self.pixels)



    def stopSequence(self):
        """E-stop for both audio and animation."""
        self.sequenceThatIsCurrentlyRunning = "none"
        self.sequenceRunning = False

        if self.robotMode == "cdrc":  # dim the lights
            self.pixels = [ (32, 32, 32) ] * 40
            if not self.nohardware:
                self.client.put_pixels(self.pixels)
        elif self.robotMode == "pumpkin":
            if not self.nohardware:
                self.servos.moveServo(2, 0)  # close that mouth




class ServoController:
    """For use with a servo controller whose name I forget.  Pretty sure this part was 
    grabbed wholesale from somewhere on the internet"""
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



# Let's get webserver stuff configured (recently converted to Flask for modernization's sake).
app = Flask(__name__)


@app.route("/")
def r_index():
    """Let the user know what HTTP-based commands are available."""
    return Response("commands:\n\nplaysequence/x\nstopaudio\nping", mimetype="text/plain")

@app.route("/playsequence/<path:path>")
def r_playsequence(path):
    """Play the specified sequence."""
    print ("playsequence function activated woo")
    robot.playSequence(path)
    return Response("playing sequence " + path, mimetype="text/plain")

@app.route("/stopaudio")
def r_stopaudio():
    """Stop audio and animation."""
    pygame.mixer.stop()
    robot.stopSequence()
    return Response("stopping audio", mimetype="text/plain")

@app.route("/ping")
def r_ping():
    """Used by controller software to make sure this bot is in working order."""
    return Response("pong", mimetype="text/plain")

@app.route("/getaudiostate")
def r_getaudiostate():
    """Tell the controller what audio/animation is currently being played."""
    return Response(str(robot.sequenceThatIsCurrentlyRunning), mimetype="text/plain")




if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("sequences")
    parser.add_argument("robotype")
    parser.add_argument("--nohardware")
    args = parser.parse_args()

    robot = Robot(args.robotype, args.sequences, args.nohardware == "true")


    # Start the animation loop
    sequenceLoopThread = Thread(target=robot.sequenceLoop)
    sequenceLoopThread.daemon = True
    sequenceLoopThread.start()

    # Run a Flask dev server (probably not worth doing the whole WSGI thing))
    app.run(debug=True, host="0.0.0.0", port=5001)