"""Offline temporal benchmark. Publishes aggregates only; see docs/EVALUATION_PLAN.md."""
from pathlib import Path
import hashlib
import json
import platform
import time
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, roc_auc_score
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]

def wilson(caught, total):
    if not total:
        return None
    z = 1.96
    p, d = caught / total, 1 + z*z / total
    center = (p + z*z/(2*total))/d
    radius = z * np.sqrt(p*(1-p)/total + z*z/(4*total*total))/d
    return [float(max(0, center-radius)), float(min(1, center+radius))]

def temporal_split(frame, train_fraction, val_fraction):
    frame = frame.sort_values('Time', kind='stable').reset_index(drop=True)
    a, b = int(len(frame)*train_fraction), int(len(frame)*(train_fraction+val_fraction))
    while a > 0 and frame.Time.iloc[a-1] == frame.Time.iloc[a]:
        a -= 1
    while b > a and frame.Time.iloc[b-1] == frame.Time.iloc[b]:
        b -= 1
    return frame.iloc[:a].copy(), frame.iloc[a:b].copy(), frame.iloc[b:].copy()

def metrics(y, score, k):
    order = np.argsort(-score, kind='stable')
    caught = int(y[order[:k]].sum())
    return dict(k=k, caught=caught, legitimate=k-caught, missed=int(y.sum())-caught,
                precision=caught/k if k else None, recall=caught/int(y.sum()) if y.sum() else None,
                interval=wilson(caught, int(y.sum())))

def curve(y, score, amount):
    order = np.argsort(-score, kind='stable')
    count, money = np.cumsum(y[order]), np.cumsum(amount[order])
    result = []
    for step in range(51):
        percent = step/10
        k = int(np.floor(len(y)*percent/100+1e-9))
        caught = int(count[k-1]) if k else 0
        result.append(dict(percent=percent, k=k, caught=caught, legitimate=k-caught,
                           missed=int(y.sum())-caught, precision=caught/k if k else None,
                           recall=caught/int(y.sum()), interval=wilson(caught, int(y.sum())),
                           selectedAmount=float(money[k-1]) if k else 0))
    return result

def features(frame, amount=True):
    x = frame[[f'V{i}' for i in range(1,29)]].to_numpy()
    return np.column_stack((x, np.log1p(frame.Amount))) if amount else x

