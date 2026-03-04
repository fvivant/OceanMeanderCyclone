# Ocean meanders modulate extratropical cyclone energetics
Félix Vivant & Guillaume Lapeyre - LMD-IPSL, CNRS, ENS Paris

Contains the code used to plot the figures in "Ocean meanders modulate extratropical cyclone energetics"

## Setup

```bash
git clone https://github.com/fvivant/OceanMeanderCyclone.git
cd OceanMeanderCyclone
pip install -r requirements.txt
```

## Data

Download data from Zenodo: 

Vivant, F., & Lapeyre, G. (2026). Ocean meanders modulate extratropical cyclone energetics - data [Data set]. Zenodo. https://doi.org/10.5281/zenodo.18846024

Update `DATA_BASE_DIR` in `config.py` with your data path.

## Usage

```bash
cd codes/
python Figure1.py
python Figure2.py
python Figure3.py
python Figure4.py
python SuppFigure1.py
python SuppFigure2.py
python SuppFigure3.py
python SuppFigure4.py
python SuppFigure5.py
```

Output figures saved to `PLOT_OUTPUT_DIR`, see in `config.py`

## Citation

```
Vivant, F., et al. (2026). Ocean Meander Cyclone. doi:10.xxxx/zenodo.XXXXXX
```

## Author

Félix Vivant - LMD-IPSL, ENS Paris

## License

CC-BY-4.0
