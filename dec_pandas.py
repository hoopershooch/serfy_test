import pandas as pd
import re
import functools
import sys
COEFFS = {
    "100m":         {"a":25.4348,"b":18, "c":1.81},
    "Long_jump":    {"a":90.5674,"b":2.2,"c":1.4},		
    "Shot_put":     {"a":51.39,  "b":1.5,"c":1.05},
    "High_jump":    {"a":585.64, "b":0.75,"c":1.42},
    "400m":         {"a":1.53775,"b":82.0,"c":1.81},
    "110m_hurdles": {"a":5.74354,"b":28.5,"c":1.92},
    "Discus_throw": {"a":12.91,  "b":4.0,"c":1.1},
    "Pole_vault":   {"a":140.182,"b":1.0,"c":1.35},
    "Javelin_throw":{"a":10.14,  "b":7.0,"c":1.08},
    "1500m":        {"a":0.03768,"b":480.0,"c":1.85}
    }


def convert(val):
    """Calculates 1500m time from string for each row. """

    splitted = re.split("\D", val)
    if len(splitted)==3:
        return 60*float(splitted[0])+float(splitted[1])+float(splitted[2])/100

def calc_score(column):
    """Calculates to total score for each row. """

    scores=(
        COEFFS[key]["a"]*pow(abs(column[key]-COEFFS[key]["b"]),COEFFS[key]["c"])
        for key in column.keys() if key in COEFFS
    )
    return functools.reduce(lambda acc, x: acc+x, scores, 0)

if __name__=="__main__":
    #checking args
    if len(sys.argv) < 2:
        print("Specify a CSV file name as a parameter!")
        sys.exit(1)
    #reading data from csv file
    names=["Name"]
    names.extend(COEFFS.keys())
    df=pd.read_csv(
        sys.argv[1],
        sep=";",
        header=None,
        names=names,
        converters={10:convert}
    )
    #dropping wrong results
    df.dropna(inplace = True)
    #counting scores
    df["score"]=df.apply(calc_score, axis=1)
    #sorting by scores
    df.sort_values(by="score",
        inplace = True,
        ascending=False,
        ignore_index=True
    )
    #counting places
    df["place_s"]=df.index+1
    dfg=df.groupby("score", as_index=False)["place_s"]
    for score, subframe in dfg:
        df.loc[df["score"]==score,"place"]="-".join(
            str(item) for item in subframe["place_s"].values
        )
    #dropping extra fields
    df.drop("place_s",axis=1,inplace=True)
    #saving to json file
    df.to_json("pd_res.json", orient="records",lines=True, indent=2)

