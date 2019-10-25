import glob

import pandas as pd
import os


def csv_dataframe(filename=None):
    if filename is not None:
        df = pd.read_csv(filename)
        return df

    cwd = os.getcwd()
    all_files = glob.glob(cwd + "/Output*.csv")

    li = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        li.append(df)

    frame = pd.concat(li, axis=0, ignore_index=True)

    return frame


def main():
    process_all = input("Quiere procesar todos los .csv que hay en esta carpeta? [y/n]: ")

    if process_all.lower() == "n":
        csv_file = input("Ingrese el nombre del csv a procesar: ")
        df = csv_dataframe(csv_file)
        print(df)

    else:
        df = csv_dataframe()
        print(df.colums())


if __name__ == '__main__':
    main()
