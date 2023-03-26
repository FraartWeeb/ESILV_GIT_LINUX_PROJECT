#!/bin/bash

# Récupérer la valeur de l'or à partir de la page web
WEBPAGE=$(curl -s 'https://or.fr/cours/or')

gold_value=$(echo "$WEBPAGE" |  grep -o '<span class="large-price" style="line-height: 0px;">.*</span>' | sed 's/<[^>]*>//g' | tr -d '[:space:]')

# Ajouter la date et l'heure actuelles
date=$(date +"%Y-%m-%d %H:%M:%S")
output="$date $gold_value"

# Stocker la valeur dans un fichier
echo $output >> /home/ec2-user/Scrapping/gold_data.csv