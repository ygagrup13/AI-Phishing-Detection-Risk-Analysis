import os
import sys
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
import logging

# Ayarlar
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from features.url_features import URL_FEATURE_KEYS, extract_url_features

DATA_DIR = os.path.join(BASE_DIR, "data", "crawled_texts")
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_V2_PATH = os.path.join(MODELS_DIR, "model_v2.pkl")
SCALER_PATH = os.path.join(MODELS_DIR, "scaler_v2.pkl")

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_and_clean_datasets(max_samples_per_file=50000):
    """
    Tüm datasetleri okur, formatlar ve birleştirir.
    """
    logger.info("Datasetler okunuyor...")
    dfs = []
    
    # Dataset mapping rules: (filename, url_col, label_col, phishing_values, legitimate_values)
    datasets_info = [
        ("phishing_site_urls.csv", "URL", "Label", ["bad"], ["good"]),
        ("malicious_phish.csv", "url", "type", ["phishing", "malware", "defacement"], ["benign"]),
        ("dataset_phishing.csv", "url", "status", ["phishing"], ["legitimate"]),
        ("uci-ml-phishing-dataset.csv", "url", "Result", ["-1", -1, "1"], ["0", 1]) # UCI bazen Result kolonu içerir
    ]
    
    for filename, url_col, label_col, phish_vals, legit_vals in datasets_info:
        filepath = os.path.join(DATA_DIR, filename)
        if not os.path.exists(filepath):
            logger.warning(f"Dosya bulunamadı: {filepath}")
            continue
            
        try:
            df = pd.read_csv(filepath, nrows=max_samples_per_file, low_memory=False)
            
            # Kolon isimlerini case-insensitive kontrol et
            cols_lower = {c.lower(): c for c in df.columns}
            actual_url_col = cols_lower.get(url_col.lower())
            actual_label_col = cols_lower.get(label_col.lower())
            
            if not actual_url_col or not actual_label_col:
                # Kolonlar eşleşmezse dinamik arama
                actual_url_col = next((c for c in df.columns if "url" in c.lower()), None)
                actual_label_col = next((c for c in df.columns if c.lower() in ["label", "status", "type", "class", "result"]), None)
            
            if not actual_url_col or not actual_label_col:
                logger.warning(f"{filename} için uygun kolonlar bulunamadı.")
                continue
                
            df = df[[actual_url_col, actual_label_col]].copy()
            df.rename(columns={actual_url_col: "url", actual_label_col: "raw_label"}, inplace=True)
            df.dropna(subset=["url"], inplace=True)
            
            def map_label(val):
                val_str = str(val).strip().lower()
                if val_str in [str(v).lower() for v in phish_vals]:
                    return 1
                elif val_str in [str(v).lower() for v in legit_vals]:
                    return 0
                
                # Dinamik tahmin
                if val_str in ["1", "1.0", "phishing", "bad", "malware", "spam"]:
                    return 1
                if val_str in ["0", "0.0", "legitimate", "good", "benign", "safe", "-1"]:
                    return 0
                return -1
                
            df["label"] = df["raw_label"].apply(map_label)
            df = df[df["label"] >= 0][["url", "label"]]
            
            logger.info(f"{filename} okundu. {len(df)} geçerli satır eklendi.")
            dfs.append(df)
        except Exception as e:
            logger.error(f"{filename} okunurken hata: {e}")
            
    if not dfs:
        raise ValueError("Hiçbir veri yüklenemedi!")
        
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Temizlik: null ve duplicate URL'leri düşür
    combined_df.dropna(subset=["url"], inplace=True)
    combined_df.drop_duplicates(subset=["url"], inplace=True)
    
    logger.info(f"Birleştirilen toplam tekil URL sayısı: {len(combined_df)}")
    
    # Class imbalance çözümü için Undersampling (Örneklem büyüklüğünü dengele)
    phishing = combined_df[combined_df["label"] == 1]
    legitimate = combined_df[combined_df["label"] == 0]
    
    logger.info(f"Sınıf Dağılımı (Öncesi) - Phishing: {len(phishing)}, Legitimate: {len(legitimate)}")
    
    min_len = min(len(phishing), len(legitimate))
    # Maksimum 30.000 (hızlı eğitim için), ancak verimiz daha azsa tamamını al
    limit = min(min_len, 30000) 
    
    phishing_sampled = phishing.sample(n=limit, random_state=42)
    legit_sampled = legitimate.sample(n=limit, random_state=42)
    
    final_df = pd.concat([phishing_sampled, legit_sampled], ignore_index=True)
    final_df = final_df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    logger.info(f"Sınıf Dağılımı (Sonrası) - Phishing: {len(phishing_sampled)}, Legitimate: {len(legit_sampled)}")
    
    return final_df

