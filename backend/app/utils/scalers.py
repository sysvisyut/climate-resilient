"""
Custom scaler classes for the ML models
This module contains scaler classes that can be pickled and loaded by any module
"""

class DummyScaler:
    """A simple scaler that doesn't transform the data.
    This is used for model serialization when we need a placeholder scaler.
    """
    def __init__(self):
        pass
        
    def transform(self, X):
        return X
        
    def inverse_transform(self, y):
        return y
        
    def fit(self, X, y=None):
        return self
