import pandas as pd
from pandas.testing import assert_frame_equal
import pytest
from excel_processing.excel_processor import ExcelProcessor

def test_processor_reads_file_correctly():
    path = "excel_processing/test/excel_test.xlsx"
    
    expected_df = pd.read_excel(path, header=None)
    processor = ExcelProcessor(path)

    assert expected_df.equals(processor.df)

def test_processor_reads_unexisting_file_raises_error():
    fake_path = "excel_processing/test/not_excel_test.xlsx"
    
    with pytest.raises(FileNotFoundError):
        ExcelProcessor(fake_path)

def test_clean_data():
    path = "excel_processing/test/excel_test.xlsx"
    res_path = "excel_processing/test/excel_test_clean.xlsx"

    expected_df = pd.read_excel(res_path)
    processor = ExcelProcessor(path)
    processor.clean_data()

    assert expected_df.equals(processor.df)

def test_count_file():
    path = "excel_processing/test/excel_test.xlsx"
    expected_count = [{'name': 'AQ TAILORED SUITES - Hotel', 'address': 'MONTEVIDEO 937', 'count': 2}, {'name': 'ARC ARENALES - EDIFICIO', 'address': 'ARENALES 2644', 'count': 2}, {'name': 'BA ABASTO HOTEL - Hotel', 'address': 'Jean Jaures 896', 'count': 2}, {'name': 'BELIEVE - Hotel', 'address': 'CHILE 80', 'count': 10}, {'name': 'BROADWAY - Hotel', 'address': 'CORRIENTES 1173', 'count': 2}, {'name': 'DOLMEN - Hotel', 'address': 'SUIPACHA 1079', 'count': 6}, {'name': 'EL CONQUISTADOR - Hotel', 'address': 'SUIPACHA 948', 'count': 2}, {'name': 'LIBERTADOR HOTEL - Hotel', 'address': 'CORDOBA 690', 'count': 4}, {'name': 'NH CENTRO HISTORICO - Hotel', 'address': 'BOLIVAR 120', 'count': 4}, {'name': 'NOMA HOTEL - Hotel', 'address': 'RODRIGUEZ PEÑA 151', 'count': 2}, {'name': 'PARK ROYAL CITY BS AS - Hotel', 'address': 'SUIPACHA 1092', 'count': 2}, {'name': 'PASEO DE LA CISTERNA - EDIFICIO', 'address': 'MORENO 550', 'count': 2}]
    expected_clean_count_path = "excel_processing/test/excel_test_count.xlsx"

    processor = ExcelProcessor(path)
    expected_df = pd.read_excel(expected_clean_count_path)
    count = processor.clean_data().count()

    assert_frame_equal(expected_df, processor.df, check_dtype=False)
    assert expected_count == count