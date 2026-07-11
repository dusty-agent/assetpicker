from jinja2 import Environment, FileSystemLoader

from app.daily.config import ASSETS, TEMPLATES

env = Environment(
    loader=FileSystemLoader(TEMPLATES),
    autoescape=True,
)


def render_html(template_name, context):

    context = {
        **context,
        "asset_path": ASSETS.resolve().as_uri(),
    }

    template = env.get_template(template_name)

    return template.render(**context)