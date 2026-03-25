import os
import flwr as fl
import lightgbm as lgb
import pandas as pd
import numpy as np
from sklearn.metrics import f1_score
import privacy


# LightGBM ne stocke pas de poids au sens reseau de neurones.
# On serialise le modele en bytes et on l'envoie comme un vecteur numpy.
# L'agregateur fait une moyenne ponderee des predictions (soft voting).


def model_to_params(model):
    """Convertit le booster LightGBM en tableau numpy serialisable."""
    import tempfile, os
    with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
        tmp = f.name
    model.booster_.save_model(tmp)
    with open(tmp, "rb") as f:
        data = f.read()
    os.unlink(tmp)
    return [np.frombuffer(data, dtype=np.uint8)]


def params_to_bytes(params):
    """Reconstruit les bytes du modele depuis les parametres Flower."""
    return params[0].tobytes()


class BankFraudClient(fl.client.NumPyClient):

    def __init__(self):
        self.bank_id    = os.environ["BANK_ID"]
        train_path      = os.environ["TRAIN_PATH"]
        test_path       = os.environ["TEST_PATH"]

        train = pd.read_parquet(train_path)
        test  = pd.read_parquet(test_path)

        self.X_train = train.drop("isFraud", axis=1).values.astype(np.float32)
        self.y_train = train["isFraud"].values
        self.X_test  = test.drop("isFraud",  axis=1).values.astype(np.float32)
        self.y_test  = test["isFraud"].values

        self.model = lgb.LGBMClassifier(
            n_estimators=100,
            class_weight="balanced",
            random_state=42,
            verbose=-1,
        )
        # Entrainnement initial sur les donnees locales
        self.model.fit(self.X_train, self.y_train)
        print(f"[{self.bank_id}] Modele initialise")

    def get_parameters(self, config):
        return model_to_params(self.model)

    def fit(self, parameters, config):
        self.model.fit(self.X_train, self.y_train)
        
        # Récupérer les vrais paramètres
        raw_params = model_to_params(self.model)
        
        # Appliquer DP sur les paramètres AVANT envoi
        protected_params = privacy.apply_dp_noise(raw_params, sigma=0.1, C=1.0)
        
        print(f"[{self.bank_id}] DP appliqué sur les poids ✓")
        return protected_params, len(self.X_train), {}

    def evaluate(self, parameters, config):
        y_pred = self.model.predict(self.X_test)
        f1 = f1_score(self.y_test, y_pred, zero_division=0)
        print(f"[{self.bank_id}] F1-Score : {f1:.4f}")
        return 0.0, len(self.X_test), {"f1": f1}


fl.client.start_client(
    server_address=os.environ["SERVER_ADDRESS"],
    client=BankFraudClient().to_client(),
    root_certificates=open("/certs/ca.crt", "rb").read(),
)
