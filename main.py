import argparse
from audio_read import read_real_time_audio
from audio_utils import audio_fft, frequency_to_note

if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-headless', action='store_true', help='Use command line instead of GUI')
    args = arg_parser.parse_args()

    audio_generator = read_real_time_audio()
    for sample_rate, signal in audio_generator:
        _, _, _, loudest_frequency, loudest_frequency_amplitude = audio_fft(signal, sample_rate)
        closest_frequency, closest_note = frequency_to_note(loudest_frequency, loudest_frequency_amplitude)
        tune_direction = None

        if args.headless:
            if closest_frequency is not None and closest_note is not None:
                if abs(loudest_frequency - closest_frequency) > 0.5:
                    if loudest_frequency < closest_frequency:
                        tune_direction = '↑'
                    else:
                        tune_direction = '↓'
                else:
                    tune_direction = '✓'

                print(
                    str(loudest_frequency) + 'Hz (' + str(closest_note) + ') ' + tune_direction)
        else:
            print('GUI not yet supported!')
            break

    audio_generator.close()
