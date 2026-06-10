import pandas as pd
import numpy as np
from schemas import count_dict
from typing import cast

class ExcelProcessor:
    def __init__(self, path: str):
        self.df = pd.read_excel(path, header=None)

    def clean_data(self) -> "ExcelProcessor":
        self.df = (
            self.df
            .dropna(axis=0, how='all')
            .dropna(axis=1, how='all')
            .rename(columns={
                1: "names_address",
                2: "count",
            })
            .dropna(axis=0, how='all', subset=["names_address", "count"])
            .reset_index(drop=True)
        )
        return self
    
    def count(self) -> list[count_dict]:
        df= self.df.copy()
        df["count"] = pd.to_numeric(df["count"], errors="coerce")

        # boolean mask
        hotel_regex = "hotel|edificio"
        is_hotel = df["names_address"].str.contains(hotel_regex, case=False, na=False)
        is_address = (
            df["count"].isna() # Is not a pax field
            & ~df["names_address"].str.contains(hotel_regex+'|asistentes', case=False, na=False) # Not a hotel or the label
            & df["names_address"].notna()
        )

        df["hotel"] = np.where(is_hotel, df["names_address"], np.nan)
        df["hotel"] = df["hotel"].ffill()

        df["address"] = np.where(is_address, df["names_address"], np.nan)
        df["address"] = df["address"].ffill()

        df_pax = df.dropna(subset=["count"]).copy()
        df_pax["count"] = df_pax["count"].astype(int)

        df_count = df_pax.groupby(["hotel", "address"])["count"].sum().reset_index()

        self.df = df_count
        count = df_count.to_dict(orient="records")
        count = cast(list[count_dict], count)
        return count

    def show(self) -> None: # pragma: no cover
        print(self.df)


if __name__ == "__main__": # pragma: no cover
    ruta_test = "excel_processing/test/excel_test.xlsx" 
    
    processor = ExcelProcessor(ruta_test)
    processor.clean_data()
    
    processor.show()
    #processor.df.to_excel("clean_excel.xlsx", index=False)