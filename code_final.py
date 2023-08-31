# -*- coding: utf-8 -*-
"""code_final.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1D_IluS0gRSMoHQY4uus8m6hc2SMv3ytc
"""

# Commented out IPython magic to ensure Python compatibility.
import numpy as np
import pandas as pd
import seaborn as sns
import scikitplot as skplt
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from bs4 import BeautifulSoup
import re
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.pipeline import Pipeline
from imblearn.over_sampling import SMOTE
import warnings
warnings.filterwarnings("ignore")
# %matplotlib inline

from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_extraction.text import TfidfTransformer,CountVectorizer

from sklearn.metrics import precision_score, f1_score, recall_score, accuracy_score, roc_auc_score, roc_curve, classification_report,confusion_matrix


import os
for dirname, _, filenames in os.walk('/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))

import nltk
nltk.download("popular")

!pip install scikit-plot

train_df = pd.read_csv('/content/train.tsv',delimiter='\t')
test_df = pd.read_csv('/content/test.tsv',delimiter='\t')

train_df.head()

train_df.shape

train_df.isnull().sum()

sns.countplot(x='Sentiment',data=train_df)

#label mapping
labels = ["Negative","Somewhat negative","Neutral","Somewhat positive","Positive"]
sentiment_code = [0,1,2,3,4]

labels_df = pd.DataFrame({"Label":labels,"Code":sentiment_code})

labels_df

train_df['Phrase Length'] = train_df['Phrase'].apply(len)

sns.distplot(train_df['Phrase Length'],bins=80,kde=False,hist_kws={"edgecolor":"blue"})

train_df.hist(column='Phrase Length',by='Sentiment',bins=80,edgecolor='black')

X = train_df["Phrase"].tolist()
Y = train_df["Sentiment"].apply(lambda i: 0 if i <= 2 else 1)

sns.set(style='darkgrid')
sns.boxplot(train_df.Sentiment)

sns.set(style='darkgrid')
sns.boxplot(train_df.PhraseId)

"""**Preprocess Texts**
Some typical text preprocessing steps will be performed:

Removal of markup, html
Obtain only words in lower case
Lemmatization
Removal of stop words
"""

lemmatizer = WordNetLemmatizer()
def proc_text(messy): #input is a single string
    first = BeautifulSoup(messy, "lxml").get_text() #gets text without tags or markup, remove html
    second = re.sub("[^a-zA-Z]"," ",first) #obtain only letters
    third = second.lower().split() #obtains a list of words in lower case
    fourth = set([lemmatizer.lemmatize(str(x)) for x in third]) #lemmatizing
    stops = set(stopwords.words("english")) #faster to search through a set than a list
    almost = [w for w in fourth if not w in stops] #remove stop words
    final = " ".join(almost)
    return final

X = [proc_text(i) for i in X]

"""**Train Test Split**"""

X_train, X_test, y_train, y_test = train_test_split(X, Y, random_state=100, test_size=0.2, stratify=Y)
print("Training Set has {} Positive Labels and {} Negative Labels".format(sum(y_train), len(y_train) - sum(y_train)))
print("Test Set has {} Positive Labels and {} Negative Labels".format(sum(y_test), len(y_test) - sum(y_test)))

"""**Feature Extraction and Train Model using Decision Tree**


Features will be built using tfidf.

Model selected here is the Decision Tree, larger weight is given to the positive class since the number of samples with positive labels are significantly smaller. The weights would be calculated as

Wp=NnNp,
 
where  Wp  is a float indicating the weight for positive class,  Nn  is the number of negative samples and  Np  is the number of positive samples.
 The output of this computation will be included in the class_weight parameter of DecisionTreeClassifier.

These steps will be collated by using sklearn's Pipeline.
"""

pos_weights = (len(y_train) - sum(y_train)) / (sum(y_train)) 
pipeline_tf = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('classifier', DecisionTreeClassifier(random_state=100, class_weight={0: 1, 1: pos_weights}))
])

pipeline_tf.fit(X_train, y_train)

predictions = pipeline_tf.predict(X_test)
predicted_proba = pipeline_tf.predict_proba(X_test)

"""**Feature Extraction and Train Model using Naive Bayes**"""

pos_weights = (len(y_train) - sum(y_train)) / (sum(y_train)) 
pipeline_tf_NB = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('classifier', MultinomialNB())
])

pipeline_tf_NB.fit(X_train, y_train)

predictions_NB = pipeline_tf_NB.predict(X_test)
predicted_proba_NB = pipeline_tf_NB.predict_proba(X_test)

"""**Feature Extraction and Train Model using Logistic Regression**"""

pos_weights = (len(y_train) - sum(y_train)) / (sum(y_train)) 
pipeline_tf_LR = Pipeline([
    ('tfidf', TfidfVectorizer()),
    ('classifier', LogisticRegression())
])

pipeline_tf_LR.fit(X_train, y_train)

predictions_LR = pipeline_tf_LR.predict(X_test)
predicted_proba_LR = pipeline_tf_LR.predict_proba(X_test)

"""**Accuracy ROC score before Threshold**"""

print("Accuracy Score Before Thresholding Decision Tree: {}".format(accuracy_score(y_test, predictions)))
print("Accuracy Score Before Thresholding Naive Bayes: {}".format(accuracy_score(y_test, predictions_NB)))
print("Accuracy Score Before Thresholding Logistic Regression: {}".format(accuracy_score(y_test, predictions_LR)))
print("---------------------------------------------------------------------------------------")
print("ROC AUC Score Decison Tree: {}".format(roc_auc_score(y_test, predicted_proba[:, -1])))
print("ROC AUC Score Naive Bayes: {}".format(roc_auc_score(y_test, predicted_proba_NB[:, -1])))
print("ROC AUC Score Logistic Regression: {}".format(roc_auc_score(y_test, predicted_proba_LR[:, -1])))

