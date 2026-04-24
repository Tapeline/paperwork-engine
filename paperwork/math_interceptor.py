from typing import Final

import ziamath
from markdown_it import MarkdownIt
from mdit_py_plugins.dollarmath import dollarmath_plugin

MATH_FONT_SIZE: Final = 18


def render_math_inline(self, tokens, idx, options, env) -> str:
    tex_content = tokens[idx].content
    try:
        svg_xml = ziamath.Latex(tex_content, inline=True, size=MATH_FONT_SIZE).svg()
        return f'<span class="math-inline" style="display: inline-block; vertical-align: middle;">{svg_xml}</span>'
    except Exception as e:
        print(f"Math rendering error on '{tex_content}': {e}")
        return f'<span class="math-error" style="color:red;">${tex_content}$</span>'


def render_math_block(self, tokens, idx, options, env) -> str:
    tex_content = tokens[idx].content
    try:
        svg_xml = ziamath.Latex(
            tex_content, inline=False, size=MATH_FONT_SIZE
        ).svg()
        return f'<div class="math-block" style="text-align: center; margin: 1em 0;">{svg_xml}</div>'
    except Exception as e:
        print(f"Math block rendering error on '{tex_content}': {e}")
        return f'<div class="math-error" style="color:red;">$${tex_content}$$</div>'


def svg_math_plugin(md: MarkdownIt):
    md.use(dollarmath_plugin)
    md.add_render_rule("math_inline", render_math_inline)
    md.add_render_rule(
        "math_inline_double", render_math_block
    )
    md.add_render_rule("math_block", render_math_block)
    md.add_render_rule("math_block_eqno", render_math_block)
