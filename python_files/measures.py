import measpy as mp
from measpy.audio import audio_run_measurement
import time

def simulateMeasure():
    print("doing a measurement...")
    time.sleep(3)
    print("measurement ended !")

def simpleMeasure():
    sout = mp.Signal.noise(fs=44100, freq_min=20, freq_max=20000, dur=5)
    sin1 = mp.Signal(desc = 'Pressure', dbfs=5.0, cal=1.0, unit="Pa")
    sin2 = mp.Signal(desc = 'Acceleration', dbfs=5.0, cal=0.1, unit="m*s**(-2)")

    M1 = mp.Measurement(
        out_sig = [sout],
        out_map = [1],
        in_sig = [sin1,sin2],
        in_map = [1,2],
        dur = 5,
        device_type = 'audio'
    )

    audio_run_measurement(M1)
