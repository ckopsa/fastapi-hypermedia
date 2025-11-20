import importlib.resources

from fastapi.templating import Jinja2Templates


def get_templates() -> Jinja2Templates:
    """
    Returns a Jinja2Templates instance configured with the package's templates directory.

    This allows users to easily render Collection+JSON responses as HTML.
    """
    # Get the templates directory from within the package
    templates_dir = importlib.resources.files("fastapi_hypermedia.templates")
    return Jinja2Templates(directory=str(templates_dir))
