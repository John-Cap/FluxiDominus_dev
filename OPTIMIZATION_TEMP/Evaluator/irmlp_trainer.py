import ast
import copy
import keras
import os
import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
import paho.mqtt.client as mqtt

SHARED_FOLDER = "../SharedData/"  # Set path to shared folder

class IRMLPTrainer:
    def __init__(self, csv_path, csv_path_unaveraged, csv_path_unmasked, num_interpolated=10, jitter_factor=0.05, client=None, host="localhost"):
        """
        Initializes the IRMLPTrainer with a dataset from a CSV file.
        
        Parameters:
        - csv_path (str): Path to the CSV file containing intensities and yield.
        - num_interpolated (int): Number of additional interpolated samples between each real sample.
        - jitter_factor (float): Maximum percentage noise to add for jittered data augmentation.
        """
        self.csv_path = csv_path
        self.csv_path_unaveraged = csv_path_unaveraged
        self.csv_path_unmasked = csv_path_unmasked
        
        self.num_interpolated = num_interpolated
        self.jitter_factor = jitter_factor
        self.scaler = None  # MinMaxScaler will be initialized during training
        self.model = None   # Trained MLP model
        self.X = None       # Feature matrix
        self.y = None       # Yield values
        
        self.trimLeft=0
        self.trimRight=0
        
        self.smallValueThreshold=0.01
        
        self.evaluatorCmndPath=(os.path.join(SHARED_FOLDER, "evaluatorCmnd.json"))
         
        self.client = client if client else (mqtt.Client(client_id="Evaluator", clean_session=True, userdata=None, protocol=mqtt.MQTTv311))
        self.host=host
        self.topicIn="eval/out"
        self.topicOut="eval/in"
        
        self.client.on_connect = self.onConnect
        self.client.on_message = self.onMessage
        
        self.inputLength=599
        
        self.yields=[]
        self.highestYield=0
        self.evaluatingYields=False

    def load_and_prepare_data(self):
        """
        Loads the dataset from CSV, normalizes it, interpolates additional samples, 
        applies jitter augmentation, and saves the processed dataset.
        """
        # Load the dataset
        df = pd.read_csv(self.csv_path)
        dfUnaveraged = pd.read_csv(self.csv_path_unaveraged)
        dfUnmasked = pd.read_csv(self.csv_path_unmasked)

        # Separate features and labels
        X = df.iloc[:, :-1].values  # All columns except the last one (intensities)
        y = df.iloc[:, -1].values   # Last column (yield)
        
        Xunaveraged = dfUnaveraged.iloc[:, :-1].values  # All columns except the last one (intensities)
        yUnaveraged = dfUnaveraged.iloc[:, -1].values   # Last column (yield)
        
        Xunmasked = dfUnmasked.iloc[:, :-1].values  # All columns except the last one (intensities)
        yUnmasked = dfUnmasked.iloc[:, -1].values   # Last column (yield)

        # Interpolate additional samples
        X_interp, y_interp = self.interpolate_spectra(X, y)
        # Interpolate additional samples unaveraqged
        X_interpUnaveraged, y_interpUnaveraged = self.interpolate_spectra(Xunaveraged, yUnaveraged)
        # Interpolate additional samples unmasked
        X_interpUnmasked, y_interpUnmasked = self.interpolate_spectra(Xunmasked, yUnmasked)

        # Apply jitter to interpolated samples
        X_jittered = self.apply_jitter(X_interp)
        X_jitteredUnaveraged = self.apply_jitter(Xunaveraged)
        X_jitteredUnmasked = self.apply_jitter(Xunmasked)

        # Combine original, interpolated, and jittered data
        X_final = np.vstack((X, X_interp, X_jittered, Xunaveraged, Xunmasked, X_jitteredUnaveraged, X_jitteredUnmasked, X_interpUnaveraged, X_interpUnmasked))
        y_final = np.concatenate((y, y_interp, y_interp, yUnaveraged, yUnmasked, yUnaveraged, yUnmasked, y_interpUnaveraged, y_interpUnmasked))  # Duplicates for jittered versions

        X_final[np.abs(X_final) < self.smallValueThreshold] = 0

        # Normalize the feature set
        self.scaler = MinMaxScaler()
        X_final = self.scaler.fit_transform(X_final)

        # Save processed training data
        processed_df = pd.DataFrame(X_final)
        processed_df["Yield"] = y_final
        processed_df.to_csv("ir_yield_training_data.csv", index=False)

        print(f"✅ Processed training data saved to ir_yield_training_data.csv")
        
        # Store the training data
        self.X, self.y = X_final, y_final

    def interpolate_spectra(self, X, y):
        """
        Generates additional samples by interpolating between real spectra.

        Parameters:
        - X (np.array): Original feature matrix.
        - y (np.array): Original yield values.

        Returns:
        - X_interpolated (np.array): Interpolated spectra.
        - y_interpolated (np.array): Corresponding interpolated yields.
        """
        X_interpolated = []
        y_interpolated = []

        for i in range(len(X) - 1):
            for j in range(1, self.num_interpolated + 1):
                alpha = j / (self.num_interpolated + 1)
                interpolated_spectrum = (1 - alpha) * X[i] + alpha * X[i + 1]
                interpolated_yield = (1 - alpha) * y[i] + alpha * y[i + 1]

                X_interpolated.append(interpolated_spectrum)
                y_interpolated.append(interpolated_yield)

        return np.array(X_interpolated), np.array(y_interpolated)

    def apply_jitter(self, X):
        """
        Applies jittering (small random noise) to spectra to improve model generalization.

        Parameters:
        - X (np.array): Feature matrix.

        Returns:
        - X_jittered (np.array): Jittered version of the input data.
        """
        noise = np.random.uniform(-self.jitter_factor, self.jitter_factor, X.shape)
        return np.clip(X + X * noise, 0, 1)  # Ensure values remain within [0,1]

    def train_mlp(self):
        """
        Trains an MLP model using the processed dataset.
        """
        if self.X is None or self.y is None:
            raise ValueError("Data not prepared. Run load_and_prepare_data() first.")

        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)

        model = Sequential([
            Dense(256, activation='relu', input_shape=(self.X.shape[1],)),
            Dense(128, activation='relu'),
            Dense(32, activation='relu'),
            Dense(1, activation='relu')  # Output yield in range [0,1]
        ])

        model.compile(optimizer='adam', loss='mse', metrics=['mae'])

        history = model.fit(X_train, y_train, validation_data=(X_test, y_test),
                            epochs=55, batch_size=30, verbose=1)
        
        self.model = model
        model.save("ir_yield_mlp.keras")

        # Save the scaler
        np.save("scaler.npy", self.scaler)

        print("✅ Model training complete and saved as ir_yield_mlp.keras")

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

    def estimateYield(self, input_scan, normalize=True, applySmallValueThreshold=True):
        """
        Estimates the yield from a new IR scan.

        Parameters:
        - input_scan (list of float): Raw IR spectrum.

        Returns:
        - yield_value (float): Predicted yield in range [0,1].
        """
        if self.model is None:
            raise ValueError("Model not loaded. Use loadModel() first.")

        # Convert input to NumPy array
        input_scan = np.array(input_scan, dtype=np.float32)
        
        if applySmallValueThreshold:
            input_scan[np.abs(input_scan) < self.smallValueThreshold] = 0

        if normalize:
            # Normalize input using the same scaler as training
            normalized_input = self.scaler.transform([input_scan])[0]
        else:
            normalized_input=input_scan

        # Predict yield
        yield_value = self.model.predict(np.array([normalized_input]))[0][0]
        return yield_value
    
    def trimDataSingle(self, data_array):
        """
        Trims the given data array based on user-defined left and right trim points.

        Parameters:
        - data_array (np.array or list): The dataset to be trimmed.

        Returns:
        - trimmed_data (np.array): The trimmed version of the input dataset.
        """
        if self.trimLeft == 0 and self.trimRight == 0:
            return np.array(data_array)  # Return unmodified if no trimming needed

        # Ensure input is a NumPy array
        data_array = np.array(data_array)

        # Check if data_array is empty
        if data_array.size == 0:
            print("🚨 Warning: No data available to trim.")
            return data_array  # Return empty array

        # Determine if data is 1D or 2D
        if data_array.ndim == 1:  # If 1D (single spectrum)
            scan_length = len(data_array)

            if self.trimLeft + self.trimRight >= scan_length:
                print("🚨 Warning: Trimming exceeds data length. Skipping trim operation.")
                return data_array  # Return unmodified

            trimmed_data = data_array[self.trimLeft:-self.trimRight]

        elif data_array.ndim == 2:  # If 2D (multiple spectra)
            scan_length = data_array.shape[1]

            if self.trimLeft + self.trimRight >= scan_length:
                print("🚨 Warning: Trimming exceeds data length. Skipping trim operation.")
                return data_array  # Return unmodified

            trimmed_data = data_array[:, self.trimLeft:-self.trimRight]

        else:
            raise ValueError("🚨 Unexpected data shape. Expected 1D or 2D array.")

        print(f"✅ Trimmed data: New shape {trimmed_data.shape}")
        return trimmed_data

    def onMessage(self, client, userdata, msg):
        _msgContents = msg.payload.decode()
        _msgContents = _msgContents.replace("true", "True").replace("false", "False")
        _msgContents=_msgContents.replace("null","None")
        _msgContents = ast.literal_eval(_msgContents)
        
        if "goEvaluator" in _msgContents:
            ir=_msgContents["scan"]
            length=len(_msgContents["scan"])
            if length == 0:
                return
            if length != self.inputLength:
                ir = self.trimDataSingle(ir)
            yield_score = self.estimateYield(ir)
            if _msgContents["goEvaluator"]:
                if self.evaluatingYields:
                    self.yields.append(yield_score)
                else:
                    self.evaluatingYields=True
                    self.yields=[]
                    self.yields.append(yield_score)
                self.highestYield=max(self.yields)
                print(f"Yields: {self.yields}")
            else:
                if len(self.yields) != 0:
                    self.highestYield=max(self.yields)
                    self.evaluatingYields=False
                    
            print(f"🔹 Evaluated yield: {yield_score*100}")
            
    def onConnect(self, client, userdata, flags, rc):
        #if self.connected:
            #return
        print(f"WJ - Connected with rc {rc}!")
        if rc == 0:
            self.client.subscribe(topic=self.topicIn)
            
