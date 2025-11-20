import importlib.resources

from fastapi.templating import Jinja2Templates


def get_templates() -> Jinja2Templates:
    # Get the templates directory from within the package
    templates_dir = importlib.resources.files("fastapi_hypermedia.templates")
    return Jinja2Templates(directory=str(templates_dir))
