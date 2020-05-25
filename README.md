<p align="center">
    <br>
    <img src="https://raw.githubusercontent.com/as-ideas/TransformerTTS/master/docs/transformer_logo.png" width="400"/>
    <br>
</p>

<h2 align="center">
<p>A Text-to-Speech Transformer in TensorFlow 2</p>
</h2>

Implementation of a non-autoregressive Transformer based neural network for Text-to-Speech (TTS). <br>
This repo is based on the following papers:
- [Neural Speech Synthesis with Transformer Network](https://arxiv.org/abs/1809.08895)
- [FastSpeech: Fast, Robust and Controllable Text to Speech](https://arxiv.org/abs/1905.09263)

Spectrograms produced with LJSpeech and standard data configuration from this repo are compatible with [WaveRNN](https://github.com/fatchord/WaveRNN).

## 🔈 Samples

[Can be found here.](https://as-ideas.github.io/TransformerTTS/)<br>
These samples' spectrograms are converted using the pre-trained [WaveRNN](https://github.com/fatchord/WaveRNN) vocoder.<br>

The TTS weights used for these samples can be found [here](https://github.com/as-ideas/tts_model_outputs/tree/master/ljspeech_transformertts).

Check out the notebooks folder for predictions with TransformerTTS and WaveRNN.

## 📖 Contents
- [Installation](#installation)
- [Dataset](#dataset)
- [Training](#training)
    - [Autoregressive](#train_autoregressive_model)
    - [Forward](#train_forward_model)
- [Prediction](#prediction)

## Installation

Make sure you have:

* Python >= 3.6

Install espeak as phonemizer backend (for macOS use brew):
```
sudo apt-get install espeak
```

Then install the rest with pip:
```
pip install -r requirements.txt
```

Read the individual scripts for more command line arguments.

## Dataset
You can directly use [LJSpeech](https://keithito.com/LJ-Speech-Dataset/) to create the training dataset.

#### Configuration
* If training LJSpeech, or if unsure, simply use ```config/standard```
* **EDIT PATHS**: in `data_config.yaml` edit the paths to point at your dataset and log folders

#### Custom dataset
Prepare a dataset in the following format:
```
|- dataset_folder/
|   |- metadata.csv
|   |- wav/
|       |- file1.wav
|       |- ...
```
where `metadata.csv` has the following format:
``` wav_file_name|transcription ```

## Training
### Train Autoregressive Model
#### Create training dataset
```bash
python create_dataset.py --config config/standard
```
#### Training
```bash
python train.py --config config/standard
```
### Train Forward Model
#### Compute alignment dataset
First use the autoregressive model to create the durations dataset
```bash
python extract_durations.py --config config/standard  --binary --fix_jumps --fill_mode_next
```
this will add an additional folder to the dataset folder containing the new datasets for validation and training of the forward model.<br>
If the rhythm of the trained model is off, play around with the flags of this script to fix the durations.
#### Training
```bash
python train_forward.py  --config /path/to/config_folder/
```
#### Training & Model configuration
- Training and model settings can be configured in `model_config.yaml`

#### Resume or restart training
- To resume training simply use the same configuration files AND `--session_name` flag, if any
- To restart training, delete the weights and/or the logs from the logs folder with the training flag `--reset_dir` (both) or `--reset_logs`, `--reset_weights`

#### Monitor training
We log some information that can be visualized with TensorBoard:
```bash
tensorboard --logdir /logs/directory/
```

## Prediction
Predict with either the Forward or AutoRegressive model
```python
from utils.config_manager import ConfigManager
from utils.audio import reconstruct_waveform

config_loader = ConfigManager('/path/to/config/', model_kind='forward')
model = config_loader.load_model()
out = model.predict('Please, say something.')

# Convert spectrogram to wav (with griffin lim)
wav = reconstruct_waveform(out['mel'].numpy().T, config=config_loader.config)
```

## Maintainers
* Francesco Cardinale, github: [cfrancesco](https://github.com/cfrancesco)

## Special thanks
[WaveRNN](https://github.com/fatchord/WaveRNN): we took the data processing from here and use their vocoder to produce the samples. <br>
[Erogol](https://github.com/erogol): for the lively exchange on TTS topics. <br>

## Copyright
See [LICENSE](LICENSE) for details.
