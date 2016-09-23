"""
This is a scrappy little playground project for numpy and pyaudio.

Code is freely adapted from SW Harden's code found here:
http://www.swharden.com/wp/2016-07-19-realtime-audio-visualization-in-python/
"""


from __future__ import division

import aubio # experimenting with alternative to pyaudio
import math
import numpy as np
import pyaudio
import sys

CHUNK =  4096 # number of data points to be read at a time
RATE  = 44100 # time resolution of the recording device (Hz)
NUMBANDS = 22
minFreq = 220
maxFreq = 1760


def printPeak(data, row=1, freqs=[]):
    sys.stderr.write("\033[%d;1H"%(row)) # Move to left col of given row
    sys.stderr.write("\033[K")   # clear row
    peak = np.max(np.abs(data))*2
    num_bars = min( int(25*peak/2**24), 80 )
    bars="#" * num_bars
    
    label = row;
    if (len(freqs)):
        label = int(freqs[row-1])
    
    print("%4s %05d %s"%(label, peak, bars))
    
    

def logChunks(data, numchunks):
    intervals = []
    chunks = []
    start = 0
    length = 1
    while (start < len(data)):
        endIdx = start + length 
        
        if (endIdx >= len(data)):
            interval = data[start:]
        else:
            interval = data[start:start+length]
        
        if (len(interval) == 0):
            break
        
        intervals.append(interval)
        start += length
        length *= 2

    numchunks = min( len(intervals), numchunks )
    split = np.array_split(intervals, numchunks)
    for a in split:
        flat = [item for sublist in a for item in sublist]
        chunks.append(flat)
    
    return chunks
    
        

def freqToMel(freq):
    return 1127.01048 * math.log(1 + freq / 700.0)

def melToFreq(mel):
    return 700 * (math.exp(mel / 1127.01048 )-1)


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

minFreqIdx = 0;
maxFreqIdx = 0;

freqs = np.fft.rfftfreq(CHUNK, 1/RATE);
freqIdx = 0;
while freqIdx < len(freqs):
    freq = freqs[freqIdx]
    if (freq < minFreq):
        minFreqIdx = freqIdx
        
    if (freq < maxFreq):
        maxFreqIdx = freqIdx+1

    freqIdx += 1

freqs = freqs[minFreqIdx:maxFreqIdx];
for f in freqs:
    mel = freqToMel(f)
    print "%s, %s"%(f, mel)
# freqBands = []
# logBands = logChunks(freqs, 16)
# for a in logBands:
#     freqBands.append(int(a[0]))
    

# while True:
#     data = np.fromstring(stream.read(CHUNK), dtype=np.int16)
#     spectrum = np.fft.rfft(data)
#     spectrum = spectrum[minFreqIdx:maxFreqIdx]
#     bands = logChunks(spectrum, NUMBANDS)
#     
#     for i, b in enumerate(bands):
#         row = i+1
#         printPeak(b, row=row, freqs=freqBands)


stream.stop_stream()
stream.close()
p.terminate()
