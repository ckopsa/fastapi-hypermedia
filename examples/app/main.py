from fastapi import FastAPI
from fastapi.routing import APIRoute
from routers import root, workflow_definitions
from routers import workflow_instances as workflow_instances_router
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware


def generate_unique_id(route: "APIRoute") -> str:
    operation_id = f"{route.name}"
    return operation_id


app = FastAPI(generate_unique_id_function=generate_unique_id)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# Include routers
app.include_router(root.router)
app.include_router(workflow_definitions.router)
app.include_router(workflow_instances_router.router)
