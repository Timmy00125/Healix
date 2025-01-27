from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import tensorflow as tf
import numpy as np
import pandas as pd
import os
import joblib
import json


class ConditionPredictionView(APIView):
    """
    API endpoint to predict condition likelihoods based on patient data.
    """

    def post(self, request):
        patient_data = request.data
        required_fields = [
            "gender",
            "age",
            "bmi",
            "sys_bp",
            "dia_bp",
            "heart_rate",
        ]  # Example fields
        if not all(field in patient_data for field in required_fields):
            return Response(
                {"error": "Missing required patient data fields."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Load the pre-trained model
            model_path = os.path.join(
                os.path.dirname(__file__),
                "models",
                "/clinical_model_20250127_011852.keras",
            )
            if not os.path.exists(model_path):
                return Response(
                    {"error": "Pre-trained model not found."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )
            model = tf.keras.models.load_model(model_path)

            # Prepare patient features for prediction
            features = self.prepare_features(patient_data)
            if features is None:
                return Response(
                    {"error": "Error preparing features for prediction."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Make prediction
            prediction = model.predict(features)

            # Interpret predictions (assuming model outputs probabilities for conditions)
            condition_names = self.get_condition_names()
            if condition_names is None:
                return Response(
                    {"error": "Condition names file not found."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

            predicted_conditions = [
                {
                    "condition": condition_names[i],
                    "likelihood": float(prob),  # Convert numpy float to standard float
                }
                for i, prob in enumerate(prediction[0])
            ]

            return Response({"predictions": predicted_conditions})

        except Exception as e:
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def prepare_features(self, patient_data):
        """
        Preprocess and prepare patient data into feature array for model prediction.
        This mirrors the preprocessing done during model training.
        """
        try:
            # Load the saved scaler
            scaler_path = os.path.join(
                os.path.dirname(__file__), "models", "standard_scaler.pkl"
            )
            if not os.path.exists(scaler_path):
                raise FileNotFoundError("Scaler file not found.")
            scaler = joblib.load(scaler_path)

            # Convert input data to DataFrame
            df = pd.DataFrame([patient_data])

            # Blood Pressure Category (same logic as training script)
            df["bp_category"] = pd.cut(
                df["sys_bp"],
                bins=[0, 120, 140, 180, 300],
                labels=["normal", "hypertensive", "severe", "crisis"],
            ).astype(
                str
            )  # Ensure string type for one-hot encoding

            # One-hot encode categorical features
            df = pd.get_dummies(df, columns=["gender", "bp_category"])

            # Ensure all expected columns are present (match training features)
            expected_columns = [
                "age",
                "bmi",
                "sys_bp",
                "dia_bp",
                "heart_rate",
                "gender_FEMALE",
                "gender_MALE",
                "bp_category_crisis",
                "bp_category_hypertensive",
                "bp_category_normal",
                "bp_category_severe",
            ]
            for col in expected_columns:
                if col not in df.columns:
                    df[col] = 0  # Add missing columns with 0

            # Select and order features to match model input order
            feature_cols = expected_columns
            features_df = df[feature_cols]

            # Scale numerical features using the saved scaler
            numerical_cols = ["age", "bmi", "sys_bp", "dia_bp", "heart_rate"]
            features_df[numerical_cols] = scaler.transform(features_df[numerical_cols])

            return features_df.values.astype(np.float32)  # Convert to numpy array

        except Exception as e:
            print(f"Error preparing features: {e}")
            return None

    def get_condition_names(self):
        """
        Load condition names from the saved JSON file (condition_names.json) from training.
        """
        condition_names_path = os.path.join(
            os.path.dirname(__file__), "models", "condition_names_20250127_011852.json"
        )
        if os.path.exists(condition_names_path):
            with open(condition_names_path, "r") as f:
                return json.load(f)
        return None
