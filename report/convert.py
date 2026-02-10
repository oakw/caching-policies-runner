# Converts config json to csv. Utility script for report config generation.
import json
import csv
import sys

if __name__ == "__main__":
    file = sys.argv[1]

    if file.endswith(".json"):
        with open(file, "r") as f:
            data = json.load(f)

        if isinstance(data, list) and data and isinstance(data[0], dict):
            keys = set()
            for d in data:
                keys.update(d.keys())
            keys = sorted(keys)

            print("\t".join(keys))
            for row in data:
                values = [str(row.get(key, "")) for key in keys]
                print("\t".join(values))

        else:
            print(f"JSON file {file} does not contain a list of dictionaries.")

    elif file.endswith(".csv"):
        with open(file, "r") as f:
            reader = csv.DictReader(f, delimiter="\t")
            data = list(reader)

        for row in data:
            keys_to_remove = [key for key, value in row.items() if value == ""]
            for key in keys_to_remove:
                del row[key]

        print(json.dumps(data, indent=2))
