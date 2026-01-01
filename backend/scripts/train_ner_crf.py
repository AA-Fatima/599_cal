import joblib, json
import sklearn_crfsuite
from sklearn_crfsuite import metrics

def word2features(sent, i):
    w = sent[i][0]
    return {
        "w": w.lower(),
        "suf3": w[-3:],
        "is_alpha": w.isalpha(),
        "is_digit": w.isdigit(),
    }

def sent2features(sent):
    return [word2features(sent, i) for i in range(len(sent))]

def load_data(path="data/ner_labeled.jsonl"):
    # Each line: {"tokens": [...], "labels": [...]} BIO
    sents = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            obj = json.loads(line)
            sents.append(list(zip(obj["tokens"], obj["labels"])))
    X = [sent2features(s) for s in sents]
    y = [[lbl for _, lbl in s] for s in sents]
    return X, y

if __name__ == "__main__":
    X, y = load_data()
    crf = sklearn_crfsuite.CRF(
        algorithm="lbfgs",
        c1=0.1,
        c2=0.1,
        max_iterations=100,
        all_possible_transitions=True
    )
    crf.fit(X, y)
    joblib.dump(crf, "models/ner_crf.joblib")
    print("saved models/ner_crf.joblib")