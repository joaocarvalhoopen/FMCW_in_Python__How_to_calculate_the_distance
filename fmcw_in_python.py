import matplotlib.pyplot as plt
import numpy as np
from scipy import signal
import scipy.fftpack
from scipy.fft import fft, ifft
from scipy.signal import find_peaks

# t -- time
# s -- samples

SOUND_VELOCITY = 320 # m/s
SAMPLE_RATE = 44100

def generate_chirp(sample_rate, chirp_duration, start_freq, end_freq):
    f_0 = start_freq
    f_1 = end_freq
    start = 0.0
    stop = chirp_duration
    step = 1.0 / sample_rate
    t = np.arange(start, stop, step, dtype='float')
    phase = 0.0
    chirp_period = chirp_duration # 1 / 100.0 #1.0
    k = (f_1 - f_0) / chirp_period
    s = np.sin(phase + 2*np.pi * ( f_0*t + (k/2)*np.square(t)) )
    len_s = s.size
    return (t, s, len_s)

def plot_chirp(t, s, start_freq, end_freq):
    plt.plot(t, s)

    plt.xlabel('time (s)')
    plt.ylabel('amplitude')
    plt.title('chirp  from ' + str(start_freq) + 'Hz  to ' + str(end_freq) + 'Hz' )
    plt.grid(True)
    #plt.savefig("test.png")
    plt.show()

def compute_cepstrum(xs):
    a = np.absolute(fft(xs))
    print("a")
    print(a)
    b = np.log(a)
    print("b")
    print(b)
    c = ifft(b)
    print("c")
    print(c)
    cepstrum = np.abs(c)
    return cepstrum

def get_distance_to_the_target(num_samples, sample_rate):
    time = num_samples / sample_rate
    distance_to_the_target = (time / 2) * SOUND_VELOCITY
    return distance_to_the_target

def distance_to_delta_sample_between_send_and_receive(distance_meters, sample_rate):
    num_samples = ((distance_meters / SOUND_VELOCITY) * sample_rate) * 2
    return int(num_samples)   

if __name__ == "__main__":

    # start_freq = 5
    start_freq = 20

    # end_freq   = 50 # 1000
    end_freq  = 20000

    # chirp_duration = 0.010
    chirp_duration = 1.00

    # Generate one chirp.
    t, s, len_s = generate_chirp(SAMPLE_RATE, chirp_duration, start_freq, end_freq)

    plot_chirp(t, s, start_freq, end_freq)

    # Super-impose 2 copies of the chirp delayed,
    # simulating the send audio signal and receive smaller audio signal.
    
    # delta_in_samples = int(len_s / 3.0) # 5.0
    # delta_in_samples = int(2000)
    
    distance_meters = 50 # From 1 to 50 meters, other values has to reset the threshold.
    delta_in_samples = distance_to_delta_sample_between_send_and_receive(distance_meters, SAMPLE_RATE)
    
    # delta_in_samples = int(5000)
    buf_send_and_receive = np.zeros(len_s + delta_in_samples, dtype='float')
    print("\n\n")
    print(s)
    print("\n\n")
    print(buf_send_and_receive)
    print("\n\n")
    buf_send_and_receive[0:len_s] = s
    buf_send_and_receive[0 + delta_in_samples: ] += s * 0.2

    amp = 1
    # Do a SFFT to see the two ramps of different intensities.
    f, t, Zxx = signal.stft(buf_send_and_receive, SAMPLE_RATE, nperseg=100)
    plt.pcolormesh(t, f, np.abs(Zxx), vmin=0, vmax=amp, shading='gouraud')
    plt.title('STFT Magnitude')
    plt.ylabel('Frequency [Hz]')
    plt.xlabel('Time [sec]')
    plt.show()


    # Cepstrum
    buf_send_and_receive = compute_cepstrum(buf_send_and_receive)


    len_cepstrum = buf_send_and_receive.shape[-1] // 2

    # Filter out the DC component for the find_peaks and the negative frequencies part of the spectrum of the IFFT. 
    dc_component_first_buckets = 100
    x = buf_send_and_receive[dc_component_first_buckets:len_cepstrum]

    peaks, _ = find_peaks(x, height=0.005)

    print("peaks")
    print(peaks)

    plt.plot(x)
    plt.plot(peaks, x[peaks], "x")
    plt.plot(np.zeros_like(x), "--", color="gray")
    plt.show()

    delta_in_frequency = np.abs((peaks[0] + dc_component_first_buckets) - (peaks[1] + dc_component_first_buckets))

    print("delta_in_frequency")
    print(delta_in_frequency)

    num_samples = delta_in_frequency
    distance_calculated = get_distance_to_the_target(num_samples, SAMPLE_RATE)
    

    print("Real distance to target:")
    print(distance_meters)
 
    print("Distance calculated to the target:")
    print(distance_calculated)
 

    print("peaks")
    print(peaks)

    print("Cepstrum")
    print(buf_send_and_receive)

    N = buf_send_and_receive.shape[-1] # Sample points
    T = 1.0 / N # Sample spacing
    x = np.linspace(0.0, N*T, N)
    y = buf_send_and_receive
    
    # yf = scipy.fftpack.fft(y)
    
    # Cepstrum
    yf = buf_send_and_receive
    
    xf = np.linspace(0.0, 1.0/(2.0*T), N//2)

    fig, ax = plt.subplots()
    ax.plot(xf, 2.0/N * np.abs(yf[:N//2]))
    plt.show()








