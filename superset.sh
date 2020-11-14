#!/bin/bash

# Activar Anaconda
source /home/estudiante/anaconda3/bin/activate
conda activate twitter

# Correr Superset
superset run -h 0.0.0.0 -p 5000 --with-threads --reload --debugger
