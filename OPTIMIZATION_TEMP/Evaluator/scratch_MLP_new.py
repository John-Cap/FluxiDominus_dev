
import copy
import keras
from scipy.interpolate import interp1d, griddata
from scipy.stats import pearsonr
from fastdtw import fastdtw
from scipy.spatial.distance import euclidean
from scipy.interpolate import CubicSpline
import os
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split


from scratch import IrStandard

class IRMLPTrainer:
    def __init__(self, ir_standard):
        self.ir_standard = ir_standard  # IR data handler
        self.scaler = None  # MinMaxScaler will be initialized during training
        self.model = None   # Trained MLP model

    def extract_high_change_features(self, scan):
        """
        Extracts high-change regions and concatenates them into a smaller feature vector.
        """
        extracted_features = []
        for start, end in self.ir_standard.highChangeRanges:
            range_mask = (self.ir_standard.allWavenumbers >= start) & (self.ir_standard.allWavenumbers <= end)
            extracted_features.extend(scan[range_mask])
        
        return np.array(extracted_features, dtype=np.float32)

    def normalize_data(self, X):
        """
        Normalizes the input features using the same MinMaxScaler as training.
        """
        if self.scaler is None:
            raise ValueError("Scaler not initialized. Train or load the model first.")
        return self.scaler.transform([X])[0]  # Keep it 1D

    def prepare_training_data(self):
        """
        Extracts features, normalizes, and returns the training dataset.
        """
        X, y = [], []
        
        for i, scan in enumerate(self.ir_standard.Z):
            features = self.extract_high_change_features(scan)
            X.append(features)
            y.append(i / (len(self.ir_standard.Z) - 1))  # Normalize yield

        X = np.array(X)
        y = np.array(y)

        # Fit and transform the MinMaxScaler
        self.scaler = MinMaxScaler()
        X = self.scaler.fit_transform(X)

        return X, y

    def train_mlp(self, X, y):
        """
        Trains an MLP model and saves the scaler.
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = Sequential([
            Dense(128, activation='relu', input_shape=(X.shape[1],)),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')  # Output yield in range [0,1]
        ])

        model.compile(optimizer='adam', loss='mse')
        model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=100, batch_size=8, verbose=1)

        self.model = model
        model.save("ir_yield_mlp.keras")

        # Save scaler
        np.save("scaler.npy", self.scaler)

    def loadModel(self, path="ir_yield_mlp.keras"):
        """
        Loads a trained MLP model and the associated MinMaxScaler.
        """
        self.model = tf.keras.models.load_model(path)

        # Load the scaler
        try:
            self.scaler = np.load("scaler.npy", allow_pickle=True).item()
        except FileNotFoundError:
            raise ValueError("Scaler file not found. Make sure to train the model first.")

        print(f"✅ Model loaded from {path}")

    def estimateYield(self, input_scan):
        """
        Estimates the yield from a new IR scan.

        Parameters:
        - input_scan (list of 839 elements): Raw IR spectrum.

        Returns:
        - yield_value (float): Predicted yield in range [0,1].
        """
        if self.model is None:
            raise ValueError("Model not loaded. Use loadModel() first.")

        # Convert list to NumPy array
        input_scan = np.array(input_scan, dtype=np.float32)

        # Process raw scan: interpolate onto standard grid
        _, processed_scan = self.ir_standard.processRawScan(self.ir_standard.allWavenumbers, input_scan)

        # Extract high-change regions
        extracted_features = self.extract_high_change_features(processed_scan)

        # Normalize the input
        normalized_input = self.normalize_data(extracted_features)

        # Predict yield
        yield_value = self.model.predict(np.array([normalized_input]))[0][0]
        return yield_value

if __name__ == "__main__":
    # Load IR standard processing
    irAnalysis = IrStandard(mainDir="isovanillin+allylbromide+product", trimLeft=200, trimRight=40)
    irAnalysis.loadData()
    irAnalysis.trimData()
    highChangeRanges = irAnalysis.detectHighChangeRegions()
    irAnalysis.filterDataInterpolate(highChangeRanges, interpolationFactor=3)

    # Initialize Trainer
    trainer = IRMLPTrainer(irAnalysis)

    # Load the trained model
    trainer.loadModel("ir_yield_mlp.keras")

    while True:
        _input=input("Input vector: ")
        _input = eval(_input)
        print(f"Estimated yield: {trainer.estimateYield(_input)}")
