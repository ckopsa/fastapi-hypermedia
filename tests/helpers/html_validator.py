try:
    from bs4 import BeautifulSoup

    HAS_BEAUTIFULSOUP = True
except ImportError:
    HAS_BEAUTIFULSOUP = False


def has_html_form(html_content: str) -> bool:
    """Check if HTML contains a form element"""
    if not HAS_BEAUTIFULSOUP:
        return "<form" in html_content.lower()

    soup = BeautifulSoup(html_content, "html.parser")
    return len(soup.find_all("form")) > 0


def has_html_links(html_content: str) -> bool:
    """Check if HTML contains anchor links"""
    if not HAS_BEAUTIFULSOUP:
        return "<a" in html_content.lower()

    soup = BeautifulSoup(html_content, "html.parser")
    return len(soup.find_all("a")) > 0


def count_html_forms(html_content: str) -> int:
    """Count number of form elements in HTML"""
    if not HAS_BEAUTIFULSOUP:
        return html_content.lower().count("<form")

    soup = BeautifulSoup(html_content, "html.parser")
    return len(soup.find_all("form"))


def get_form_action(html_content: str, form_index: int = 0) -> str | None:
    """Get action attribute of nth form in HTML"""
    if not HAS_BEAUTIFULSOUP:
        return None

    soup = BeautifulSoup(html_content, "html.parser")
    forms = soup.find_all("form")
    if form_index < len(forms):
        return forms[form_index].get("action")
    return None


def has_form_input(html_content: str, input_name: str) -> bool:
    """Check if HTML form contains input with specific name"""
    if not HAS_BEAUTIFULSOUP:
        return (
            f'name="{input_name}"' in html_content
            or f"name='{input_name}'" in html_content
        )

    soup = BeautifulSoup(html_content, "html.parser")
    inputs = soup.find_all("input", {"name": input_name})
    return len(inputs) > 0
