# -*- coding: utf-8 -*-
"""Healthcare Data Dashboard.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Dmewos7VIYcN6t9yBr6sPp-zK4S7vyV2
"""

#pip install streamlit pandas matplotlib seaborn

import pandas as pd
import numpy as np
import streamlit as st
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("hospital data analysis.csv")

# View sample data
print(df.head())

# Convert data types
df["Readmission"] = df["Readmission"].map({"Yes": 1, "No": 0})  # Convert to 0/1 for analysis
df["Length_of_Stay"] = pd.to_numeric(df["Length_of_Stay"], errors="coerce")
df["Satisfaction"] = pd.to_numeric(df["Satisfaction"], errors="coerce")
df["Cost"] = pd.to_numeric(df["Cost"], errors="coerce")

print(df.head())

#handle missing values

df.dropna(subset=["Length_of_Stay", "Readmission", "Satisfaction"], inplace=True)
df.fillna({"Cost": df["Cost"].median()}, inplace=True)  # Fill cost with median

#nan values
nan_counts = df[['Age', 'Readmission']].isna().sum()
total_rows = len(df)

nan_percentage = (nan_counts / total_rows) * 100

print("NaN counts:\n", nan_counts)
print("\nNaN percentage:\n", nan_percentage)

import matplotlib.pyplot as plt
import seaborn as sns

# Group by Condition and calculate average stay
stay_by_condition = df.groupby("Condition")["Length_of_Stay"].mean().sort_values()

# Plot
plt.figure(figsize=(10,5))
sns.barplot(x=stay_by_condition.index, y=stay_by_condition.values, palette="viridis")
plt.xticks(rotation=45)
plt.xlabel("Medical Condition")
plt.ylabel("Average Length of Stay (Days)")
plt.title("Average Length of Stay by Medical Condition")
plt.show()

# Create Age Groups
df["Age Group"] = pd.cut(df["Age"], bins=[0, 18, 40, 60, 80, 100], labels=["0-18", "19-40", "41-60", "61-80", "81+"])

# Calculate Readmission Rate per Age Group
readmission_rates = df.groupby("Age Group")["Readmission"].mean()

# Drop NaN values from readmission_rates before plotting
readmission_rates = readmission_rates.dropna()

# Plot
plt.figure(figsize=(6,6))
plt.pie(readmission_rates, labels=readmission_rates.index, autopct="%1.1f%%", colors=sns.color_palette("pastel"))
plt.title("Readmission Rate by Age Group")
plt.show()

# Count outcomes over time
discharge_trends = df.groupby("Outcome").size()

# Plot
plt.figure(figsize=(8,5))
sns.lineplot(x=discharge_trends.index, y=discharge_trends.values, marker="o", color="b")
plt.xticks(rotation=45)
plt.xlabel("Outcome")
plt.ylabel("Number of Patients")
plt.title("Discharge Trends by Outcome")
plt.show()

# Group by Procedure and get average satisfaction score
satisfaction_by_procedure = df.groupby("Procedure")["Satisfaction"].mean().sort_values()

# Plot
plt.figure(figsize=(10,5))
sns.barplot(x=satisfaction_by_procedure.index, y=satisfaction_by_procedure.values, palette="coolwarm")
plt.xticks(rotation=45)
plt.xlabel("Procedure")
plt.ylabel("Average Satisfaction Score")
plt.title("Patient Satisfaction by Procedure")
plt.show()

# Group by Condition and calculate average cost
cost_by_condition = df.groupby("Condition")["Cost"].mean().sort_values()

# Plot
plt.figure(figsize=(10,5))
sns.barplot(x=cost_by_condition.index, y=cost_by_condition.values, palette="Blues_r")
plt.xticks(rotation=45)
plt.xlabel("Medical Condition")
plt.ylabel("Average Treatment Cost ($)")
plt.title("Average Treatment Cost by Condition")
plt.show()

import streamlit as st
import plotly.express as px  # Import plotly.express

st.title("🏥 Patient Stay & Discharge Analytics")

st.subheader("📊 Average Length of Stay by Medical Condition")
st.bar_chart(stay_by_condition)

st.subheader("📈 Readmission Rate by Age Group")
fig = px.pie(readmission_rates, values=readmission_rates.values, names=readmission_rates.index, title="Readmission Rate by Age Group") # Create the pie chart using plotly.express
st.plotly_chart(fig)  # Display the pie chart using st.plotly_chart

st.subheader("📉 Discharge Trends by Outcome")
st.line_chart(discharge_trends)

st.subheader("💰 Average Treatment Cost by Condition")
st.bar_chart(cost_by_condition)

"""# ML Models"""

X = df[['Age', 'Gender', 'Condition', 'Procedure', 'Cost', 'Readmission']]
y = df['Length_of_Stay']

# Convert categorical data into numeric using One-Hot Encoding
X = pd.get_dummies(X, drop_first=True)

# Split data into training & testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a RandomForest Model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict & Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
st.write(f"**Model Performance (MAE):** {mae:.2f}")

st.sidebar.header("Predict Patient Stay")

# User input fields
age = st.sidebar.number_input("Age", min_value=0, max_value=100, value=30)
gender = st.sidebar.selectbox("Gender", ["Male", "Female"])
condition = st.sidebar.selectbox("Condition", df["Condition"].unique())
procedure = st.sidebar.selectbox("Procedure", df["Procedure"].unique())
cost = st.sidebar.number_input("Cost", min_value=100, max_value=100000, value=5000)
readmission = st.sidebar.selectbox("Readmission", [0, 1])

# Convert input into dataframe
input_data = pd.DataFrame([[age, gender, condition, procedure, cost, readmission]],
                          columns=['Age', 'Gender', 'Condition', 'Procedure', 'Cost', 'Readmission'])

# Apply one-hot encoding to match training format
input_data = pd.get_dummies(input_data, drop_first=True)

# Ensure same columns as training data
missing_cols = set(X.columns) - set(input_data.columns)
for col in missing_cols:
    input_data[col] = 0

# Predict Length of Stay
if st.sidebar.button("Predict Stay"):
    prediction = model.predict(input_data)
    st.sidebar.write(f"**Predicted Length of Stay:** {prediction[0]:.2f} days")