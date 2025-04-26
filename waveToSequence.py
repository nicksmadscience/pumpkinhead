import wave
from itertools import izip_longest
import json
from statistics import median

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)


master = {}


interval = 0.03

for audiofile in range(1, 4):
    print audiofile
    theWave = wave.open("%02d" % (audiofile) + ".wav", 'r')


    cursor = 0
    time = 0.0

    sequencearray = []

    while cursor < theWave.getnframes():
        cursor += int(44100 * interval)
        time += interval

        chunk = theWave.readframes(int(44100 * interval))

        thisJoant = []
        audiosmooth = [0, 0, 0, 0, 0, 0, 0]
        for ll, lh, rl, rh in grouper(4, chunk):
            audiosmooth.pop(0)
            audiosmooth.append(int(ord(lh)))
            audiosmooth_average = sum(audiosmooth) / len(audiosmooth)
            thisJoant.append(int(audiosmooth_average))
            print audiosmooth

        #jaw = sum(thisJoant) / len(thisJoant)
        jaw = median(thisJoant)
        newValues = {"jaw": jaw, "time": + round(time, 1)}
        sequencearray.append(newValues)

    master[str(audiofile)] = {"audio": ("%02d" % (audiofile)) + ".wav", "sequence": sequencearray}

the_file = open('pumpkinsequences.txt', 'w')
the_file.write(json.dumps(master, indent=4, sort_keys=True))

