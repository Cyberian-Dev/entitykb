import multiprocessing

from entitykb import rpc, environ
from .app import app

subprocess = None


@app.on_event("startup")
async def startup_event():
    """ Start RPC Server for development purposes. """
    global subprocess
    kw = dict(root=environ.root, host=environ.rpc_host, port=environ.rpc_port)
    subprocess = multiprocessing.Process(target=rpc.launch, kwargs=kw)
    subprocess.start()


@app.on_event("shutdown")
async def shutdown_event():
    """ Piggyback on uvicorn reloading to restart RPC server. """
    global subprocess
    subprocess.terminate()
    subprocess.join()
