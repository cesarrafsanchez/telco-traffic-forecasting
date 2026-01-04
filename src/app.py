# src/app.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import pandas as pd
import os


# 1. Definimos el input exacto (6 variables)
# Quitamos is_holiday porque no lo usamos en el entrenamiento final
class NetworkStatus(BaseModel):
    hour: int
    day_of_week: int
    is_weekend: int
    lag_1h: float
    lag_24h: float
    rolling_mean_3h: float


app = FastAPI(title="WOW Peru Traffic Predictor AI")

# Definir ruta del modelo
MODEL_PATH = "src/xgb_traffic_model.json"

# Variable global para el Booster
booster = None


@app.on_event("startup")
def load_model():
    global booster
    try:
        if os.path.exists(MODEL_PATH):
            # CORRECCIÓN CLAVE: Usamos el Booster nativo, no XGBRegressor
            booster = xgb.Booster()
            booster.load_model(MODEL_PATH)
            print(f"✅ CEREBRO CARGADO: Modelo leído desde {MODEL_PATH}")
        else:
            print(f"❌ ERROR: No encuentro el archivo en {MODEL_PATH}")
    except Exception as e:
        print(f"❌ ERROR CRÍTICO al cargar modelo: {e}")


@app.post("/predict")
def predict_traffic(data: NetworkStatus):
    global booster
    if not booster:
        raise HTTPException(status_code=500, detail="El modelo no está cargado.")

    try:
        # 1. Crear el DataFrame con el orden EXACTO de entrenamiento
        features_order = ['hour', 'day_of_week', 'is_weekend', 'lag_1h', 'lag_24h', 'rolling_mean_3h']

        input_data = {
            'hour': data.hour,
            'day_of_week': data.day_of_week,
            'is_weekend': data.is_weekend,
            'lag_1h': data.lag_1h,
            'lag_24h': data.lag_24h,
            'rolling_mean_3h': data.rolling_mean_3h
        }

        df_input = pd.DataFrame([input_data], columns=features_order)

        # 2. Convertir a DMatrix (Formato nativo de alto rendimiento de XGBoost)
        dmatrix = xgb.DMatrix(df_input)

        # 3. Predicción
        prediction = float(booster.predict(dmatrix)[0])

        # 4. Lógica de Negocio
        CRITICAL_THRESHOLD = 6_000_000
        alert = prediction > CRITICAL_THRESHOLD

        return {
            "predicted_mb": round(prediction, 2),
            "alert_status": "CRITICAL" if alert else "NORMAL",
            "action_required": "ACTIVATE_BACKUP" if alert else "NONE"
        }

    except Exception as e:
        # Esto nos dará el error real en el JSON si falla
        raise HTTPException(status_code=500, detail=f"Error en inferencia: {str(e)}")