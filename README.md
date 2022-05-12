# Matching MOFs from the NIST-ISODB to the CSD

Notebooks supporting the article *Data-driven matching of experimental crystal structures and gas adsorption isotherms of metal-organic frameworks* by Daniele Ongari, Leopold Talirz, Kevin Maik Jablonka, Daniel W. Siderius, and Berend Smit.

- ChemRxiv: [10.26434/chemrxiv-2021-gs0wj](https://chemrxiv.org/engage/chemrxiv/article-details/61f9aafd537af8e7daad48f4)
- J. Chem. Eng. Data: [10.1021/acs.jced.1c00958](https://pubs.acs.org/doi/10.1021/acs.jced.1c00958)

## Python environment
Install the conda environment as:
```
conda env create -f environment.yml
```
and, for development purpose, update the file with:
```
conda env export --name isodb_csd  > environment.yml
```
