# -*- coding: utf-8 -*-
"""cai.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nAETPYIiYR_np2e2duqkTAarl3d_VjG5
"""

# for cai classification (fs+1 & fs-1)

import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import roc_curve, auc, accuracy_score, precision_score, recall_score, f1_score
import numpy as np
from imblearn.under_sampling import RandomUnderSampler

# file_path = "/content/drive/MyDrive/fs/fs+1top10.xlsx"
# file_path = "/content/drive/MyDrive/fs/fs+1_o.xlsx"
# file_path = "/content/drive/MyDrive/fs/fs+1exp.xlsx"
# file_path = "/content/drive/MyDrive/fs/fs+1set18fea.xlsx"
#file_path = "/content/drive/MyDrive/fs/fs+1lowfea.xlsx"
# file_path = "/content/drive/MyDrive/fs/fs+1low10_type.xlsx"
# file_path = "/content/drive/MyDrive/fs/fs+1_cai_binary.xlsx"
# file_path = "/content/drive/MyDrive/fs/fs+1_cai_binary_top10.xlsx"
# file_path = "/content/drive/MyDrive/fs/fs+1_cai_binary_low10.xlsx"
file_path = "/content/drive/MyDrive/fs/fs-1_cai_binary.xlsx"
# file_path = "/content/drive/MyDrive/fs/fs-1_cai_binary_top20.xlsx"
# file_path = "/content/drive/MyDrive/fs/fs-1_cai_binary_low20.xlsx"


excel_data = pd.ExcelFile(file_path)

classifiers = [
    LogisticRegression(random_state=1234, max_iter=1000),
    GaussianNB(),
    SVC(probability=True),
    # KNeighborsClassifier(),
    # DecisionTreeClassifier(random_state=1234),
    RandomForestClassifier(random_state=1234),
    AdaBoostClassifier(random_state=1234),
    GradientBoostingClassifier(random_state=1234),
    XGBClassifier(random_state=1234)
]

# Define the mean false positive rate for ROC computation
mean_fpr = np.linspace(0, 1, 100)
# Dictionary to store interpolated true positive rates for each classifier
mean_tprs = {cls.__class__.__name__: [] for cls in classifiers}
# Dictionary to store evaluation metrics for each classifier
metrics = {cls.__class__.__name__: {'accuracy': [], 'precision': [], 'recall': [], 'f1': []} for cls in classifiers}

# this section parses different sheets of the excel file and train / test the model for each sheet
for set_number in range(1, 16):
    sheet_name = f'set{set_number}'
    df = excel_data.parse(sheet_name)
    df.dropna(inplace=True)

    # X1 = pd.get_dummies(df.drop(columns=['type', 'count','GC%']), drop_first=True)
    # y1 = df['type']
    # label_mapping = {'essential': 0, 'non-essential': 1}
    # y1 = y1.map(label_mapping)
    # undersample = RandomUnderSampler(sampling_strategy='majority')
    # X, y = undersample.fit_resample(X1, y1)
    X = pd.get_dummies(df.drop(columns=['type', 'count','GC%','CAI','CAI_o']), drop_first=True)
    y = df['CAI']
    # label_mapping = {'essential': 0, 'non-essential': 1}
    # y = y.map(label_mapping)

    # the classification loop iterates for 10 times to train the model
    num_iterations = 10
    for cls in classifiers:
        for _ in range(num_iterations):
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=1234)   # train test split

            model = cls.fit(X_train, y_train)
            y_proba = model.predict_proba(X_test)[:, 1]   # Predict probabilities for ROC curve computation
            y_pred = model.predict(X_test)   # Predict labels for evaluation metrics

            # Compute ROC curve and interpolate TPR
            fpr, tpr, _ = roc_curve(y_test, y_proba)
            interp_tpr = np.interp(mean_fpr, fpr, tpr)
            interp_tpr[0] = 0.0
            mean_tprs[cls.__class__.__name__].append(interp_tpr)

            # Compute and store evaluation metrics
            metrics[cls.__class__.__name__]['accuracy'].append(accuracy_score(y_test, y_pred))
            metrics[cls.__class__.__name__]['precision'].append(precision_score(y_test, y_pred))
            metrics[cls.__class__.__name__]['recall'].append(recall_score(y_test, y_pred))
            metrics[cls.__class__.__name__]['f1'].append(f1_score(y_test, y_pred))

# average true positive rates for each classifier
mean_tpr_dict = {}
for cls_name, tpr_list in mean_tprs.items():
    mean_tpr = np.mean(tpr_list, axis=0)
    mean_tpr_dict[cls_name] = mean_tpr

# Plot average ROC curves for each classifier
plt.figure(figsize=(10, 6))
for cls_name, mean_tpr in mean_tpr_dict.items():
    mean_auc = auc(mean_fpr, mean_tpr)
    plt.plot(mean_fpr, mean_tpr, lw=2, alpha=0.8,
             label=f'{cls_name} (AUC = {mean_auc * 100:.2f}%)')
# To Plot chance line
plt.plot([0, 1], [0, 1], linestyle='--', lw=2, color='r', label='Chance', alpha=.8)

plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Average ROC curve across sets')
plt.legend(loc='lower right')

plt.show()

# Print average metrics for each classifier
for cls_name, metric_dict in metrics.items():
    avg_accuracy = np.mean(metric_dict['accuracy'])
    avg_precision = np.mean(metric_dict['precision'])
    avg_recall = np.mean(metric_dict['recall'])
    avg_f1 = np.mean(metric_dict['f1'])
    print(f'{cls_name}:')
    print(f'  Accuracy: {avg_accuracy:.4f}')
    print(f'  Precision: {avg_precision:.4f}')
    print(f'  Recall: {avg_recall:.4f}')
    print(f'  F1 Score: {avg_f1:.4f}\n')