"""**ROC Curve**
The curve is plots values of true positive rates (y-axis) against those of false positive rates (x-axis) and these values are plotted at various probability thresholds.

There can be two ways of obtaining a more optimal probability threshold for the positive class:

Youden's J Statistic
Its computed as
J=TruePositiveRate+TrueNegativeRate−1=TruePositiveRate−FalsePositiveRate
Find the maximum difference between true positive rate and false positive rate and the probability threshold tied tagged to this largest difference would be the selected one
Euclidean Distance
The most optimal ROC curve would be one that leans towards the top left of the plot, i.e. true positive rate of 1 and false positive rate of 0.
Select the probability threshold as the most optimal one if its true positive rate and false positive rate are closest to the ones mentioned in the previous point in terms of Euclidean distance, i.e.
d(tpr,fpr)=(tpr1−tpr2)2+fpr1−fpr2)2−−−−−−−−−−−−−−−−−−−−−−−−√.

**ROC CURVE FOR DECISION TREE**
"""

false_pos_rate, true_pos_rate, proba = roc_curve(y_test, predicted_proba[:, -1])
plt.figure()
plt.plot([0,1], [0,1], linestyle="--") # plot random curve
plt.plot(false_pos_rate, true_pos_rate, marker=".", label=f"AUC = {roc_auc_score(y_test, predicted_proba[:, -1])}")
plt.title("ROC Curve")
plt.ylabel("True Positive Rate")
plt.xlabel("False Positive Rate")
plt.legend(loc="lower right")

"""**ROC CURVE FOR NAIVE BAYES**"""

false_pos_rate, true_pos_rate, proba = roc_curve(y_test, predicted_proba_NB[:, -1])
plt.figure()
plt.plot([0,1], [0,1], linestyle="--") # plot random curve
plt.plot(false_pos_rate, true_pos_rate, marker=".", label=f"AUC = {roc_auc_score(y_test, predicted_proba_NB[:, -1])}")
plt.title("ROC Curve")
plt.ylabel("True Positive Rate")
plt.xlabel("False Positive Rate")
plt.legend(loc="lower right")

"""**ROC CURVE FOR LOGESTIC REGRESSION**"""

false_pos_rate, true_pos_rate, proba = roc_curve(y_test, predicted_proba_LR[:, -1])
plt.figure()
plt.plot([0,1], [0,1], linestyle="--") # plot random curve
plt.plot(false_pos_rate, true_pos_rate, marker=".", label=f"AUC = {roc_auc_score(y_test, predicted_proba_LR[:, -1])}")
plt.title("ROC Curve")
plt.ylabel("True Positive Rate")
plt.xlabel("False Positive Rate")
plt.legend(loc="lower right")

"""**Evaluate Model (After Thresholding) DECISION TREE**



We can see that the optimal probability threshold managed to suppress the number of false positives
"""

optimal_proba_cutoff = sorted(list(zip(np.abs(true_pos_rate - false_pos_rate), proba)), key=lambda i: i[0], reverse=True)[0][1]
roc_predictions = [1 if i >= optimal_proba_cutoff else 0 for i in predicted_proba[:, -1]]

print("Accuracy Score Before and After Thresholding:")
print("{}, {}".format(classification_report(y_test,predictions), classification_report(y_test, roc_predictions)))

"""**Confusion matrix for Decision Tree**"""

y_actual = pd.Series(y_test)
y_predict_tf = pd.Series(predictions)
cm_dt=confusion_matrix(y_test,y_predict_tf)
#plot our confusion matrix
skplt.metrics.plot_confusion_matrix(y_actual,y_predict_tf,normalize=False,figsize=(8,8))
plt.show()

"""**Evaluate Model (After Thresholding) NAIVE BAYES**"""

optimal_proba_cutoff = sorted(list(zip(np.abs(true_pos_rate - false_pos_rate), proba)), key=lambda i: i[0], reverse=True)[0][1]
roc_predictions_NB = [1 if i >= optimal_proba_cutoff else 0 for i in predicted_proba_NB[:, -1]]

print("Accuracy Score Before and After Thresholding:")
print("{}, {}".format(classification_report(y_test,predictions_NB), classification_report(y_test, roc_predictions_NB)))

"""**Confusion matrix for Naive Bayes**"""

y_actual = pd.Series(y_test)
y_predict_tf_NB = pd.Series(predictions_NB)
cm_dt=confusion_matrix(y_actual,y_predict_tf_NB)
#plot our confusion matrix
skplt.metrics.plot_confusion_matrix(y_actual,y_predict_tf_NB,normalize=False,figsize=(8,8))
plt.show()

"""**Evaluate Model (After Thresholding) LOGISTIC REGRESSION**"""

optimal_proba_cutoff = sorted(list(zip(np.abs(true_pos_rate - false_pos_rate), proba)), key=lambda i: i[0], reverse=True)[0][1]
roc_predictions_LR = [1 if i >= optimal_proba_cutoff else 0 for i in predicted_proba_LR[:, -1]]

print("Accuracy Score Before and After Thresholding:")
print("{}, {}".format(classification_report(y_test,predictions_LR), classification_report(y_test, roc_predictions_LR)))

"""**Confusion Matrix of Logistic Regression**"""

y_actual = pd.Series(y_test)
y_predict_tf_LR = pd.Series(predictions_LR)
cm_dt=confusion_matrix(y_actual,y_predict_tf_LR)
#plot our confusion matrix
skplt.metrics.plot_confusion_matrix(y_actual,y_predict_tf_LR,normalize=False,figsize=(8,8))
plt.show()