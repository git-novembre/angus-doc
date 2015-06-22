#!/usr/bin/env python
# -*- coding: utf-8 -*-

import Queue
import StringIO
import wave

import angus.cloud
import pyaudio

CHUNK = 512
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
RECORD_SECONDS = 2
INDEX = 3  # USB Cam
WAVE_OUTPUT_FILENAME = "output.wav"

p = pyaudio.PyAudio()

print p.get_default_host_api_info()
print
print
print p.get_device_info_by_host_api_device_index(0, INDEX)
print
print

conn = angus.connect()

service = conn.services.get_service('sound_detection', version=1)

stream_queue = Queue.Queue()


def callback(in_data, frame_count, time_info, status):
    stream_queue.put(in_data)
    return (in_data, pyaudio.paContinue)

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                frames_per_buffer=CHUNK,
                input_device_index=INDEX,
                stream_callback=callback)


print("* recording")
stream.start_stream()

while(True):
    frames = []

    for i in range(RATE / CHUNK / 2):
        data = stream_queue.get()
        frames.append(data)

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    job = service.process({'sound': open(WAVE_OUTPUT_FILENAME)})

    print job.result


stream.stop_stream()
print("* done recording")

stream.close()
p.terminate()