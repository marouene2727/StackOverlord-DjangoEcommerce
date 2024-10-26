# comment_moderation.py

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# Exemple de données d'entraînement (vous devriez les enrichir avec des données réelles)
X = [
    "Ceci est un commentaire approprié.",
    "Ce commentaire est du spam.",
    "Un autre exemple de contenu inapproprié.",
    "J'adore cet article !",
    "C'est nul !",
]
y = [0, 1, 1, 0, 1]  # 0: approprié, 1: inapproprié

# Entraînement du modèle
model = make_pipeline(CountVectorizer(), MultinomialNB())
model.fit(X, y)

def predict_comment(content):
    return model.predict([content])[0]  # 0 pour approprié, 1 pour inapproprié
