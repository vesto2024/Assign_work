import streamlit as st
import pandas as pd
import joblib
import mysql.connector
from mysql.connector import Error
import matplotlib.pyplot as plt
import seaborn as sns

# Load the trained model
model_filename = "random_forestt_model.pkl"
try:
    model = joblib.load(model_filename)
except FileNotFoundError:
    st.error(f"Error: Model file '{model_filename}' not found!")
    st.stop()

# Expected features from training (only the ones you want to use)
trained_features = [
    'Attendance', 'Assignment_Score', 'Midterm_Score', 
    'Final_Score', 'Outstanding_Balance'
]

# MySQL connection details
config = {
    'user': 'root',                # MySQL username
    'password': 'Mukunzi@2025',       # MySQL password
    'host': 'localhost',           # MySQL host (usually localhost)
    'database': 'data_warehouse',  # Your database name
    'raise_on_warnings': True
}

# Function to insert data into MySQL (simplified for your features)
def insert_prediction_data(prediction_data, prediction_result):
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # SQL query to insert data (only the selected features)
        insert_query = """
        INSERT INTO student_records (
            Attendance, Assignment_Score, Midterm_Score, 
            Final_Score, Outstanding_Balance, Performance
        ) 
        VALUES (%s, %s, %s, %s, %s, %s);
        """
        
        # Append the prediction result (1 for Pass, 0 for Fail)
        prediction_data.append(prediction_result)
        
        cursor.execute(insert_query, tuple(prediction_data))
        connection.commit()  # Commit the transaction
        st.success("Data saved to database successfully!")
    except Error as e:
        st.error(f"Error during database insertion: {e}")
    finally:
        connection.close()

# Streamlit UI
st.set_page_config(page_title="Student Performance Dashboard", layout="centered")

# Custom styles (unchanged)
st.markdown("""
    <style>
    .css-1v0mbdj {
        background-color: #e1f5fe; /* Light blue background */
    }
    h1 {
        font-family: 'Arial', sans-serif;
        color: #0277bd; /* Dark blue color */
        text-align: center;
    }
    .stButton>button {
        background-color: #0277bd;
        color: white;
        font-size: 18px;
    }
    .stSidebar .sidebar-content {
        background-color: #b3e5fc; /* Light blue for sidebar */
    }
    .stSlider>div>div {
        background-color: #bbdefb; /* Light blue for sliders */
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1>📊 Student Performance Prediction</h1>", unsafe_allow_html=True)
st.write("Enter student details to predict performance.")

# Input form (only the selected features)
input_data = {}

input_data["Attendance"] = st.slider("Attendance (%)", 0, 100, 75)
input_data["Assignment_Score"] = st.slider("Assignment Score", 0, 100, 70)
input_data["Midterm_Score"] = st.slider("Midterm Score", 0, 100, 50)
input_data["Final_Score"] = st.slider("Final Score", 0, 100, 50)
input_data["Outstanding_Balance"] = st.number_input("Outstanding Balance (RWF)", min_value=0, max_value=500000, value=0)

# Convert input to DataFrame
input_df = pd.DataFrame([input_data])

# Ensure input_df matches training features
for col in trained_features:
    if col not in input_df:
        input_df[col] = 0  # Add missing features as 0 (shouldn't happen here)

# Reorder columns to match training data
input_df = input_df[trained_features]

# Make prediction
if st.button("Predict Performance"):
    try:
        prediction = model.predict(input_df)[0]
        prediction_result = int(prediction)  # Convert to int (0 or 1)
        
        performance_label = "Pass ✅" if prediction_result == 1 else "Fail ❌"
        st.success(f"Prediction: {performance_label}")

        # Insert data into the database after prediction
        insert_prediction_data(list(input_data.values()), prediction_result)

    except Exception as e:
        st.error(f"Error during prediction: {e}")

# Display Pass/Fail Overview (simplified visualization)
def visualize_performance():
    st.subheader("Pass/Fail Overview 📊")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.countplot(x=[1, 0, 1, 0, 1], ax=ax, palette="Set1")  # Example pass/fail data
    ax.set_title("Pass/Fail Distribution")
    ax.set_xlabel("Prediction (1 = Pass, 0 = Fail)")
    ax.set_ylabel("Count")
    st.pyplot(fig)

# Call the visualization function
visualize_performance()