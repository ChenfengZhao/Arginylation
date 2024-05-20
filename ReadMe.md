# Arginylation

<!-- <p align="center">
    <img width="30%" src="./NuMoFinder_Logo.png" alt="NuMoFinder Finder"><br>
</p> -->

## Overview

[Add a short paragraph to introduce Arginylation]
You can either download the source code to run it on your own PC as the following direction, or directly visit [Add the Arginylation website address] for more dataset.
## Requirements

- Recommended OS: macOS (>= 10.13), Linux (e.g. Ubuntu >= 18.04), or Windows (>= 10)
- Python3 (3.7 or higher is supported)
- Pip3
- Python dependencies: numpy==1.21.2, scipy==1.7.1, dash==2.10.2, dash_bootstrap_components==1.4.1, pandas==1.3.4, openpyxl==3.1.2

## Installation Guide
Run the following command to install the dependencies of the visualization website Arginylation
```
pip3 install -r requirements.txt
```

## Usage Example
1. Download the source code of Arginylation. You can manully download the zip file and unzip it, or you can use the following command to directly download it.
```
git clone https://github.com/ChenfengZhao/Arginylation.git
```
  
2. Prepare your input files following the format of the example. Enter the data path **./data/**. Then unzip Human.zip. This example provides the examplary directory structure and the format input files. To add new datasets, copy your files to the appropriate path under this folder, then add corresponding information to **1website_information.xlsx**. Finally run the following command to automatically generate **web_info.xlsx**.
```
python3 gen_web_info.py
```

3. Start Arginylation using the following code:
```
cd <the path of app_new.py>
python3 app_new.py
```
If you run it on your own PC, copy **http://127.0.0.1:8050** to your local web browser.

The first page is the overall introduction of the Arginylation website. Click **Start Visualization** to view result of datasets



## License
[Apache_2.0_license]: http://www.apache.org/licenses/LICENSE-2.0

The source code of this project is released under the [Apache 2.0 License][Apache_2.0_license].

## Citation
If you think Arginylation is helpful for your research, please cite the following paper:

[Removed to preserve anonymity]

<!-- Xie, Y; De Luna Vitorino, F.N.; Chen, Y; Lempiäinen, J. K.; Zhao, C.; Steinbock, R. T.; Liu, X.; Lin, Z.; Zahn, E.; Garcia, A. L.; Weitzman, M. D.; Garcia, B. A., SWAMNA: a comprehensive platform for analysis of nucleic acid modifications. *Chemical Communications* **2023**

[ChemComm version](https://doi.org/10.1039/D3CC04402E)

[ChemRxiv version](https://chemrxiv.org/engage/chemrxiv/article-details/64f6a89079853bbd781e9eb7) -->
