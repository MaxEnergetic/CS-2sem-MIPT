# Simple Autotune Implementation (FFT-based)

import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import resample


sample_rate, audio = wavfile.read('voice.wav')


if len(audio.shape) > 1:
    audio = audio.mean(axis=1)

audio = audio.astype(np.float32)

print("Sample rate:", sample_rate)
print("Audio length:", len(audio))

frame_size = int(0.03 * sample_rate)  
hop_size = frame_size // 2

def detect_pitch(frame, sample_rate):
    frame = frame - np.mean(frame)
    corr = np.correlate(frame, frame, mode='full')
    corr = corr[len(corr)//2:]


    min_lag = int(sample_rate / 1000)  
    max_lag = int(sample_rate / 80)   

    corr[:min_lag] = 0
    if max_lag < len(corr):
        corr[max_lag:] = 0

    peak = np.argmax(corr)
    if peak == 0:
        return 0

    return sample_rate / peak


def nearest_note_freq(freq):
    if freq <= 0:
        return freq
    n = 12 * np.log2(freq / 440.0)
    n_rounded = np.round(n)
    return 440.0 * (2 ** (n_rounded / 12))

def pitch_shift(frame, ratio):
    if ratio == 0 or np.isnan(ratio) or np.isinf(ratio):
        return frame
    new_len = int(len(frame) / ratio)
    if new_len < 1:
        return frame
    shifted = resample(frame, new_len)
    shifted = resample(shifted, len(frame))
    return shifted

output = np.zeros_like(audio)
window = np.hanning(frame_size)

pitch_curve = []

for i in range(0, len(audio) - frame_size, hop_size):
    frame = audio[i:i+frame_size] * window

    freq = detect_pitch(frame, sample_rate)
    target = nearest_note_freq(freq)

    if freq > 0:
        ratio = target / freq
    else:
        ratio = 1

    shifted = pitch_shift(frame, ratio)

    output[i:i+frame_size] += shifted * window
    pitch_curve.append(freq)

output = output / np.max(np.abs(output))

wavfile.write("autotuned.wav", sample_rate, (output * 32767).astype(np.int16))

print("Saved autotuned.wav")

plt.plot(pitch_curve)
plt.title("Detected Pitch Over Time")
plt.xlabel("Frame")
plt.ylabel("Frequency (Hz)")
plt.show()

final_output = (output * 32767).astype(np.int16)

wavfile.write("audio.wav", sample_rate, final_output)

print("Saved audio.wav")
