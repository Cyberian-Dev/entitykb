import multiprocessing

from entitykb import rpc, environ
from .app import app

subprocess = None


@app.on_event("startup")
async def startup_event():
    global subprocess
    kw = dict(root=environ.root, host=environ.rpc_host, port=environ.rpc_port)
    subprocess = multiprocessing.Process(target=rpc.launch, kwargs=kw)
    subprocess.start()


@app.on_event("shutdown")
async def shutdown_event():
    global subprocess
    subprocess.terminate()
    subprocess.join()
