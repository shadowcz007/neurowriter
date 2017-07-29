
# coding: utf-8

# Module for generating written text using a pretrained model
#
# @author Álvaro Barbero Jiménez

import numpy as np
import itertools

from neurowriter.encoding import NULL

class Writer():
    # Keras model to use for generation
    model = None
    # Character encoder used
    encoder = None
    # Creativity rate (probability temperature)
    creativity = None
    
    def __init__(self, model, encoder, creativity=0.5):
        """Creates a writer using a pretrained model"""
        self.model = model
        self.encoder = encoder
        self.creativity = creativity
        
    def write(self, seed=[], length=1000):
        """Start writing characters
        
        Arguments:
            seed: list of tokens to initialize generation
            length: length of the generated text
            
        Return the generated text.
        """        
        # Iterate generation
        return itertools.islice(self.generate(seed), length)
    
    def generate(self, seed=[]):
        """Infinite generator of text following the Writer style.
        
        Arguments:
            seed: list of tokens to initialize generation
        
        Returns one piece of text at a time.
        """
        # Prepare seed
        inputtokens = self.model.layers[0].input_shape[1]
        if len(seed) < inputtokens:
            seed = [NULL] * (inputtokens-len(seed)) + seed
        seedcoded = self.encoder.encodetext(seed[-inputtokens:])
        
        # Iterate generation
        while True:
            # Predict token probabilities using model
            pred = self.model.predict(
                np.array([seedcoded]), 
                verbose=0
            )
            # Apply creativity
            maxoutput = sample(pred.squeeze(), temperature=self.creativity)
            newtoken = self.encoder.index2char[maxoutput]
            # Drop oldest token, add new one
            seedcoded = np.vstack((seedcoded[1:], self.encoder.encodetext([newtoken])))
            yield newtoken
            
def normalize(probs):
    """Normalizes a list of probabilities, so that they sum up to 1"""
    prob_factor = 1 / sum(probs)
    return [prob_factor * p for p in probs]
    
def sample(a, temperature=1.0):
    a = np.exp(np.log(a) / temperature)
    a = normalize(a)
    return np.argmax(np.random.multinomial(1, a, 1))