
from scratch import IrStandard
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from scipy.interpolate import interp1d

class IRMLPTrainer:
    def __init__(self, ir_standard):
        self.ir_standard = ir_standard  # IR data handler
        self.scaler = MinMaxScaler()  # For feature scaling
    
    def extract_high_change_features(self):
        """
        Extracts high-change regions and concatenates them into a smaller input vector.
        """
        filtered_data = []
        yields = []
        
        for i, scan in enumerate(self.ir_standard.Z):
            extracted_features = []
            for start, end in self.ir_standard.highChangeRanges:
                range_mask = (self.ir_standard.allWavenumbers >= start) & (self.ir_standard.allWavenumbers <= end)
                extracted_features.extend(scan[range_mask])
            
            filtered_data.append(extracted_features)
            yields.append(i / (len(self.ir_standard.Z) - 1))  # Normalize yield between 0-1
        
        return np.array(filtered_data, dtype=np.float32), np.array(yields, dtype=np.float32)

    def interpolate_spectra(self, X, y, num_interpolated=5):
        """
        Generates additional samples by interpolating between real spectra.
        """
        X_interpolated = []
        y_interpolated = []
        
        for i in range(len(X) - 1):
            for j in range(1, num_interpolated + 1):
                alpha = j / (num_interpolated + 1)
                interpolated_spectrum = (1 - alpha) * X[i] + alpha * X[i + 1]
                interpolated_yield = (1 - alpha) * y[i] + alpha * y[i + 1]
                
                X_interpolated.append(interpolated_spectrum)
                y_interpolated.append(interpolated_yield)

        return np.array(X_interpolated), np.array(y_interpolated)

    def apply_jitter(self, X, jitter_factor=0.05):
        """
        Adds small random noise to the spectra.
        """
        noise = np.random.uniform(-jitter_factor, jitter_factor, X.shape)
        return np.clip(X + X * noise, 0, 1)  # Ensure values stay in valid range

    def prepare_training_data(self):
        """
        Extracts features, interpolates, applies jitter, normalizes, and saves to CSV.
        """
        X, y = self.extract_high_change_features()
        X_interp, y_interp = self.interpolate_spectra(X, y)
        X_jitter = self.apply_jitter(X_interp)

        # Combine all training data
        X_final = np.vstack((X, X_interp, X_jitter))
        y_final = np.concatenate((y, y_interp, y_interp))

        # Normalize features
        X_final = self.scaler.fit_transform(X_final)

        # Save to CSV
        df = pd.DataFrame(X_final)
        df['Yield'] = y_final
        df.to_csv("ir_yield_training_data.csv", index=False)

        return X_final, y_final

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
        extracted_features = processed_scan #self.extract_high_change_features(processed_scan)

        # Normalize the input
        normalized_input = self.normalize_data(extracted_features)

        # Predict yield
        yield_value = self.model.predict(np.array([normalized_input]))[0][0]
        return yield_value

    def train_mlp(self, X, y):
        """
        Trains an MLP to predict yield from IR spectra.
        """
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        model = Sequential([
            Dense(128, activation='relu', input_shape=(X.shape[1],)),
            Dense(64, activation='relu'),
            Dense(32, activation='relu'),
            Dense(1, activation='sigmoid')  # Output yield in range [0,1]
        ])

        model.compile(optimizer='adam', loss='mse', metrics=['mae'])

        history = model.fit(X_train, y_train, validation_data=(X_test, y_test),
                            epochs=100, batch_size=8, verbose=1)
        
        self.model=model
        np.save("scaler.npy", self.scaler)
        
        model.save("ir_yield_mlp.keras")
        return model, history

if __name__ == "__main__":
    # Load and process IR data
    irAnalysis = IrStandard(mainDir="isovanillin+allylbromide+product", trimLeft=200, trimRight=40)
    irAnalysis.loadData()
    
    print(f"Length: {len(irAnalysis.Z[0])}")

    trainer = IRMLPTrainer(irAnalysis)
    X, y = trainer.prepare_training_data()
    
    # Train the MLP model
    model, history = trainer.train_mlp(X, y)

    # Plot training history
    plt.figure(figsize=(10, 5))
    plt.plot(history.history['loss'], label='Training Loss')
    plt.plot(history.history['val_loss'], label='Validation Loss')
    plt.legend()
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.title('MLP Training Loss')
    
    plt.show()
    
    while True:
        _input=input("Input vector: ")
        _input = eval(_input)
        print(f"Estimated yield: {trainer.estimateYield(_input)}")