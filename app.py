"""
This is a scrappy little playground project for numpy and pyaudio.

Code is freely adapted from SW Harden's code found here:
http://www.swharden.com/wp/2016-07-19-realtime-audio-visualization-in-python/
"""


from __future__ import division

import numpy as np
import pyaudio
import sys

CHUNK =  4096 # number of data points to be read at a time
RATE  = 44100 # time resolution of the recording device (Hz)

def printPeak(data, row=1, freqs=[]):
    sys.stderr.write("\033[%d;1H"%(row)) # Move to left col of given row
    sys.stderr.write("\033[K")   # clear row
    peak = np.average(np.abs(data))*2
    bars="#"*int(25*peak/2**16)
    
    label = row;
    # if (len(freqs)):
    #     label = int(freqs[(row-1) * CHUNK/16])
    
    print("%16s %05d %s"%(label, peak, bars))
    
    



p = pyaudio.PyAudio()
stream = p.open(
  format=pyaudio.paInt16, 
  channels=1, 
  rate=RATE, 
  input=True, 
  frames_per_buffer=CHUNK
)

sys.stderr.write("\033[1;1H") # Move to left col of given row
sys.stderr.write("\033[2J")

# print RATE
# print 1/RATE

while True:
    data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
    spectrum = np.fft.rfft(data)
    bands = np.array_split(spectrum, 16)
    
    freqs = np.fft.rfftfreq(CHUNK, 1/RATE)

    for i, b in enumerate(bands):
        row = i+1
        printPeak(b, row=row, freqs=freqs)


stream.stop_stream()
stream.close()
p.terminate()
