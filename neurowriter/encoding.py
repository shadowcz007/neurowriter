
# coding: utf-8

# Module for character encoding/decoding operations
#
# @author Álvaro Barbero Jiménez

import numpy as np
from itertools import chain
import pickle as pkl

from neurowriter.genutils import batchedgenerator, infinitegenerator
from neurowriter.tokenizer import tokenizerbyname

# Start sequence special character
START = "<START>"
# End sequence special character
END = "<END>"
# Null value in sequence special character
NULL = "<NULL>"
# Dictionary of all special characters
SPCHARS = [NULL, START, END]

class Encoder():
    # Dictionary of chars to numeric indices
    char2index = None    
    # Dictionary of numeric indices to chars
    index2char = None
    # Tokenizer used to process text
    tokenizer = None
    
    def __init__(self, corpus=None, tokenizer="char"):
        """Creates an encoder from tokens to numbers and viceversa

        The encoder is built to represent all tokens present in the
        given corpus of texts, plus some special tokens for padding
        and sequence start/end. The special tokens are always codified
        as the first numbers, so that meaning is the same throughout
        different corpus.

        Arguments
            corpus: iterable of strings
            tokenizer: method used to split the corpus into tokens. Can be:
                - 'char': one token per character
                - 'word': one token per word
        """
        if corpus is not None:
            # Train tokenizer on corpus
            self.tokenizer = tokenizerbyname(tokenizer)()
            self.tokenizer.fit(corpus)
            # Get unique tokens from data
            #chars = set([letter for text in corpus for letter in text])
            tokens = set([token for token in self.tokenizer.transform(corpus)])
            print('Total tokens:', len(tokens) + len(SPCHARS))
            self.char2index = dict((c, i) for i, c in enumerate(chain(SPCHARS ,tokens)))
            self.index2char = dict((i, c) for i, c in enumerate(chain(SPCHARS ,tokens)))

    def encodetext(self, text, addstart=False, fixlength=None):
        """Transforms a single text to tensor representation
        
        An special START character is added at the beginning to mark the start,
        if requested.
    
        If the fixlength parameter is provided, NULL characters are added
        at the beginning until such length is met.    
        """
        # Tokenize text
        tokens = self.tokenizer.transform(text)
        return self.encodetokens(tokens, addstart, fixlength)
    
    def encodetokens(self, tokens, addstart=False, fixlength=None):
        """Transforms a list of tokens to tensor representation
        
        An special START token is added at the beginning to mark the start,
        if requested.
    
        If the fixlength parameter is provided, NULL token are added
        at the beginning until such length is met.    
        """
        ln = len(tokens) + (1 if addstart else 0)
        X = np.zeros((ln, len(self.char2index)))
        if addstart:
            X[0, self.char2index[START]] = 1
            offset = 1
        else:
            offset = 0
        for t, token in enumerate(tokens):
            if token in self.char2index:
                X[offset + t, self.char2index[token]] = 1
            else:
                print("WARNING: token", token, "not recognized")
    
        # Null padding, if requested            
        if fixlength is not None:
            Xfix = np.zeros((fixlength, len(self.char2index)))
            for i in range(min(ln,fixlength)):
                Xfix[-i] = X[-i]
            for i in range(ln, fixlength):
                Xfix[-i, self.char2index[NULL]] = 1
            X = Xfix
            
        return X
        
    def decodetext(self, X):
        """Transforms a matrix representing a text into text form
        
        Special characters are ignored"""
        text = ""
        for elem in X:
            char = self.index2char[np.argmax(elem)]
            if char not in SPCHARS:
                text += char + self.tokenizer.intertoken
                
        return text
    
    @batchedgenerator
    @infinitegenerator
    def patterngenerator(self, corpus, tokensperpattern, start=0, end=None, **kwargs):
        """Infinite generator of encoded patterns.
        
        Arguments
            - corpus: list of tokens making up the corpus
            - tokensperpattern: how many tokens to include in every pattern
            - start: first corpus token to use in pattern generation
            - end: last corpus token to use in pattern generation
            - **kwargs: any other arguments are passed on to decodetext
        """
        tokens = self.tokenizer.transform(corpus)
        end = len(tokens) if end is None else end
        for i in range(start,end-tokensperpattern):
            x = self.encodetokens(tokens[i:i+tokensperpattern], **kwargs)
            y = self.encodetokens([tokens[i+tokensperpattern]], **kwargs).squeeze()
            yield x, y

    def save(self, filename):
        """Saves the encoding to a file"""
        with open(filename, "wb") as f:
            pkl.dump(self, f)
                       
    @property                
    def nchars(self):
        return len(self.char2index)

def loadencoding(filename):
    with open(filename, "rb") as f:
        encoder = pkl.load(f)
    return encoder
