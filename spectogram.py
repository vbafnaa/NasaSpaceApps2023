import librosa
import librosa.display
import matplotlib.pyplot as plt

audio_file_path = 'rms.wav'
audio_data, sample_rate = librosa.load(audio_file_path, sr=None)
plt.figure(figsize=(10, 4))
D = librosa.amplitude_to_db(np.abs(librosa.stft(audio_data)), ref=np.max)
librosa.display.specshow(D, sr=sample_rate, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Spectrogram')
plt.tight_layout()
plt.show()