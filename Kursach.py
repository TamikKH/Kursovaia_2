import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from xgboost import XGBRegressor, XGBClassifier
import warnings

warnings.filterwarnings('ignore')


class AgriculturalInformationSystem:

    def __init__(self, data_path):
        self.data = pd.read_csv(data_path)
        self.models = {}

    def clean_data(self):
        self.data_clean = self.data.copy()

        # Удаляем строки без урожайности
        self.data_clean = self.data_clean.dropna(subset=['Yield_tons_per_hectare'])

        # Числовые признаки
        for col in self.data_clean.select_dtypes(include=[np.number]).columns:
            self.data_clean[col] = self.data_clean[col].fillna(self.data_clean[col].median())

        # Категориальные
        for col in self.data_clean.select_dtypes(include=['object']).columns:
            self.data_clean[col] = self.data_clean[col].fillna('Unknown')

        return self

    def train_models(self):

        # One-Hot Encoding
        self.encoded_data = pd.get_dummies(self.data_clean, drop_first=True)

        # --- Регрессия (урожайность) ---
        feature_cols = [col for col in self.encoded_data.columns
                        if col not in ['Yield_tons_per_hectare', 'Best_Crop']]

        X = self.encoded_data[feature_cols]
        y = self.encoded_data['Yield_tons_per_hectare']

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )

        model = XGBRegressor(
            n_estimators=500,
            max_depth=6,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42
        )

        model.fit(X_train, y_train)

        pred = model.predict(X_test)

        print("\n=== РЕГРЕССИЯ ===")
        print("R2:", r2_score(y_test, pred))
        print("RMSE:", np.sqrt(mean_squared_error(y_test, pred)))

        self.models['yield'] = model
        self.feature_names = X.columns

        # --- Классификация (культура) ---
        if 'Best_Crop' in self.data_clean.columns:

            self.data_clean['Best_Crop'] = self.data_clean['Best_Crop'].astype('category')
            self.data_clean['Best_Crop_encoded'] = self.data_clean['Best_Crop'].cat.codes

            yc = self.data_clean['Best_Crop_encoded']

            Xc = pd.get_dummies(self.data_clean.drop(columns=['Best_Crop', 'Best_Crop_encoded']), drop_first=True)

            Xc = Xc.reindex(columns=self.feature_names, fill_value=0)

            Xc_train, Xc_test, yc_train, yc_test = train_test_split(
                Xc, yc, test_size=0.2, random_state=42
            )

            clf = XGBClassifier(
                n_estimators=300,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                use_label_encoder=False,
                eval_metric='mlogloss'
            )

            clf.fit(Xc_train, yc_train)

            pred_clf = clf.predict(Xc_test)

            print("\n=== КЛАССИФИКАЦИЯ ===")
            print("Accuracy:", accuracy_score(yc_test, pred_clf))

            self.models['crop'] = clf
            self.crop_mapping = dict(enumerate(self.data_clean['Best_Crop'].cat.categories))

        return self

    def predict_yield(self, features):
        df = pd.DataFrame([features])
        df = pd.get_dummies(df)

        df = df.reindex(columns=self.feature_names, fill_value=0)

        return self.models['yield'].predict(df)[0]

    def recommend_crop(self, features):
        if 'crop' not in self.models:
            return "Нет данных"

        df = pd.DataFrame([features])
        df = pd.get_dummies(df)

        df = df.reindex(columns=self.feature_names, fill_value=0)

        pred = self.models['crop'].predict(df)[0]

        return self.crop_mapping[pred]


def main(test):
    system = AgriculturalInformationSystem("agriculture_dataset.csv")
    system.clean_data()
    system.train_models()

    yield_pred = system.predict_yield(test)
    crop_pred = system.recommend_crop(test)

    return yield_pred, crop_pred

