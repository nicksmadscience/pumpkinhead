from mido import MidiFile
import mido
import json
import operator


# cdrc emotion
# pitch bend      = eyes left / right
# 80 (decay)      = awake / asleep
# 18 (general #3) = angry / neutral / sad
# 1 (modulation)  = eyes down?
# 2 (breath)      = eyes up?

cdrc_awakeAsleep_control = 80
cdrc_emotion_control     = 18
cdrc_eyesDown_control    = 1
cdrc_eyesUp_control      = 2


# pumpkin head movement
pumpkin_tiltDown = 1
pumpkin_tiltUp   = 2

# this is where each clip landed in my Logic project
#offsets = [1, 11, 36, 42, 55, 81, 109, 156, 159, 204, 272, 278, 283, 285, 289, 294, 300, 309, 313, 318, 322, 328, 335, 341, 348, 352, 355, 360, 363, 367, 383, 387, 390, 392, 395, 397, 400, 402, 404, 406, 408, 410, 413, 416, 419, 421, 432, 457, 473, 486, 491]
offsets = [2, 29, 66, 105, 112, 138, 157, 180, 206, 241, 285, 299, 333, 346, 368, 418, 428, 434, 438, 442, 448, 467, 471, 482, 510, 534, 566, 651, 674, 692, 709, 711, 714, 720, 725, 739, 759, 775, 796, 810, 816]

master = {}

