from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor
import model as tf_model
import uvicorn
import subprocess
import uuid
import glob

# =============================================================================
# Pool de Threads para disparar consultas
executor = ThreadPoolExecutor(max_workers=5)

# Consultas programadas (Promises List)
futures = {}

# Crear el motor de la aplicacion web
app = FastAPI()

# Desactivar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =============================================================================
# Modelos para los diversos body de los RF


class predict_text(BaseModel):
    """
    Contiene el texto a predecir con el modelo
    de aprendizaje automatico

    Properties
    -------------------
    text: str
        Mensaje de twitter
    """

    text: str


# =============================================================================
# Funciones auxiliares para ejecucion en batch


def execute_process(uuid, output, hadoop):
    """
    Ejecuta el comando de prueba y redirige la salida estandar a un archivo
    """
    # Ruta del proceso
    backend_path = "/home/bigdata07/backend"
    # Path para el proceso de log
    path = "%s/logs/%s.txt" % (backend_path, uuid)
    # Comando para crear la carpeta para guardar los resultados del proceso de Hadoop
    backend_output_dir = "%s/output/%s" % (backend_path, uuid)
    mkdir_output = "mkdir -p %s" % (backend_output_dir)
    # Comando para hacer get de HDFS al home
    get_output = "hdfs dfs -get %s/* %s/" % (output, backend_output_dir)
    with open(path, "w") as file:
        # Ejecutar Hadoop
        subprocess.run(hadoop.split(" "), check=True, stdout=file, stderr=file)
        subprocess.run(mkdir_output.split(" "), check=True, stdout=file, stderr=file)
        subprocess.run(get_output.split(" "), check=True, stdout=file, stderr=file)
    # Resolve() de una promesa en JS
    return backend_output_dir


# =============================================================================
# Renderizar vistas
@app.get("/")
def hello_word():
    """
    Mensaje de prueba con retorno de
    hola mundo
    """
    return {"hello": "world"}


@app.post("/predict")
async def predict(params: predict_text):
    """
    Permite predecir la polaridad del tweet yentregar
    su nivel de similitud
    """
    tweet = params.text
    return tf_model.predict(tweet)


@app.post("/bigdata07/execute/rf2")
# params: rf2_data
def execute_rf2(params: str):
    idPath = str(uuid.uuid4())
    # Carpeta de salida del proceso
    output = "%s/%s" % (params.output, idPath)
    # Comando de ejecucion para Hadoop
    hadoop = (
        "hadoop jar ProcesamientoEscalable-0.0.1-SNAPSHOT.jar grp_07.RF2.job.RF2 %s %s %s %s %s"
        % (params.input, output, params.dias, params.zonas, params.mes)
    )
    # Ejecutar el proceso paralelamente.
    futures[idPath] = executor.submit(execute_process, idPath, output, hadoop)
    return {"id": idPath}


@app.post("/complete/{task}", status_code=200)
async def is_complete(task: str):
    future = futures.get(task)
    if future is not None:
        if not future.done():
            detail_message = "El proceso %s aun sigue ejecutandose" % (task)
            raise HTTPException(status_code=206, detail=detail_message)
        else:
            path_result = future.result()
            result = {}
            founded = False
            for file in glob.iglob(path_result + "/part*", recursive=True):
                founded = True
                with open(file, "rb") as file_readed:
                    lines = file_readed.readlines()
                    for l in lines:
                        line = l.decode("utf-8")
                        parsed = line.strip().split(":", 1)
                        result[parsed[0]] = parsed[1].strip()
            if founded:
                # Borrar el future (promise) de la lista de pendientes
                futures.pop(task)
                return result
            else:
                futures.pop(task)
                raise HTTPException(
                    status_code=500, detail="Error fatal al buscar el part_ asociado"
                )
    else:
        detail_message = "El proceso %s NO existe" % (task)
        raise HTTPException(status_code=404, detail=detail_message)


if __name__ == "__main__":
    # Cargar el modelo de tensorflow
    tf_model.init()
    # Lanza la aplicación
    uvicorn.run(app, host="0.0.0.0", port=8000)