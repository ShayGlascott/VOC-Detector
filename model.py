import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib

# Constants for the script
WINDOW_SIZE = 10  # Adjust based on your model's needs
TEST_SIZE = 0.2
VALIDATION_SIZE = 0.1

# Load data
file_paths = [
    'data/labeled/ambient1.csv',
    'data/labeled/ambient2.csv',
    'data/labeled/ambient3.csv',
    'data/labeled/breathing1.csv'
]
dataframes = [pd.read_csv(file) for file in file_paths]
data = pd.concat(dataframes, ignore_index=True)

# Normalize the sensor data
scaler = StandardScaler()
data[['CO2', 'TVOC', 'Temperature', 'Pressure', 'Humidity']] = scaler.fit_transform(data[['CO2', 'TVOC', 'Temperature', 'Pressure', 'Humidity']])

# Encode labels
data['Label'] = data['Label'].str.lower()  # Normalize casing
label_encoder = LabelEncoder()
data['Label'] = label_encoder.fit_transform(data['Label'])

# Function to create windows
def create_windows(data, window_size, step=1):
    X = []
    y = []
    for i in range(0, len(data) - window_size, step):
        window = data.iloc[i:i+window_size]
        X.append(window[['CO2', 'TVOC', 'Temperature', 'Pressure', 'Humidity']].values)
        y.append(window['Label'].iloc[-1])  # Label for the last item in the window
    return np.array(X), np.array(y)

# Create windows
X, y = create_windows(data, WINDOW_SIZE)

# Split data into training, validation, and testing sets
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=TEST_SIZE + VALIDATION_SIZE, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=TEST_SIZE / (TEST_SIZE + VALIDATION_SIZE), random_state=42)

print("Training set size:", len(X_train))
print("Validation set size:", len(X_val))
print("Testing set size:", len(X_test))

import tensorflow as tf
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from keras.callbacks import EarlyStopping

# Constants
BATCH_SIZE = 32
EPOCHS = 50

# Defining the RNN model
def build_model(input_shape, num_classes):
    model = Sequential([
        LSTM(64, return_sequences=True, input_shape=input_shape),
        Dropout(0.5),
        LSTM(32),
        Dropout(0.5),
        Dense(32, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return model

# Get input shape and number of classes from the data
input_shape = X_train.shape[1:]  # Shape of the input data (window_size, num_features)
num_classes = len(np.unique(y_train))  # Number of unique labels

# Build and compile the model
model = build_model(input_shape, num_classes)

# Print model summary
print(model.summary())

# Early stopping to prevent overfitting
early_stopping = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)

# Train the model
history = model.fit(
    X_train, y_train,
    validation_data=(X_val, y_val),
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=[early_stopping]
)

# Evaluate the model on the test set
test_loss, test_accuracy = model.evaluate(X_test, y_test)
print("Test Loss:", test_loss)
print("Test Accuracy:", test_accuracy)

# Plot training history
import matplotlib.pyplot as plt

def plot_history(history):
    plt.figure(figsize=(12, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(history.history['accuracy'], label='Training accuracy')
    plt.plot(history.history['val_accuracy'], label='Validation accuracy')
    plt.title('Accuracy over epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Accuracy')
    plt.legend()
    
    plt.subplot(1, 2, 2)
    plt.plot(history.history['loss'], label='Training loss')
    plt.plot(history.history['val_loss'], label='Validation loss')
    plt.title('Loss over epochs')
    plt.xlabel('Epochs')
    plt.ylabel('Loss')
    plt.legend()

    plt.show()

# plot the training and validation loss and accuracy
plot_history(history)

model.save('model.h5')
joblib.dump(label_encoder, 'label_encoder.pkl')
