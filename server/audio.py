import pyaudiowpatch as pyaudio
from flask import Flask
from aiohttp import web
import pyflac
import numpy as np
import queue
import struct
import lameenc

wav_queue = queue.SimpleQueue()
mp3_queue = queue.SimpleQueue()

app = Flask(__name__)

p = pyaudio.PyAudio()
# info = p.get_host_api_info_by_index(0)
# numdevices = info.get('deviceCount')

# for i in range(0, numdevices):
#     print(p.get_device_info_by_host_api_device_index(0, i))

#     if (p.get_device_info_by_host_api_device_index(0, i).get('maxOutputChannels')) > 0:
#         print("Input Device id ", i, " - ",
#               p.get_device_info_by_host_api_device_index(0, i).get('name'))

wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
print(wasapi_info)

default_speakers = p.get_device_info_by_index(
    wasapi_info["defaultOutputDevice"])
# print(default_speakers)

if not default_speakers["isLoopbackDevice"]:
    print("ee")
    for loopback in p.get_loopback_device_info_generator():
        """
        Try to find loopback device with same name(and [Loopback suffix]).
        Unfortunately, this is the most adequate way at the moment.
        """
        print(loopback)
        # if default_speakers["name"] in loopback["name"]:
        if 32== loopback["index"]:
            default_speakers = loopback
            break

print(default_speakers)

encoder = lameenc.Encoder()
encoder.set_bit_rate(64)
encoder.set_in_sample_rate(int(default_speakers["defaultSampleRate"]))
encoder.set_channels(2)
encoder.set_quality(7)

def callback(in_data, frame_count, time_info, status):
    data = in_data
    # print(frame_count, time_info, status)
    # If len(data) is less than requested frame_count, PyAudio automatically
    # assumes the stream is finished, and the stream stops.

    # print(data)
    # wav_queue.put(data)
    # print("receive data: ",end='')
    # print(data)

    data = np.frombuffer(data, dtype=np.int16)
    samples = data.reshape((len(data) // default_speakers["maxInputChannels"], default_speakers["maxInputChannels"]))
    mp3_queue.put(encoder.encode(samples)) 

    # wav_queue.put(in_data)
    return (in_data, pyaudio.paContinue)


async def mp3(request):
    print(mp3_queue.qsize())
    stream=p.open(format=pyaudio.paInt16,
            channels=default_speakers["maxInputChannels"],
            rate=int(default_speakers["defaultSampleRate"]),
            frames_per_buffer=pyaudio.get_sample_size(pyaudio.paInt16),
            input=True,
            input_device_index=default_speakers["index"],
            stream_callback=callback
            )
    response = web.StreamResponse()
    response.content_type = 'audio/mp3'
    
    await response.prepare(request)
    try:
        while True:
            await response.write(mp3_queue.get())
    except ConnectionResetError:
        print("connection reset")
        stream.close()
        return response

def mp32(request):
    response = web.Response()
    response.body=open(r"C:\repo\speaker-server\1.mp3",'rb').read()
    return response

app = web.Application()
app.add_routes([web.get('/1.mp3', mp3)])
app.add_routes([web.get('/2.mp3', mp32)])

# Close stream (4)
# stream.close()

# # Release PortAudio system resources (5)
# p.terminate()

if __name__ == "__main__":
    # app.run(debug=False, port=8080)
    web.run_app(app)
