import importlib.resources
from fastapi.templating import Jinja2Templates


def get_templates() -> Jinja2Templates:
    # Get the templates directory from within the package
    with importlib.resources.files("fastapi_hypermedia.templates") as templates_dir:
        return Jinja2Templates(directory=str(templates_dir))
