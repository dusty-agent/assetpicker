from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from app.daily.config import ASSETS


def render_html(
    template_name: str,
    context: dict,
    template_dir: Path,
):
    """
    지정한 template_dir에서 Jinja 템플릿을 렌더링한다.

    cards/templates
    shorts/templates
    모두 공용으로 사용.
    """

    env = Environment(
        loader=FileSystemLoader(template_dir),
        autoescape=True,
    )

    context = {
        **context,
        "asset_path": ASSETS.resolve().as_uri(),
    }

    template = env.get_template(template_name)

    return template.render(**context)