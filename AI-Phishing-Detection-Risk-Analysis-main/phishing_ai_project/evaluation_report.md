# Model Değerlendirme Raporu

## Logistic Regression
- **Validation F1-Score**: 0.7670
- **CV F1-Score (5-fold)**: 0.7663
## Random Forest
- **Validation F1-Score**: 0.8963
- **CV F1-Score (5-fold)**: 0.8959
## XGBoost-like (HistGradientBoosting)
- **Validation F1-Score**: 0.8969
- **CV F1-Score (5-fold)**: 0.8965

## En İyi Model: XGBoost-like (HistGradientBoosting)
### Test Seti Sonuçları
- **Accuracy**: 0.9212
- **Precision**: 0.9347
- **Recall**: 0.8601
- **F1-Score**: 0.8958
- **False Positive Rate**: 0.0391
### Confusion Matrix
```
[[62554  2545]
 [ 5924 36413]]
```
TN: 62554, FP: 2545, FN: 5924, TP: 36413