def feature_engineering(df):
    """
    URL'lerden sayısal özellikleri çıkarır.
    """
    logger.info("Feature engineering başlatılıyor... (Bu işlem biraz sürebilir)")
    
    def safe_extract(url):
        try:
            return extract_url_features(str(url))
        except:
            return {k: 0 for k in URL_FEATURE_KEYS}
            
    # Hızlı extraction (List comprehension genelde pandas apply'dan hızlıdır)
    features_list = [safe_extract(u) for u in df["url"].values]
    features_df = pd.DataFrame(features_list)[list(URL_FEATURE_KEYS)]
    
    return features_df, df["label"].values

from sklearn.pipeline import Pipeline

def train_and_evaluate(X, y):
    logger.info("Train/Val/Test split yapılıyor (%70 / %15 / %15)")
    X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.30, random_state=42, stratify=y)
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.50, random_state=42, stratify=y_temp)
    
    models = {
        "Logistic Regression": Pipeline([
            ("scaler", StandardScaler()),
            ("model", LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced'))
        ]),
        "Random Forest": Pipeline([
            # Tree models don't strictly need scaling, but it's safe to include if we want a uniform pipeline interface
            ("model", RandomForestClassifier(n_estimators=150, max_depth=25, min_samples_leaf=1, random_state=42, n_jobs=-1, class_weight='balanced'))
        ]),
        "XGBoost-like (HistGradientBoosting)": Pipeline([
            ("model", RandomForestClassifier(n_estimators=200, max_depth=30, random_state=42, n_jobs=-1)) # Using RF again but deeper as alternative since xgboost might not be installed
        ])
    }
    
    best_model = None
    best_f1 = 0
    best_name = ""
    report_lines = ["# Model Değerlendirme Raporu\n"]
    
    for name, model in models.items():
        logger.info(f"Eğitiliyor: {name}")
        
        model.fit(X_train, y_train)
        
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='f1')
        logger.info(f"{name} - CV F1 Skoru: {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
        
        y_pred_val = model.predict(X_val)
        val_f1 = f1_score(y_val, y_pred_val)
        
        report_lines.append(f"## {name}")
        report_lines.append(f"- **Validation F1-Score**: {val_f1:.4f}")
        report_lines.append(f"- **CV F1-Score (5-fold)**: {cv_scores.mean():.4f}")
        
        if val_f1 > best_f1:
            best_f1 = val_f1
            best_model = model
            best_name = name
            
    logger.info(f"En iyi model {best_name} seçildi. Test seti ile değerlendiriliyor...")
    
    y_pred_test = best_model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred_test)
    prec = precision_score(y_test, y_pred_test)
    rec = recall_score(y_test, y_pred_test)
    f1 = f1_score(y_test, y_pred_test)
    cm = confusion_matrix(y_test, y_pred_test)
    
    tn, fp, fn, tp = cm.ravel()
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0
    
    logger.info(f"TEST Accuracy : {acc:.4f}")
    logger.info(f"TEST Precision: {prec:.4f}")
    logger.info(f"TEST Recall   : {rec:.4f}")
    logger.info(f"TEST F1-Score : {f1:.4f}")
    logger.info(f"TEST False Positive Rate: {fpr:.4f}")
    
    report_lines.append("\n## En İyi Model: " + best_name)
    report_lines.append("### Test Seti Sonuçları")
    report_lines.append(f"- **Accuracy**: {acc:.4f}")
    report_lines.append(f"- **Precision**: {prec:.4f}")
    report_lines.append(f"- **Recall**: {rec:.4f}")
    report_lines.append(f"- **F1-Score**: {f1:.4f}")
    report_lines.append(f"- **False Positive Rate**: {fpr:.4f}")
    report_lines.append("### Confusion Matrix")
    report_lines.append(f"```\n{cm}\n```")
    report_lines.append(f"TN: {tn}, FP: {fp}, FN: {fn}, TP: {tp}")
    
    with open(os.path.join(BASE_DIR, "evaluation_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
        
    return best_model, best_name

def save_model_artifact(model):
    if not os.path.exists(MODELS_DIR):
        os.makedirs(MODELS_DIR)
        
    joblib.dump(model, MODEL_V2_PATH)
    logger.info(f"Final model başarıyla kaydedildi: {MODEL_V2_PATH}")

if __name__ == "__main__":
    df = load_and_clean_datasets(max_samples_per_file=60000)
    X, y = feature_engineering(df)
    best_model, best_name = train_and_evaluate(X, y)
    save_model_artifact(best_model)
