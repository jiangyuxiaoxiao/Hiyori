from pathlib import Path

import jinja2
import markdown
from httpx import AsyncClient
from Hiyori.Plugins.Basic_plugins.nonebot_plugin_htmlrender.data_source import get_new_page, read_tpl

from .config import config

RES_PATH = Path(__file__).parent / "res"
HTML_TEMPLATE = jinja2.Template((RES_PATH / "template.html.jinja").read_text("u8"))


async def render_image(thing_a: str, thing_b: str, content: str) -> bytes:
    parsed_md = markdown.markdown(
        content,
        extensions=[
            "pymdownx.tasklist",
            "tables",
            "fenced_code",
            "codehilite",
            "mdx_math",
            "pymdownx.tilde",
        ],
        extension_configs={"mdx_math": {"enable_dollar_delimiter": True}},
    )

    katex_js = await read_tpl("katex/katex.min.js")
    mathtex_js = await read_tpl("katex/mathtex-script-type.min.js")
    extra = f"<script defer>{katex_js}</script><script defer>{mathtex_js}</script>"
    css_txt = "\n\n".join(
        (
            await read_tpl("github-markdown-light.css"),
            await read_tpl("pygments-default.css"),
            await read_tpl("katex/katex.min.b64_fonts.css"),
        ),
    )

    rendered_html = HTML_TEMPLATE.render(
        css=css_txt,
        main_font=config.either_choice_main_font,
        code_font=config.either_choice_code_font,
        a=thing_a,
        b=thing_b,
        table=parsed_md,
        extra=extra,
    )

    async with get_new_page() as page:
        await page.set_viewport_size(
            {"width": config.either_choice_pic_width, "height": 720},
        )
        await page.goto(RES_PATH.as_uri())
        await page.set_content(rendered_html, wait_until="networkidle")

        elem = await page.query_selector(".body")
        assert elem
        return await elem.screenshot(type="jpeg")


async def get_choice(thing_a: str, thing_b: str) -> str:
    async with AsyncClient(
        timeout=config.either_choice_timeout,
        proxies=config.proxy,
    ) as client:
        response = await client.post(
            "https://eitherchoice.com/api/prompt/dev",
            json={
                "A": thing_a,
                "B": thing_b,
                "allowPublic": str(config.either_choice_allow_public).lower(),
                "lang": config.either_choice_lang,
            },
        )
    return response.text


async def get_choice_pic(thing_a: str, thing_b: str) -> bytes:
    return await render_image(thing_a, thing_b, await get_choice(thing_a, thing_b))
