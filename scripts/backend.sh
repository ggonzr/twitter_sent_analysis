#!/bin/bash

# Activar Anaconda
source /home/estudiante/anaconda3/bin/activate
conda activate twitter

# Correr Gunicorn y desplegar el servidor
python main.py
