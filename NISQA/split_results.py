import pandas as pd

# load csv
df = pd.read_csv("NISQA_results.csv")

# extract folder name
df["folder"] = df["target_file"].apply(lambda x: x.split("/")[1])

# extract com value (com10, com2, etc.)
df["group"] = df["folder"].apply(lambda x: "_".join(x.split("_")[:2]))

# rename target_file column to folder name
df["target_file"] = df["folder"].apply(lambda x: x.split("_")[2])

# remove helper column
df = df.drop(columns=["folder", "model"])

with pd.ExcelWriter("output.xlsx") as writer:
    for group, data in df.groupby("group"):
        data = data.drop(columns=["group"])
        data.to_excel(writer, sheet_name=group, index=False)