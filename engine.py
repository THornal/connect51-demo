import pandas as pd

def load_data(inst_csv, res_csv):
    inst = pd.read_csv(inst_csv)
    res = pd.read_csv(res_csv)
    inst["topic_set"] = inst["topics"].str.lower().str.split(";")
    res["topic_set"] = res["topics"].str.lower().str.split(";")
    return inst, res

def score_overlap(a, b):
    a = set(a)
    b = set(b)
    if not a or not b:
        return 0
    return len(a.intersection(b)) / len(a.union(b))

def classify_partner(row):
    impact = row["impact_score"]
    collab = row["intl_collab_score"]
    if impact > 95:
        return "Global Prestige Partner"
    if collab > 90:
        return "High Collaboration Partner"
    if impact > 85 and collab > 80:
        return "Strategic Research Partner"
    return "Emerging Opportunity"

def recommend(inst_df, source, subject):
    src = inst_df[
        (inst_df["institution_name"] == source) &
        (inst_df["subject_area"] == subject)
    ].iloc[0]

    results = []
    for _, row in inst_df.iterrows():
        if row["institution_name"] == source:
            continue

        overlap = score_overlap(src["topic_set"], row["topic_set"])
        score = (
            overlap * 0.4
            + row["impact_score"] / 100 * 0.25
            + row["intl_collab_score"] / 100 * 0.2
            + row["strategic_region_score"] / 100 * 0.15
        )

        results.append({
            "institution_name": row["institution_name"],
            "country": row["country"],
            "match_score": round(score * 100, 2),
            "impact_score": row["impact_score"],
            "intl_collab_score": row["intl_collab_score"]
        })

    df = pd.DataFrame(results)
    df["strategy_type"] = df.apply(classify_partner, axis=1)
    return df.sort_values("match_score", ascending=False).head(10)

def recommend_researchers(res_df, institutions):
    return res_df[res_df["institution_name"].isin(institutions)].head(10)