def run():
    config = json.loads((ROOT/'evaluation/config.json').read_text())
    raw_path = ROOT/config['dataset']
    if not raw_path.exists():
        raise SystemExit('Obtain creditcard.csv from the cited ULB dataset and place it in data/raw/. No credentials are read by this benchmark.')
    start = time.perf_counter()
    frame = pd.read_csv(raw_path)
    assert len(frame) == 284807 and int(frame.Class.sum()) == 492, 'Unexpected dataset; check its provenance.'
    assert np.isfinite(frame.to_numpy()).all() and set(frame.Class.unique()) == {0, 1}
    train, val, test = temporal_split(frame, config['train_fraction'], config['validation_fraction'])
    ytrain, yval, y = (part.Class.to_numpy(dtype=int) for part in (train,val,test))
    k = int(len(test)*config['capacity_percent']/100)
    scores, validation, repeats = {}, {}, []
    for seed in config['seeds']:
        for ident, use_amount in [('logistic', True), ('no_amount', False)]:
            scaler = StandardScaler().fit(features(train, use_amount))
            model = LogisticRegression(**config['logistic'], random_state=seed)
            model.fit(scaler.transform(features(train, use_amount)), ytrain)
            vs = model.decision_function(scaler.transform(features(val, use_amount)))
            ts = model.decision_function(scaler.transform(features(test, use_amount)))
            repeats.append(dict(model=ident, seed=seed, average_precision=float(average_precision_score(y, ts)), **metrics(y, ts, k)))
            if seed == config['seed']:
                scores[ident] = ts
                validation[ident] = float(average_precision_score(yval, vs))
        scaler = StandardScaler().fit(features(train))
        xtrain = scaler.transform(features(train))
        anomaly = IsolationForest(**config['isolation_forest'], random_state=seed)
        anomaly.fit(xtrain[ytrain == 0])
        ts = -anomaly.score_samples(scaler.transform(features(test)))
        repeats.append(dict(model='isolation', seed=seed, average_precision=float(average_precision_score(y, ts)), **metrics(y, ts, k)))
        if seed == config['seed']:
            scores['isolation'] = ts
    selected = max(validation, key=validation.get)
    scores['amount'] = test.Amount.to_numpy()
    names = {'logistic': 'Logistic regression', 'no_amount': 'Logistic · no amount', 'isolation': 'Isolation Forest', 'amount': 'Largest amount first'}
    strategies = [dict(id=ident, name=names[ident], average_precision=float(average_precision_score(y, s)),
                       roc_auc=float(roc_auc_score(y, s)), primary=metrics(y, s, k), points=curve(y, s, test.Amount.to_numpy()))
                  for ident, s in scores.items()]
    strategies.sort(key=lambda s: s['id'] != selected)
    selected_score = scores[selected]
    selected_metric, baseline_metric = metrics(y, selected_score, k), metrics(y, scores['isolation'], k)
    # Paired bootstrap of fixed test scores; correlated rows remain a documented limitation.
    rng, deltas = np.random.default_rng(config['seed']), []
    for _ in range(config['bootstrap_samples']):
        ix = rng.integers(0, len(y), len(y))
        if y[ix].sum():
            deltas.append(metrics(y[ix], selected_score[ix], k)['recall']-metrics(y[ix], scores['isolation'][ix], k)['recall'])
    errors = []
    reviewed = np.zeros(len(y), dtype=bool)
    reviewed[np.argsort(-selected_score, kind='stable')[:k]] = True
    for label, mask in [('Amount ≤ 25', test.Amount.to_numpy() <= 25), ('Amount 25–100', (test.Amount.to_numpy()>25)&(test.Amount.to_numpy()<=100)), ('Amount > 100', test.Amount.to_numpy()>100), ('Earlier test half', np.arange(len(y))<len(y)//2), ('Later test half', np.arange(len(y))>=len(y)//2)]:
        fraud = int(y[mask].sum())
        caught = int(y[mask & reviewed].sum())
        errors.append(dict(segment=label, rows=int(mask.sum()), fraud=fraud, caught=caught, missed=fraud-caught, recall=caught/fraud if fraud else None))
    feature_cols = [c for c in frame if c not in ['Time', 'Class']]
    hashes = [pd.util.hash_pandas_object(part[feature_cols], index=False) for part in (train,val,test)]
    duplicates = dict(train_to_val=int(hashes[1].isin(set(hashes[0])).sum()), train_to_test=int(hashes[2].isin(set(hashes[0])).sum()), val_to_test=int(hashes[2].isin(set(hashes[1])).sum()))
    # Remove test rows whose features occur in either earlier partition and re-evaluate.
    novel = ~hashes[2].isin(set(hashes[0]) | set(hashes[1])).to_numpy()
    deduplicated = metrics(y[novel], selected_score[novel], int(novel.sum()*config['capacity_percent']/100))
    success = selected_metric['recall'] >= .6 and selected_metric['precision'] >= .15 and selected_metric['recall']-baseline_metric['recall'] >= .1
    report = dict(schema=1, name='ULB chronological holdout', source='https://www.kaggle.com/datasets/mlg-ulb/creditcardfraud',
                  attribution='Worldline and Machine Learning Group, Université Libre de Bruxelles. September 2013 European card payments.',
                  dataset_sha256=hashlib.sha256(raw_path.read_bytes()).hexdigest(), rows=len(test), fraud=int(y.sum()),
                  all_rows=len(frame), all_fraud=int(frame.Class.sum()), selected=selected, config=config,
                  splits={name:dict(rows=len(p), fraud=int(p.Class.sum()), start=float(p.Time.min()), end=float(p.Time.max())) for name,p in [('train',train),('validation',val),('test',test)]},
                  validation_average_precision=validation, strategies=strategies, repeats=repeats,
                  random_expected=dict(precision=float(y.mean()), recall=k/len(y), caught=k*float(y.mean())),
                  primary_success=success, recall_difference_interval=np.quantile(deltas,[.025,.975]).tolist(),
                  error_analysis=errors, duplicate_feature_overlap=duplicates, novel_test=dict(rows=int(novel.sum()), **deduplicated),
                  versions=dict(python=platform.python_version(),numpy=np.__version__,pandas=pd.__version__,sklearn=sklearn.__version__))
    # Timing is deliberately excluded from deterministic output.
    destination = ROOT/'public/benchmark.json'
    destination.parent.mkdir(exist_ok=True)
    encoded = (json.dumps(report, indent=2, ensure_ascii=False)+'\n').encode('utf-8')
    destination.write_bytes(encoded)
    (ROOT/'reports/benchmark.json').write_bytes(encoded)
    print(json.dumps(dict(selected=selected, primary=selected_metric, baseline=baseline_metric, success=success, duplicate_overlap=duplicates, seconds=round(time.perf_counter()-start,1)), indent=2))

if __name__ == '__main__':
    run()
