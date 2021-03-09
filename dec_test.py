import pathlib
import json
import csv
import functools
import re
import collections
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


def read_from_csv(csv_file_name):
    """Reads raw competition data from csv file.

    Reads data from csv file lines according to decathlon
    disciplines.

    Args:
        csv_file_name: string, containg path to csv file.

    Returns: list of dicts, containing disciplines names:results and
        also names of competitors with key "Name"
    """
    names=["Name"]
    names.extend(COEFFS.keys())
    result=[]
    with open(csv_file_name,"r") as csv_file:
        reader = csv.reader(csv_file, delimiter = ";")
        for row in reader:
            result.append(
                {key: value
                 for key, value in zip(names, (res for res in row))}
            )
    return result

def reducer(acc,add):
    """Reducer disciplines results to total score.

    Transforms disciplines results to floats and reduces them
    to total score.

    Args:
        acc: reducer function accumulator.
        add: discipline result tuple, containing discipline result and
            coefficients to count score addition.

    Returns: modified acc.
    """
    def convert_to_float(res_string):
        try:
            return float(res_string)
        except ValueError:
            splitted = re.split("\D", res_string)
            if len(splitted)==3:
                return 60*float(splitted[0])+float(splitted[1])+float(splitted[2])/100
    return acc+add[1]["a"]*pow(abs(convert_to_float(add[0])-add[1]["b"]),add[1]["c"])    


if __name__=="__main__":
    #checking args
    if len(sys.argv) < 2:
        print("Specify a CSV file name as a parameter!")
        sys.exit(1)
    #reading data from csv file
    result = read_from_csv(sys.argv[1])
    #counting scores
    scores = collections.defaultdict(list)
    for index, comp_data in enumerate(result):
        comp_data.update(
            {
                "score":
                functools.reduce(
                    reducer,  
                    ((comp_data[key],COEFFS[key])
                    for key in COEFFS.keys() if key in comp_data),
                    0
                ),
                "place":None
             }
        )
        scores[comp_data["score"]].append({index: None})
    #counting places
    place=1
    for score in sorted(scores.keys(), reverse=True):
        for index_dict in scores[score]:
            for index in index_dict.keys():
                index_dict[index]=place
                place+=1
    #groupping places
    for ip_dict_list in scores.values():
        places=[]
        for ip_dict in ip_dict_list:
            for index, place in ip_dict.items():
                places.append(str(place))
        for ip_dict in ip_dict_list:
            for index in ip_dict.keys():
                result[index]["place"]="-".join(places)
    #sorting results
    result.sort(key=lambda x: x["score"], reverse=True)
    #saving results to json file
    with open("results.json", "w") as jf:
        json.dump(result, jf, indent=2)




