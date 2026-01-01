import joblib, json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

def load_data(path="data/intent_labeled.jsonl"):
    texts, labels = [], []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            texts.append(obj["text"])
            labels.append(obj["label"])
    return texts, labels

if __name__ == "__main__":
    texts, labels = load_data()
    vec = TfidfVectorizer(analyzer="char", ngram_range=(3,5), min_df=2)
    X = vec.fit_transform(texts)
    clf = LogisticRegression(max_iter=200)
    clf.fit(X, labels)
    joblib.dump((vec, clf), "models/intent.joblib")
    print("saved models/intent.joblib")