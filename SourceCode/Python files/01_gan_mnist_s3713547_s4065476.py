# -*- coding: utf-8 -*-
"""GAN_MNIST.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1c5rJBeDa4wVsiy6VeRBFXrXgUPMkL7Bx
"""

gpu_info = !nvidia-smi
gpu_info = '\n'.join(gpu_info)
if gpu_info.find('failed') >= 0:
  print('Select the Runtime → "Change runtime type" menu to enable a GPU accelerator, ')
  print('and then re-execute this cell.')
else:
  print(gpu_info)

#Required to save output
from google.colab import drive
drive.mount('/content/drive')

## Implementation of GAN
#1. Importing required packages
from keras.datasets import mnist
from keras.layers import Input, Dense, Reshape, Flatten
from keras.layers import BatchNormalization
from keras.layers.advanced_activations import LeakyReLU, ReLU
from keras.models import Sequential, Model
from keras.optimizers import Adam
import matplotlib.pyplot as plt
import numpy as np

#2. Constructing GAN class that contains the model for the discriminator and generator
class MNISTGAN():
  def __init__(self):
    self.img_shape = (28, 28, 1)
    self.noise_dimension = 64
    self.discriminator = self.build_discriminator()
    self.discriminator.compile(loss='binary_crossentropy',
                                optimizer=Adam(0.0002, 0.5),
                                metrics=['accuracy'])
    self.generator = self.build_generator()
    z = Input(shape=(self.noise_dimension,))
    img = self.generator(z)
    self.discriminator.trainable = False
    validity = self.discriminator(img)
    self.combined = Model(z, validity)
    self.combined.compile(loss='binary_crossentropy', optimizer= Adam(0.0001, 0.5))

  #3. Setting up generator model
  def build_generator(self):
      model = Sequential()
      momentum = 0.8
      model.add(Dense(256, input_dim=self.noise_dimension))
      model.add(LeakyReLU(alpha=0.2))
      model.add(BatchNormalization(momentum=momentum))
      model.add(Dense(512))
      model.add(LeakyReLU(alpha=0.2))
      model.add(BatchNormalization(momentum=momentum))
      model.add(Dense(1024))
      model.add(LeakyReLU(alpha=0.2))
      model.add(BatchNormalization(momentum=momentum))
      model.add(Dense(np.prod(self.img_shape), activation='tanh'))
      model.add(Reshape(self.img_shape))
      input_noise = Input(shape=(self.noise_dimension,))
      img = model(input_noise)
      model.summary()
      return Model(input_noise, img)

  #4. Setting up discriminator model
  def build_discriminator(self):
      model = Sequential()
      model.add(Flatten(input_shape=self.img_shape))
      model.add(Dense(512))
      model.add(LeakyReLU(alpha=0.2))
      model.add(Dense(256))
      model.add(LeakyReLU(alpha=0.2))
      model.add(Dense(1, activation='sigmoid'))
      img = Input(shape=self.img_shape)
      validity = model(img)
      model.summary()
      return Model(img, validity)

  #5. Defining the training parameters
  def train(self, epochs, batch_size=128, sample_interval=1000):
      '''
      Usage documentation can be found here: https://www.tensorflow.org/api_docs/python/tf/keras/datasets/mnist/load_data
      Since this is a unsupervised learning and we wanted only the training images, we ignored to load other x_test, y_train and y_test.
      '''
      (X_train, _), (_, _) = mnist.load_data(path="mnist.npz")
      X_train = X_train / 127.5 - 1.
      X_train = np.expand_dims(X_train, axis=3)
      valid = np.ones((batch_size, 1))
      fake = np.zeros((batch_size, 1))
      for epoch in range(epochs):
          idx = np.random.randint(0, X_train.shape[0], batch_size)
          imgs = X_train[idx]
          input_noise = np.random.normal(0, 1, (batch_size, self.noise_dimension))
          g_loss = self.combined.train_on_batch(input_noise, valid)
          gen_imgs = self.generator.predict(input_noise)
          d_loss_real = self.discriminator.train_on_batch(imgs, valid)
          d_loss_fake = self.discriminator.train_on_batch(gen_imgs, fake)
          d_loss = 0.5 * np.add(d_loss_real, d_loss_fake)
          print("%d [D loss: %f, acc.: %.2f%%] [G loss: %f]" % (epoch, d_loss[0], 100 * d_loss[1], g_loss))
          if epoch % sample_interval == 0:
            self.generate_numbers(epoch)

  #6. Generating new numbers at given sample interval		
  def generate_numbers(self, epoch):
      input_noise = np.random.normal(0, 1, (1, gan.noise_dimension))
      predictions = gan.generator.predict(input_noise)
      print(predictions.shape)
      print("Reshaping")
      generated_seq = np.reshape(predictions[0], (28,28))
      print(generated_seq.shape)
      plt.figure(figsize = (5,5))
      plt.imshow(generated_seq,aspect='auto',cmap='gray')
      #Path to be created in Google Drive to avoid failure
      plt.savefig("/content/drive/My Drive/DL/GAN/Results/GAN_MNIST/%d.png" % epoch)
      plt.show()
      plt.close()

#7. Running both the models with specified epochs, batch size and sample intervals (to less generated samples, the sample_interval size should be increased)
gan = MNISTGAN()
gan.train(epochs=50000, batch_size=32, sample_interval=1000)