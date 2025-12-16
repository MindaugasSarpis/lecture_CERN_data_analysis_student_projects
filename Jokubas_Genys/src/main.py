import numpy as np
from scipy import signal
import librosa
from pathlib import Path
import soundfile as sf
import os
import pyroomacoustics as pra
import matplotlib.pyplot as plt


SAMPLE_RATE = 48000 # all files resampled to this rate
IR_PATH = os.path.join(os.getcwd(), 'data', 'impulse_responses') # impulse response path
SOURCE_PATH = os.path.join(os.getcwd(), 'data', 'sounds') # input sound path
RESULT_PATH = os.path.join(os.getcwd(), 'results')
LOCATIONS = ('corridor', 'dormroom', 'kitchen', 'shower', 'toilet') # must be in order of the files in IR_PATH
IR_COUNT = 4 # count of how many impulse responses there are per location (must be the same for each room) 

def energy_ratio(data, sample_rate, window_length = 0.05, onset = 0):
    """
    Calculates the energy ratio of an impulse response's early (onset til window_length) and 
    late (onset + window_length til the end) reverberations
    
    :param data: floating point time series of signal to be analyzed (usually float32 numpy array)
    :param sample_rate: sample rate of signal
    :param window_length: in seconds, the cutoff point between the first part and the second part of the signal to be analyzed,
    for example if window_length = 0.01, then the energy ratio is calculated between the first 10ms of the signal and the rest
    :param onset: in seconds, the start of the signal to be analyzed, for example if there is silence before the signal,
    it may be truncated by selecting an apt onset value
    """

    energy = data ** 2
    window_samples = int(window_length * sample_rate)
    return 10 * np.log10(np.sum(energy[onset : onset + window_samples] / np.sum(energy[onset + window_samples :])))

def spectral_centroid(data, sample_rate):
    """
    Calculates (a single value) POWER spectral centroid of an impulse response using the OpenAE standard
    
    :param data: floating point time series of signal to be analyzed (usually float32 numpy array)
    :param sample_rate: sample rate of signal
    """

    power = np.abs(np.fft.rfft(data)) ** 2
    bins = np.arange(len(power))
    conversion_factor = (sample_rate / (2 * (len(bins) - 1)))
    return conversion_factor * (np.sum(bins * power) / np.sum(power))

def gather_feature_data(feature_dict, locations, ir_count):
    data = []
    for loc in locations:
        vals = [v for k,v in feature_dict.items() if loc in k]
        data.append(vals)
    return data


def main():
    if not os.path.exists(RESULT_PATH):
        os.mkdir(RESULT_PATH)

    # impulse responses
    irs = {}

    # features
    # rt60: time in seconds for an impulse response to become quieter by 60 dB
    # drr: direct to reverberent energy ratio - energy ratio with window of 10 ms
    # c80: clarity for musical performances - energy ratio with window of 80 ms
    # sc: spectral centroid - here it is calulated as a single value power spectral centroid using the OpenAE standard
    features = {
            'rt60' : {},
            'drr' : {},
            'c80' : {},
            'sc' : {}
            }
    
    files = librosa.util.find_files(IR_PATH)
    for path in files:
        y, sr = librosa.load(path, sr = SAMPLE_RATE)
        y /= max(abs(y)) # normalize
        file_stem = Path(path).stem
        irs[file_stem] = y   

        features['rt60'][file_stem] = pra.experimental.rt60.measure_rt60(y, fs = SAMPLE_RATE)
        features['drr'][file_stem] = energy_ratio(y, SAMPLE_RATE, 0.01)
        features['c80'][file_stem] = energy_ratio(y, SAMPLE_RATE, 0.08)
        features['sc'][file_stem] = spectral_centroid(y, SAMPLE_RATE)

    
    rt60_data = gather_feature_data(features['rt60'], LOCATIONS, IR_COUNT)
    drr_data  = gather_feature_data(features['drr'], LOCATIONS, IR_COUNT)
    c80_data  = gather_feature_data(features['c80'], LOCATIONS, IR_COUNT)
    sc_data   = gather_feature_data(features['sc'], LOCATIONS, IR_COUNT)

    plt.figure()
    plt.boxplot(rt60_data, tick_labels=LOCATIONS)
    plt.ylabel('RT60 (s)')
    plt.title('RT60 per Location')
    plt.grid(True)
    plt.savefig(os.path.join(RESULT_PATH, 'rt60_boxplot.png'), dpi=300, bbox_inches='tight')

    plt.figure()
    plt.boxplot(drr_data, tick_labels=LOCATIONS)
    plt.ylabel('DRR (dB)')
    plt.title('DRR per Location')
    plt.grid(True)
    plt.savefig(os.path.join(RESULT_PATH, 'drr_boxplot.png'), dpi=300, bbox_inches='tight')

    plt.figure()
    plt.boxplot(c80_data, tick_labels=LOCATIONS)
    plt.ylabel('C80 (dB)')
    plt.title('C80 per Location')
    plt.grid(True)
    plt.savefig(os.path.join(RESULT_PATH, 'c80_boxplot.png'), dpi=300, bbox_inches='tight')

    plt.figure()
    plt.boxplot(sc_data, tick_labels=LOCATIONS)
    plt.ylabel('Spectral Centroid (Hz)')
    plt.title('Spectral Centroid per Location')
    plt.grid(True)
    plt.savefig(os.path.join(RESULT_PATH, 'sc_boxplot.png'), dpi=300, bbox_inches='tight')

    sources = {}
    files = librosa.util.find_files(SOURCE_PATH)
    for path in files:
        y, sr = librosa.load(path, sr = SAMPLE_RATE)
        y /= max(abs(y)) # normalize
        sources[Path(path).stem] = y

    for name_input, input in sources.items():
        result_dir = os.path.join(RESULT_PATH, name_input)
        if not os.path.exists(result_dir):
            os.mkdir(result_dir)

        for name_ir, ir in irs.items():      
            conv_sig = signal.convolve(input, ir) # convolved signal
            conv_sig /= max(abs(conv_sig)) # normalize so audio doesn't clip

            file_name = os.path.join(result_dir, name_input + '+' + name_ir + '.wav')
            sf.write(file_name, conv_sig, SAMPLE_RATE, format = 'wav', subtype = 'PCM_24')


if __name__ == "__main__":
    main()
