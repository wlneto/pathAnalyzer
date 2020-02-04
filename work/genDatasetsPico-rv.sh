#!/bin/bash
# python createDatabase.py pico-rv_400 pico-rvDatabase400.pkl
python createDatabase.py pico-rv_500 pico-rvDatabase500.pkl
python concatenateDatabases.py pico-rvDatabaseFull.pkl pico-rvDatabase400.pkl pico-rvDatabase500.pkl
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy0.pkl 0.7 0.3 0.0 0 0
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy1.pkl 0.7 0.3 0.0 0 1
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy2.pkl 0.7 0.3 0.0 0 2
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy3.pkl 0.7 0.3 0.0 0 3
mv pico-rvDatabaseFull.pkl pico-rvDatabaseFull0.pkl 
python createDatabase.py pico-rv_600 pico-rvDatabase600.pkl
python concatenateDatabases.py pico-rvDatabaseFull.pkl pico-rvDatabase400.pkl pico-rvDatabase500.pkl pico-rvDatabase600.pkl
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy0.pkl 0.7 0.3 0.0 0 0
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy1.pkl 0.7 0.3 0.0 0 1
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy2.pkl 0.7 0.3 0.0 0 2
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy3.pkl 0.7 0.3 0.0 0 3
mv pico-rvDatabaseFull.pkl pico-rvDatabaseFull1.pkl 
python createDatabase.py pico-rv_700 pico-rvDatabase700.pkl
python concatenateDatabases.py pico-rvDatabaseFull.pkl pico-rvDatabase400.pkl pico-rvDatabase500.pkl pico-rvDatabase600.pkl pico-rvDatabase700.pkl
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy0.pkl 0.7 0.3 0.0 0 0
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy1.pkl 0.7 0.3 0.0 0 1
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy2.pkl 0.7 0.3 0.0 0 2
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy3.pkl 0.7 0.3 0.0 0 3
mv pico-rvDatabaseFull.pkl pico-rvDatabaseFull2.pkl 
python createDatabase.py pico-rv_800 pico-rvDatabase800.pkl
python concatenateDatabases.py pico-rvDatabaseFull.pkl pico-rvDatabase400.pkl pico-rvDatabase500.pkl pico-rvDatabase600.pkl pico-rvDatabase700.pkl pico-rvDatabase800.pkl
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy0.pkl 0.7 0.3 0.0 0 0
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy1.pkl 0.7 0.3 0.0 0 1
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy2.pkl 0.7 0.3 0.0 0 2
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy3.pkl 0.7 0.3 0.0 0 3
mv pico-rvDatabaseFull.pkl pico-rvDatabaseFull3.pkl 
python createDatabase.py pico-rv_950 pico-rvDatabase950.pkl
python concatenateDatabases.py pico-rvDatabaseFull.pkl pico-rvDatabase400.pkl pico-rvDatabase500.pkl pico-rvDatabase600.pkl pico-rvDatabase700.pkl pico-rvDatabase800.pkl pico-rvDatabase950.pkl
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy0.pkl 0.7 0.3 0.0 0 0
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy1.pkl 0.7 0.3 0.0 0 1
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy2.pkl 0.7 0.3 0.0 0 2
python createDataset.py pico-rvDatabaseFull.pkl pico-rvTrainDatasetFullStrategy3.pkl 0.7 0.3 0.0 0 3
