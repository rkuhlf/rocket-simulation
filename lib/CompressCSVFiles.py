# COMPRESS CSVs FOR GITHUB UPLOAD
# Not really compressing to be honest, it just takes every nth row


import pandas as pd

def compress_csv(file_path, nth_rows=10):

    df = pd.read_csv(file_path)

    df = df.iloc[::nth_rows, :]

    df.to_csv(file_path)



if __name__ == "__main__":
    files_to_compress = ["output5DOFNoWind", "output5DOFWind"]

    for f in files_to_compress:
        compress_csv(f"Data/Output/{f}.csv")