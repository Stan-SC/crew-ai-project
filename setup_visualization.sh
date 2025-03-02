#!/bin/bash

# Activation de l'environnement virtuel
source .venv/bin/activate

# Installation des packages nécessaires
pip install ipywidgets plotly pandas jupyter

# Installation des extensions Jupyter
jupyter nbextension enable --py widgetsnbextension
jupyter labextension install @jupyter-widgets/jupyterlab-manager

echo "Installation terminée. Vous pouvez maintenant lancer Jupyter Notebook." 