# Overview
This repository contains the source code for the paper "Read your Circuit: Leveraging Word Embedding to Guide Logic Optimization". It has the TCL and Python codes to generate and analyze the criticality of logic paths post-generic synthesis. The repo is organized as follows: 

- data: contains a shell script to clean up the generated CSV files that are used as input for training/inference. 
- src: contains the python code to generate the database with the extracted paths. 
- tcl: contains the TCL procedure used to extract the paths. This procedure might run for a long-time in complex designs. It also includes a simple Python script to parse the timing report and generate a CSV file as the example files in the data folder. 
- work: contains all the python code to generate and save the database, analyze the database, generate the neural network, and generate the SDC file used in the flow. 

Some examples of databases used in the paper are available in the work folder. Also, examples of how to create the databases are in the shell scripts, also under the work directory. The examples in the folder with the comments in the code should be enough to get it running. The code was developed considering the ASAP 7nm standard cell library, so some prefixes are hardcoded. Before using, take a look at the code and what is hardcoded or not. More examples will be added when possible. Good luck, and if you have any questions, please get in touch with walter.launeto@utah.edu.   

## Dependencies
- Cadence Genus for Logic Synthesis (the report timing script is implemented for Genus). 
- Python 2.7

## Reference

If you use this code, please cite our paper: 

```shell
@inproceedings{10.1145/3394885.3431560,
author = {Neto, Walter Lau and Moreira, Matheus Trevisan and Amaru, Luca and Yu, Cunxi and Gaillardon, Pierre-Emmanuel},
title = {Read Your Circuit: Leveraging Word Embedding to Guide Logic Optimization},
year = {2021},
isbn = {9781450379991},
publisher = {Association for Computing Machinery},
address = {New York, NY, USA},
url = {https://doi.org/10.1145/3394885.3431560},
doi = {10.1145/3394885.3431560},
booktitle = {Proceedings of the 26th Asia and South Pacific Design Automation Conference},
pages = {530–535},
numpages = {6},
keywords = {Word Embedding, Machine Learning, Electronic Design Automation, Timing Closure},
location = {Tokyo, Japan},
series = {ASPDAC '21}
}
```

