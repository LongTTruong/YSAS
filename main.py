"""
    these comments are strictly for me lol
    idea -> load in any song/piece and play/sing along and receive score at end
    just like karaoke lol
    most important aspects are timing and pitch
    preserving timbre isn't super important for now, but we should still be mindful
    first order of business is essentially coding up a tuner
    don't worry abt speed rn.

    for preprocessing, we want to isolate just the frequencies that matter when we do perform ffts
    accordingly, we perform a lowpass filter in order to get rid of the underlying rumble
    we wouldnt perform a highpass filter in preprocessing because 1: higher frequency noise just isn't
    as common or intrusive as low frequency noise and 2: we will need those higher frequencies because they are essential
    characteristics in regards to timbre 

    
    
"""

import pyaudio
import numpy as np
import wave
from scipy.signal import butter, sosfilt

if __name__ == '__main__':
    #compare incoming audio to known values (A=440.0hz in relation C0, might be a bit inaccurate bc ratios rough at 4 sig figs)    
    NOTES = [
    ("C", 16.35), ("C#", 17.32), ("D", 18.35), ("D#", 19.45), ("E", 20.60),
    ("F", 21.83), ("F#", 23.12), ("G", 24.50), ("G#", 25.96), ("A", 27.50),
    ("A#", 29.14), ("B", 30.87)
]
    #audio stream parameters
    CHUNK = 4096
    FORMAT = pyaudio.paFloat32
    CHANNELS = 1
    SAMPLING_RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(
        format = FORMAT,
        channels = CHANNELS,
        rate = SAMPLING_RATE,
        input = True,
        frames_per_buffer = CHUNK
    )

    #again, 16.35hz = C0. for each x, there exists an infinite number of z such that 2**z == x
    def find_closest_note(frequency):
        octave = int(np.log2(frequency / 16.35))
        note_frequencies = [(note, freq * 2**octave) for note, freq in NOTES]
        closest_note = min(note_frequencies, key=lambda x : abs(x[1] - frequency))
        return closest_note
    
    def high_pass_filter(data, sample_rate, cutoff):
        """
        Applies high pass filter to the audio data. Butterworth filter.

        Params:
            data :  numpy.ndarray  => input-audio data (time-domain signal)
            sample_rate : int => sample rate in Hz
            cutoff_frequency : float => cutoff frequency of filter in Hz
        
        Returns:
            numpy.ndarray
        """
        sos = butter(
            4,
            Wn = cutoff / (0.5 * sample_rate),
            btype = 'highpass',
            output='sos'
        )
        filtered_audio = sosfilt(sos, data)
        return filtered_audio

    def band_pass_filter(data, sample_rate, low_cutoff, high_cutoff):
        """
        Applies a band pass filter to the audio data. Butterworth filter.

        Params:
            data :  numpy.ndarray  => input-audio data (time-domain signal)
            sample_rate : int => sample rate in Hz
            low_cutoff : float => low cutoff frequency in Hz
            high_cutoff : float => high cutoff frequency in Hz
        
        Returns:
            numpy.ndarray
        """
        sos = butter(
            4,
            [low_cutoff, high_cutoff],
            btype = 'band',
            fs = sample_rate,
            output='sos'
        )
        filtered_audio = sosfilt(sos, data)
        return filtered_audio

    def normalization(data):
        """
        Normalizes the audio data. this particular normalization technique is a simple Peak normalization

        Params:
            data : numpy.ndarray => input-audio data (time-domain signal)

        Returns:
            numpy.ndarray
        """
        max_amplitude = np.max(np.abs(data))

        if max_amplitude > 0:
            normalized_data = data / max_amplitude
        else:
            normalized_data = data
        return normalized_data

    print ("Recording! Press Ctrl+c to stop.")

    # main loop
    try:
        while True:
            data = stream.read(CHUNK, exception_on_overflow=False)
            
            #acquire the audio arrays from stream
            audio_data = np.frombuffer(data, dtype=np.float32)

            #preprocessing
            audio_data = high_pass_filter(audio_data, SAMPLING_RATE, 50)
            audio_data = normalization(audio_data)

            #band-pass filtering
            audio_data = band_pass_filter(audio_data, SAMPLING_RATE, 50, 5000)

            #Frequency-Domain analysis
            fft = np.fft.fft(audio_data)
            frequencies = np.fft.fftfreq(len(fft), d=1/SAMPLING_RATE)
            magnitudes = np.abs(fft)
            
            peak_index = np.argmax(magnitudes[:CHUNK // 2])
            peak_frequency = abs(frequencies[peak_index])

            if peak_frequency > 20:
                note, expected_freq  = find_closest_note(peak_frequency)
                deviation = peak_frequency - expected_freq
                print(f"Frequency: {peak_frequency:.2f} Hz, Note: {note}, Deviation: {deviation:+.4f} Hz")

    except KeyboardInterrupt:
        print('\nexited!')
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()
