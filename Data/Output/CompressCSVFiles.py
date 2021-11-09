# COMPRESS CSVs FOR GITHUB UPLOAD
# Not really compressing to be honest, it just takes every nth row


import pandas as pd

def compress_csv(file_path, nth_rows=50):

    df = pd.read_csv(file_path)

    df = df.iloc[::nth_rows, :]

    df.to_csv(file_path)



if __name__ == "__main__":
    compress_csv("Data/Output/output5DOFMMR.csv")