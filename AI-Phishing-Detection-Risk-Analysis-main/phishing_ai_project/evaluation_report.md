# Model Değerlendirme Raporu

## Logistic Regression
- **Validation F1-Score**: 0.7632
- **CV F1-Score (5-fold)**: 0.7677
## Random Forest
- **Validation F1-Score**: 0.8762
- **CV F1-Score (5-fold)**: 0.8707
## XGBoost-like (HistGradientBoosting)
- **Validation F1-Score**: 0.8737
- **CV F1-Score (5-fold)**: 0.8703

## En İyi Model: Random Forest
### Test Seti Sonuçları
- **Accuracy**: 0.8814
- **Precision**: 0.9123
- **Recall**: 0.8440
- **F1-Score**: 0.8768
- **False Positive Rate**: 0.0811
### Confusion Matrix
```
[[4135  365]
 [ 702 3798]]
```
TN: 4135, FP: 365, FN: 702, TP: 3798