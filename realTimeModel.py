import serial
import numpy as np
from keras.models import load_model
from sklearn.preprocessing import StandardScaler
import joblib

# Load the pre-trained model and the LabelEncoder
model = load_model('model.h5')
label_encoder = joblib.load('label_encoder.pkl')

# Setup the serial connection
# Will need to change port/modem 
ser = serial.Serial('/dev/cu.usbmodem11401', 9600)

# Constants
WINDOW_SIZE = 10
FEATURES = ['CO2', 'TVOC', 'Temperature', 'Pressure', 'Humidity']
scaler = StandardScaler()

# Collect initial data to fit the scaler
initial_data = []
while len(initial_data) < WINDOW_SIZE:
    line = ser.readline().decode('utf-8').strip()
    if line.startswith('(') and line.endswith(')'):
        line = line[1:-1]
        data = [float(x) for x in line.split(',')]
        initial_data.append(data)

scaler.fit(initial_data)  # Fit the scaler with the initial data
data_window = initial_data.copy()  # Start with initial data in the window

def predict_with_model(data_window):
    # Convert data window to numpy array and scale
    array = scaler.transform(data_window)
    array = np.array([array])  # Reshape for model input
    prediction = model.predict(array)
    predicted_label = label_encoder.inverse_transform([np.argmax(prediction)])[0]
    print("Predicted value:", predicted_label)

def read_from_serial():
    while True:
        line = ser.readline().decode('utf-8').strip()
        if line.startswith('(') and line.endswith(')'):
            line = line[1:-1]
            data = [float(x) for x in line.split(',')]
            data_window.append(data)
            if len(data_window) > WINDOW_SIZE:
                data_window.pop(0)  # Maintain sliding window size
            predict_with_model(data_window)

if __name__ == '__main__':
    read_from_serial()