if __name__ == "__main__":
    # Initialize Trainer with the CSV file
    trainer = IRMLPTrainer(csv_path="ir_yield_no_resample_averages.csv", csv_path_unaveraged= 'ir_yield_no_resample_unaveraged.csv', csv_path_unmasked='ir_yield_no_resample_unmasked.csv', num_interpolated=5, jitter_factor=0.05)

    # Load, process, and prepare training data
    #trainer.load_and_prepare_data()
    
    #print(f"Number of examples: {trainer.X.shape}")

    # Train the MLP model
    #trainer.train_mlp()

    # Load trained model
    trainer.loadModel("ir_yield_mlp.keras")
    
    trainer.trimLeft=200
    trainer.trimRight=40

    # Test loop
    # _i=0
    # _wrong=0
    # for _x in trainer.X:
    #     _est=trainer.estimateYield(_x,False,False)
    #     _true=trainer.y[_i]
    #     _err=error = abs(_true - _est) * 100
    #     if _err > 5:
    #         _wrong+=1
    #     print(f"Estimated yield: {_est}, true: {_true}, error: {_err}")
    #     _i+=1
    # print(f"Percentage of incorrect predictions: {100*(_wrong/(trainer.X.shape[0]))}")

    # Interactive prediction loop
    while True:
        _input = input("Input vector: ")
        _input = eval(_input)  # Convert input string to a list
        _input=trainer.trimDataSingle(_input)
        
        print(f"Estimated yield standard: {trainer.estimateYield(_input)}")
