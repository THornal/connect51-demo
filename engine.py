import pandas as pd

def load_data(inst_csv, res_csv):
    inst = pd.read_csv(inst_csv)
    res = pd.read_csv(res_csv)
    inst["topic_set"] = inst["topics"].str.lower().str.split(";")
    res["topic_set"] = res["topics"].str.lower().str.split(";")
    return inst, res

def score_overlap(a, b):
    a=set(a); b=set(b)
    if not a or not b:
        return 0
    return len(a.intersection(b)) / len(a.union(b))

def recommend(inst_df, source, subject):
    src = inst_df[(inst_df["institution_name"]==source) & (inst_df["subject_area"]==subject)].iloc[0]
    results=[]
    for _,row in inst_df.iterrows():
        if row["institution_name"]==source: 
            continue
        overlap = score_overlap(src["topic_set"], row["topic_set"])
        score = overlap*0.4 + row["impact_score"]/100*0.25 + row["intl_collab_score"]/100*0.2 + row["strategic_region_score"]/100*0.15
        results.append((row["institution_name"], row["country"], round(score*100,2)))
    df = pd.DataFrame(results, columns=["institution_name","country","match_score"])
    return df.sort_values("match_score", ascending=False).head(10)

def recommend_researchers(res_df, institutions):
    return res_df[res_df["institution_name"].isin(institutions)].head(10)