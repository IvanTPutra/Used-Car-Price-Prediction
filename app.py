from flask import Flask, render_template, request
import pandas as pd
import joblib  # Import joblib for loading the trained model
import datetime
import numpy as np
import json

# Load the dataset
df = pd.read_csv('mobil1234.csv')

# Extract unique values for dropdowns
brands = df['Brand'].unique()
names = df['Name'].unique()
transmissions = df['transmission'].unique()
locations = df['location'].unique()

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', brands=brands, names=names, transmissions=transmissions, locations=locations)

@app.route('/get_names', methods=['GET'])
def get_names():
    if request.method == 'GET':
        selected_brand = request.args.get('selected_brand')

        # Filter the unique car names based on the selected brand
        filtered_names = df[df['Brand'] == selected_brand]['Name'].unique()

        # Return the filtered names as a JSON response
        return json.dumps(filtered_names.tolist())

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        # Retrieve user input from the form
        brand = request.form.get('brand')
        year = int(request.form.get('year'))
        kilometer = int(request.form.get('kilometer'))

        # Calculate 'Car_Age' and 'Mileage_Per_Year'
        current_year = datetime.datetime.now().year
        car_age = current_year - year
        mileage_per_year = kilometer / car_age if car_age > 0 else 0

        # Create a DataFrame from the user's input
        input_data = pd.DataFrame({
            'Year': [year],
            'Kilometer': [kilometer],
            'Car_Age': [car_age],
            'Mileage_Per_Year': [mileage_per_year],
            'Brand': [brand],
            'transmission': [request.form.get('transmission')],
            'location': [request.form.get('location')],
            'Name': [request.form.get('name')]
        })

        # Use trained model to make predictions
        predicted_price = make_prediction(input_data)

        if predicted_price is not None:
            # Convert from logarithmic scale to normal scale using np.exp
            predicted_price = np.exp(predicted_price)

            # Calculate the price range
            range_min = predicted_price * 0.975  # 95% of the predicted price
            range_max = predicted_price * 1.025  # 105% of the predicted price

            # Round the price range to the nearest million
            range_min = round(range_min, -6)
            range_max = round(range_max, -6)

            # Format the price range as strings with the desired format
            formatted_range = "Rp {:,.0f} - Rp {:,.0f}".format(int(range_min), int(range_max))

            # Display the price range on the web page
            return render_template('index.html', brands=brands, names=names, transmissions=transmissions, locations=locations, range=formatted_range)
        else:
            formatted_range = "Price range not available"

        # Display the price range on the web page
        return render_template('index.html', brands=brands, names=names, transmissions=transmissions, locations=locations, range=formatted_range)


def make_prediction(input_data):
    # Load trained model
    model = joblib.load('trained_model.joblib')

    # Convert the input data (list of dictionaries) to a DataFrame
    input_df = pd.DataFrame(input_data)

    # Make predictions using the loaded model
    predicted_price = model.predict(input_df)  # Provide a DataFrame

    return predicted_price[0]  # Return the first prediction



if __name__ == '__main__':
    app.run(debug=True)