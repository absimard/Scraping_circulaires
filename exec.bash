#!/bin/bash

# Activation de l'environnement virtuel
source .venv/bin/activate

# Exécution du script Python
python scraping_circulaires.py

# Récupération de la date d'exécution au format AAAA-MM-JJ
DATE_EXEC=$(date +%F)

# Renommage du fichier
mv circulaires.xlsx "circulaires_${DATE_EXEC}.xlsx"

# Désactivation de l'environnement virtuel (optionnel)
deactivate

