# Ejecucion del servidor para ofrecer un endpoint a los requerimientos

Para poder desplegar correctamente el servidor con __uvicorn__ instale Anaconda
```
cd /tmp
wget https://repo.anaconda.com/archive/Anaconda3-2020.07-Linux-x86_64.sh
bash Anaconda3-2020.07-Linux-x86_64.sh
```

Complete los pasos de la instalacion y proceda ahora a configurar en entorno virtual para desplegar
```
conda env create -f env_backend.yaml
conda activate bigdata
```

En la carpeta raiz del directorio del usuario /home/__usuario__ cree una carpeta para el log
```
mkdir logs
```

Despliegue el servicio
```
uvicorn main:app --host 0.0.0.0 --port 24009
```

La carpeta contenedora del backend debe tener por nombre __backend__ y estar ubicada en el directorio __/home/bigdata07/__
A continuacion se muestra su estructura y las carpetas base que debe tener

![backend-bigdata](https://user-images.githubusercontent.com/37672135/95377542-534cc480-08a8-11eb-8797-220fe10553a1.png)
