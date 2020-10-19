from pathlib import Path

import tensorflow as tf

from utils.audio import Audio
from utils.display import tight_grid, buffer_image, gen_plot
from utils.vec_ops import norm_tensor
from utils.decorators import ignore_exception


def control_frequency(f):
    def apply_func(*args, **kwargs):
        # args[0] is self
        plot_all = ('plot_all' in kwargs) and kwargs['plot_all']
        if (args[0].global_step % args[0].plot_frequency == 0) or plot_all:
            result = f(*args, **kwargs)
            return result
        else:
            return None
    
    return apply_func


class SummaryManager:
    """ Writes tensorboard logs during training.
    
        :arg model: model object that is trained
        :arg log_dir: base directory where logs of a config are created
        :arg config: configuration dictionary
        :arg max_plot_frequency: every how many steps to plot
    """
    
    def __init__(self,
                 model: tf.keras.models.Model,
                 log_dir: str,
                 config: dict,
                 max_plot_frequency=10,
                 default_writer='log_dir'):
        self.model = model
        self.log_dir = Path(log_dir)
        self.config = config
        self.audio = Audio(config)
        self.plot_frequency = max_plot_frequency
        self.default_writer = default_writer
        self.writers = {}
        self.add_writer(tag=default_writer, path=self.log_dir, default=True)
    
    def add_writer(self, path, tag=None, default=False):
        """ Adds a writer to self.writers if the writer does not exist already.
            To avoid spamming writers on disk.
            
            :returns the writer on path with tag tag or path
        """
        if not tag:
            tag = path
        if tag not in self.writers.keys():
            self.writers[tag] = tf.summary.create_file_writer(str(path))
        if default:
            self.default_writer = tag
        return self.writers[tag]
    
    @property
    def global_step(self):
        return self.model.step
    
    def add_scalars(self, tag, dictionary, step=None):
        if step is None:
            step = self.global_step
        for k in dictionary.keys():
            with self.add_writer(str(self.log_dir / k)).as_default():
                tf.summary.scalar(name=tag, data=dictionary[k], step=step)
    
    def add_scalar(self, tag, scalar_value, step=None):
        if step is None:
            step = self.global_step
        with self.writers[self.default_writer].as_default():
            tf.summary.scalar(name=tag, data=scalar_value, step=step)
    
    def add_image(self, tag, image, step=None):
        if step is None:
            step = self.global_step
        with self.writers[self.default_writer].as_default():
            tf.summary.image(name=tag, data=image, step=step, max_outputs=4)
    
    def add_histogram(self, tag, values, buckets=None):
        with self.writers[self.default_writer].as_default():
            tf.summary.histogram(name=tag, data=values, step=self.global_step, buckets=buckets)
    
    def add_audio(self, tag, wav, sr, step=None):
        if step is None:
            step = self.global_step
        with self.writers[self.default_writer].as_default():
            tf.summary.audio(name=tag,
                             data=wav,
                             sample_rate=sr,
                             step=step)
    
    @ignore_exception
    def display_attention_heads(self, outputs, tag='', step=None):
        if step is None:
            step = self.global_step
        for layer in ['encoder_attention', 'decoder_attention']:
            for k in outputs[layer].keys():
                image = tight_grid(norm_tensor(outputs[layer][k][0]))
                # dim 0 of image_batch is now number of heads
                batch_plot_path = f'{tag}/{layer}/{k}'
                self.add_image(str(batch_plot_path), tf.expand_dims(tf.expand_dims(image, 0), -1), step=step)
    
    @ignore_exception
    def display_mel(self, mel, tag='', step=None):
        if step is None:
            step = self.global_step
        img = tf.transpose(mel)
        figure = self.audio.display_mel(img, is_normal=True)
        buf = buffer_image(figure)
        img_tf = tf.image.decode_png(buf.getvalue(), channels=3)
        self.add_image(tag, tf.expand_dims(img_tf, 0), step=step)
    
    @ignore_exception
    def display_image(self, image, with_bar=False, figsize=None, tag='', step=None):
        if step is None:
            step = self.global_step
        buf = gen_plot(image, with_bar=with_bar, figsize=figsize)
        image = tf.image.decode_png(buf.getvalue(), channels=4)
        image = tf.expand_dims(image, 0)
        self.add_image(tag=tag, image=image, step=step)
    
    @control_frequency
    @ignore_exception
    def display_loss(self, output, tag='', plot_all=False, step=None):
        if step is None:
            step = self.global_step
        self.add_scalars(tag=f'{tag}/losses', dictionary=output['losses'], step=step)
        self.add_scalar(tag=f'{tag}/loss', scalar_value=output['loss'], step=step)
    
    @control_frequency
    @ignore_exception
    def display_scalar(self, tag, scalar_value, plot_all=False, step=None):
        if step is None:
            step = self.global_step
        self.add_scalar(tag=tag, scalar_value=scalar_value, step=step)
    
    @ignore_exception
    def display_audio(self, tag, mel, step=None):
        wav = tf.transpose(mel)
        wav = self.audio.reconstruct_waveform(wav)
        wav = tf.expand_dims(wav, 0)
        wav = tf.expand_dims(wav, -1)
        self.add_audio(tag, wav.numpy(), sr=self.config['sampling_rate'], step=step)