for midinumber in range(1, 42):
    cumulativetime = 0
    mid = MidiFile("%02d" % (midinumber) + ".mid")
    messageNumber = 0
    cumulativetime = 0
    #thejoant = [{"time": 0, "jaw": 0}]  # so we start with something (otherwise some component will complain about missing bits)
    thisMidiFile = {} # sorted by time
    thisMidiFile["0"] = {}

    for message in mid:

        # Okay, here's what needs to happen.
        # Every event needs to be rounded to the nearest 20th.
        # The master dictionary for each MIDI file will be sorted by time.
        # The most recent event takes precedence.  Old events that also round to that time will be overwritten.

        #print message
        if messageNumber == 0:  # this came from one huge Logic project, and evidently it doesn't start the notes at zero for each file
            offset = (offsets[midinumber - 1] - 1) * 2
            cumulativetime = message.time - offset
            #print offset
        else:
            cumulativetime += message.time
        messageNumber += 1

        #roundedCumulativeTime = 0.025 * math.ceil(40.0 * cumulativetime)
        #timeString = "{0:.2f}".format(roundedCumulativeTime)
        timeString = "{0:0>3}".format(int(cumulativetime)) + "{:.3f}".format(cumulativetime % 1)[1:]  # couldn't figure out the right way to do this :-(
        # anyway the reason for the weird float is so it'll index the string correctly.  Otherwise the pumpkin head will start with 1, then go to 10, and then maybe 100
        # if it's that long, and go to 2 way at the end.  Because it is indexing strings and not numbers and "10" comes right after "1" in string form

        print (timeString)
        
        if not isinstance(message, mido.MetaMessage):
            if message.channel == 1 or message.channel == 3:
                # make a new slot for this time if it doesn't already exist, in which case we'll add to what's already there
                if timeString not in thisMidiFile:
                    thisMidiFile[timeString] = {}

                if message.channel == 1:
                    thisMidiFile[timeString]['jaw'] = message.pitch
                elif message.channel == 3:
                    try:
                        thisMidiFile[timeString]['eyesLeftRight'] = message.pitch
                    except AttributeError:
                        pass

                    try:
                        if   message.control == cdrc_awakeAsleep_control:
                            thisMidiFile[timeString]['awakeAsleep'] = message.value
                        elif message.control == cdrc_emotion_control:
                            thisMidiFile[timeString]['emotion']     = message.value
                        elif message.control == cdrc_eyesUp_control:
                            thisMidiFile[timeString]['eyesUp']      = message.value
                        elif message.control == cdrc_eyesDown_control:
                            thisMidiFile[timeString]['eyesDown']    = message.value
                    except AttributeError:
                        pass



            # if message.channel == 0 or message.channel == 2:
            #     if timeString not in thisMidiFile:
            #         thisMidiFile[timeString] = {}

            #     if message.channel == 0:
            #         try:
            #             thisMidiFile[timeString]['jaw'] = message.pitch / 275
            #         except AttributeError:
            #             pass

            #     elif message.channel == 2:
            #         try:
            #             thisMidiFile[timeString]['pan'] = (-message.pitch / 275) + 90
            #         except AttributeError:
            #             pass

            #         try:
            #             if message.control == pumpkin_tiltUp:
            #                 #thisMidiFile[timeString]['tiltUp']      = message.value
            #                 #thisMidiFile[timeString]['tilt'] = (-message.value / 60)
            #                 #print "tiltUp " + str(message.value)
            #                 tilt = -message.value
            #             elif message.control == pumpkin_tiltDown:
            #                 #thisMidiFile[timeString]['tilt'] = (message.value / 60)
            #                 #print "tiltDown " + str(message.value)
            #                 tilt = message.value

            #             tilt = (-tilt / 3.0) + 90
            #             print tilt
            #             thisMidiFile[timeString]['tilt'] = tilt

            #         except AttributeError:
            #             pass

                    
                    #thejoant.append({"time": cumulativetime, "jaw": message.pitch / 200})
                    #thisMidiFile[str(roundedCumulativeTime)] = thisMidiEvent
                    #print str(roundedCumulativeTime) + " = " + str(thisMidiFile[str(roundedCumulativeTime)])
                # except Exception as inst:
                #     print "exception"
                #     print inst, inst.args

    #print "thisMidiFile: " + str(thisMidiFile)

    #pprint.pprint(thisMidiFile)

    # turn it into the format that the robots expect, with the time included in each frame instead of indexed by time
    flattenedMidi = []
    sortedMidiFile = sorted(thisMidiFile.items(), key=operator.itemgetter(0))

    # print sortedMidiFile

    # now's when I'm gonna do the whole baked-into-each-frame thing
    cdrc_awakeAsleep = 0
    cdrc_emotion = 64
    cdrc_eyesUp = 0
    cdrc_eyesDown = 0
    cdrc_jaw = 0
    cdrc_eyesLeftRight = 0
    for joant in sortedMidiFile:
        controllers = joant[1]

        if "awakeAsleep" in controllers:
            cdrc_awakeAsleep = controllers['awakeAsleep']

        if "emotion" in controllers:
            cdrc_emotion = controllers['emotion']

        if "eyesUp" in controllers:
            cdrc_eyesUp = controllers['eyesUp']

        if "eyesDown" in controllers:
            cdrc_eyesDown = controllers['eyesDown']

        if "jaw" in controllers:
            cdrc_jaw = controllers['jaw']

        if "eyesLeftRight" in controllers:
            cdrc_eyesLeftRight = controllers['eyesLeftRight']

        finalJoant = {"time": float(joant[0]),
            "awakeAsleep": cdrc_awakeAsleep,
            "emotion": cdrc_emotion,
            "eyesUp": cdrc_eyesUp,
            "eyesDown": cdrc_eyesDown,
            "jaw": cdrc_jaw,
            "eyesLeftRight": cdrc_eyesLeftRight}

        #flattenedFrame = {"time": float(joant[0])}
        #flattenedFrame.update(joant[1])
        #flattenedMidi.append(flattenedFrame)

        flattenedMidi.append(finalJoant)
    


    master[str(midinumber)] = {"audio": ("2016-%02d" % (midinumber)) + ".wav", "sequence": flattenedMidi}

#the_file = open('pumpkinsequences.txt', 'w')
the_file = open('cdrcsequences.txt', 'w')
the_file.write(json.dumps(master, indent=4, sort_keys=True))

