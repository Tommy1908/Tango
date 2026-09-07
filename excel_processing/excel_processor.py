import pandas as pd
import numpy as np
from schemas import count_dict
from typing import cast

class ExcelProcessor:
    def __init__(self, path: str):
        self.df = pd.read_excel(path, header=None)

    def clean_data(self) -> "ExcelProcessor":
        #Initial cleanup: Drop empty rows/cols
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

        # We will add the secuential name to only one count
        processed_rows = []
        current_hotel = None
        current_address = None
        current_count = 0

        #print(self.df)
        for _, row in self.df.iterrows():
            row_text = row['names_address']
            row_count = row['count']
            #print(row)

            # If there is no count, the row contains either a hotel name or an address
            if pd.isna(row_count):
                # If we already have a hotel and address, we have hit the start of a new one. (Or repeated one)
                if current_hotel is not None and current_address is not None:
                    if(current_count == 0):
                        raise Exception(f"Count is missing on {current_hotel}") 
                    processed_rows.append({
                        "Hotel": current_hotel,
                        "Address": current_address,
                        "Total_Count": current_count
                    })
                    # Reset for the new block
                    current_hotel = row_text
                    current_address = None
                    current_count = 0
                # Otherwise, populate the missing hotel or address for the CURRENT block
                elif current_hotel is None:
                    current_hotel = row_text
                elif current_address is None:
                    current_address = row_text
            
            # If there is a count, add it to the running total for the current hotel
            else:
                if current_address is None:
                    #If there is a name, and hit a new one but no address, something is wrong with the excel
                    raise Exception(f"Address is missing on {current_hotel}") 
                try:
                    current_count += int(row_count)
                except ValueError:
                    pass
                
        # Append the last hotel block
        if current_hotel is not None:
            processed_rows.append({
                "Hotel": current_hotel,
                "Address": current_address,
                "Total_Count": current_count
            })

        # Overwrite self.df with the cleanly parsed records
        self.df = pd.DataFrame(processed_rows)
        self.df["Total_Count"] = self.df["Total_Count"].astype(int)

        # If there was any repeated hotel, here it will continue to be like that
        # We add them toghether on count
        return self
    
    def count(self) -> list[count_dict]:
        df = self.df.copy()

        # Rename for dictionary keys
        df.columns = ["name", "address", "count"]

        # Group by name and address to sum counts
        df = df.groupby(["name", "address"])["count"].sum().reset_index()

        self.df = df
        count_records = df.to_dict(orient="records")
        
        return cast(list[count_dict], count_records)

    def show(self) -> None: # pragma: no cover
        """Prints the current state of the DataFrame."""
        print(self.df)


if __name__ == "__main__": # pragma: no cover
    ruta_test = "excel_processing/test/excel_test.xlsx" 
    
    processor = ExcelProcessor(ruta_test)
    
    # Process and save clean data
    clean = processor.clean_data()
    processor.df.to_excel("excel_test_clean.xlsx", index=False)
    
    # Group data, print, and save
    count_data = processor.count()
    print(count_data)
    processor.show()
    processor.df.to_excel("excel_test_count.xlsx", index=False)