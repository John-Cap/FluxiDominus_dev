import numpy as np
import keras
from keras.models import Sequential
from keras.layers import LSTM, Dense
from keras.losses import Huber
from time import sleep
import uuid

class Optimizer:
    def __init__(self, reaction_lookup, stop_val=0.95, sequence_length=5):
        self.reaction_lookup = reaction_lookup
        self.stop_val = stop_val
        self.sequence_length = sequence_length
        self.models = {}
        self.optimize = True
        self.cycle_number = 0

    def build_model(self, input_shape, param_names, param_bounds, name=None):
        """Initialize an LSTM model for optimization."""
        model = Sequential([
            LSTM(64, input_shape=input_shape),
            Dense(len(param_names), activation='relu')
        ])
        model.compile(optimizer='adam', loss=Huber())
        
        model_id = name or str(uuid.uuid4())
        self.models[model_id] = {
            'model': model,
            'param_names': param_names,
            'param_bounds': param_bounds,
            'history': []
        }
        print(f"Model '{model_id}' created.")
        return model_id

    def _normalize_params(self, params, bounds):
        """Normalize parameters to [0, 1] based on bounds."""
        return [(p - bounds[name][0]) / (bounds[name][1] - bounds[name][0]) for name, p in params.items()]

    def _denormalize_params(self, normalized_params, bounds):
        """Denormalize parameters from [0, 1] to original scale."""
        return {name: norm * (bounds[name][1] - bounds[name][0]) + bounds[name][0]
                for name, norm in zip(bounds.keys(), normalized_params)}

    def get_next_params(self, model_id):
        """Predict the next set of parameters."""
        model_data = self.models[model_id]
        history = model_data['history']
        param_bounds = model_data['param_bounds']

        if len(history) < self.sequence_length:
            # Random initialization if not enough history
            return {name: np.random.uniform(bounds[0], bounds[1]) 
                    for name, bounds in param_bounds.items()}
        
        # Prepare input data for prediction
        recent_data = np.array([entry['normalized'] for entry in history[-self.sequence_length:]])
        recent_data = recent_data.reshape(1, self.sequence_length, -1)
        predicted_norm = model_data['model'].predict(recent_data, verbose=0)[0]
        return self._denormalize_params(predicted_norm, param_bounds)

    def evaluate_params(self, params):
        """Simulate the reaction to get the yield."""
        yield_val = self.reaction_lookup.get_yield(params['temp'], params['time'])
        return yield_val

    def run_cycle(self, model_id):
        """Run a single optimization cycle."""
        model_data = self.models[model_id]
        param_names = model_data['param_names']

        params = self.get_next_params(model_id)
        yield_val = self.evaluate_params(params)

        # Record history
        normalized_params = self._normalize_params(params, model_data['param_bounds'])
        model_data['history'].append({
            'params': params,
            'normalized': normalized_params,
            'yield': yield_val
        })

        print(f"Cycle {self.cycle_number}: Params {params}, Yield {yield_val:.2f}")

        # Check if yield exceeds stop value
        if yield_val >= self.stop_val:
            self.optimize = False
            print(f"Optimization complete for {model_id}. Best Yield: {yield_val:.2f}")

        return params, yield_val

    def train_model(self, model_id):
        """Train the model using the collected history."""
        model_data = self.models[model_id]
        history = model_data['history']
        
        if len(history) < self.sequence_length:
            print(f"Not enough data to train model {model_id}.")
            return

        # Prepare training data
        X = np.array([entry['normalized'] for entry in history[:-1]])
        y = np.array([entry['normalized'] for entry in history[1:]])
        X = X.reshape(-1, self.sequence_length, len(model_data['param_names']))
        y = y.reshape(-1, len(model_data['param_names']))

        # Train the model
        model_data['model'].fit(X, y, epochs=30, verbose=0)
        print(f"Model {model_id} trained.")

    def optimize_loop(self):
        """Run the optimization loop."""
        while self.optimize:
            for model_id in self.models:
                params, yield_val = self.run_cycle(model_id)
                self.train_model(model_id)
            self.cycle_number += 1
        print("Optimization loop finished.")

# Reaction lookup mock
class ReactionLookup:
    def get_yield(self, temp, time):
        return 1 - abs(temp - 20) * 0.05 - abs(time - 10) * 0.05  # Example surface

# Initialize optimizer
reaction_lookup = ReactionLookup()
optimizer = Optimizer(reaction_lookup, stop_val=0.95, sequence_length=5)

# Create and optimize models
param_bounds = {"temp": (0, 40), "time": (0, 20)}
model_id = optimizer.build_model((5, 2), ["temp", "time"], param_bounds, name="Reaction1")
optimizer.optimize_loop()
