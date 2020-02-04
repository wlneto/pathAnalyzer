#!/bin/bash
python createDatabase.py aes_200 aesDatabase200.pkl
python createDataset.py aesDatabase200.pkl aesTestDataset200Strategy0.pkl 0.0 0.0 1.0 0 0
python createDataset.py aesDatabase200.pkl aesTestDataset200Strategy1.pkl 0.0 0.0 1.0 0 1
python createDataset.py aesDatabase200.pkl aesTestDataset200Strategy2.pkl 0.0 0.0 1.0 0 2
python createDataset.py aesDatabase200.pkl aesTestDataset200Strategy3.pkl 0.0 0.0 1.0 0 3
python createDatabase.py aes_225 aesDatabase225.pkl
python createDataset.py aesDatabase225.pkl aesTestDataset225Strategy0.pkl 0.0 0.0 1.0 0 0
python createDataset.py aesDatabase225.pkl aesTestDataset225Strategy1.pkl 0.0 0.0 1.0 0 1
python createDataset.py aesDatabase225.pkl aesTestDataset225Strategy2.pkl 0.0 0.0 1.0 0 2
python createDataset.py aesDatabase225.pkl aesTestDataset225Strategy3.pkl 0.0 0.0 1.0 0 3
python createDatabase.py aes_250 aesDatabase250.pkl
python createDataset.py aesDatabase250.pkl aesTestDataset250Strategy0.pkl 0.0 0.0 1.0 0 0
python createDataset.py aesDatabase250.pkl aesTestDataset250Strategy1.pkl 0.0 0.0 1.0 0 1
python createDataset.py aesDatabase250.pkl aesTestDataset250Strategy2.pkl 0.0 0.0 1.0 0 2
python createDataset.py aesDatabase250.pkl aesTestDataset250Strategy3.pkl 0.0 0.0 1.0 0 3
python createDatabase.py aes_275 aesDatabase275.pkl
python createDataset.py aesDatabase275.pkl aesTestDataset275Strategy0.pkl 0.0 0.0 1.0 0 0
python createDataset.py aesDatabase275.pkl aesTestDataset275Strategy1.pkl 0.0 0.0 1.0 0 1
python createDataset.py aesDatabase275.pkl aesTestDataset275Strategy2.pkl 0.0 0.0 1.0 0 2
python createDataset.py aesDatabase275.pkl aesTestDataset275Strategy3.pkl 0.0 0.0 1.0 0 3
python createDatabase.py aes_300 aesDatabase300.pkl
python createDataset.py aesDatabase300.pkl aesTestDataset300Strategy0.pkl 0.0 0.0 1.0 0 0
python createDataset.py aesDatabase300.pkl aesTestDataset300Strategy1.pkl 0.0 0.0 1.0 0 1
python createDataset.py aesDatabase300.pkl aesTestDataset300Strategy2.pkl 0.0 0.0 1.0 0 2
python createDataset.py aesDatabase300.pkl aesTestDataset300Strategy3.pkl 0.0 0.0 1.0 0 3
python createDatabase.py aes_325 aesDatabase325.pkl
python createDataset.py aesDatabase325.pkl aesTestDataset325Strategy0.pkl 0.0 0.0 1.0 0 0
python createDataset.py aesDatabase325.pkl aesTestDataset325Strategy1.pkl 0.0 0.0 1.0 0 1
python createDataset.py aesDatabase325.pkl aesTestDataset325Strategy2.pkl 0.0 0.0 1.0 0 2
python createDataset.py aesDatabase325.pkl aesTestDataset325Strategy3.pkl 0.0 0.0 1.0 0 3
# python createDatabase.py aes_350 aesDatabase350.pkl
python createDataset.py aesDatabase350.pkl aesTestDataset350Strategy0.pkl 0.0 0.0 1.0 0 0
python createDataset.py aesDatabase350.pkl aesTestDataset350Strategy1.pkl 0.0 0.0 1.0 0 1
python createDataset.py aesDatabase350.pkl aesTestDataset350Strategy2.pkl 0.0 0.0 1.0 0 2
python createDataset.py aesDatabase350.pkl aesTestDataset350Strategy3.pkl 0.0 0.0 1.0 0 3
# Concat
python concatenateDatabases.py aesDatabaseFull.pkl aesDatabase200.pkl aesDatabase225.pkl aesDatabase250.pkl aesDatabase275.pkl aesDatabase300.pkl aesDatabase325.pkl aesDatabase350.pkl
python createDataset.py aesDatabaseFull.pkl aesTestDatasetFullStrategy0.pkl 0.0 0.0 1.0 0 0
python createDataset.py aesDatabaseFull.pkl aesTestDatasetFullStrategy1.pkl 0.0 0.0 1.0 0 1
python createDataset.py aesDatabaseFull.pkl aesTestDatasetFullStrategy2.pkl 0.0 0.0 1.0 0 2
python createDataset.py aesDatabaseFull.pkl aesTestDatasetFullStrategy3.pkl 0.0 0.0 1.0 0 3
