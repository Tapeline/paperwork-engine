import os
import re
from markdown_it import MarkdownIt
from markdown_it.rules_inline import StateInline


def obsidian_embed_rule(state: StateInline, silent: bool) -> bool:
    """Inline parser rule to find ![[...]]"""
    if not state.src.startswith("![[", state.pos):
        return False

    end_pos = state.src.find("]]", state.pos + 3)
    if end_pos == -1:
        return False

    if not silent:
        content = state.src[state.pos + 3: end_pos]
        token = state.push("obsidian_embed", "", 0)
        token.content = content

    state.pos = end_pos + 2
    return True


def render_obsidian_embed(self, tokens, idx, options, env) -> str:
    """Renderer rule that converts the parsed token into HTML using `env` context"""
    token = tokens[idx]

    parts = token.content.split("|")
    filename = parts[0]

    alt_text = parts[1] if len(parts) > 1 else ""
    width, height = "", ""

    # Handle Obsidian resize aliases (e.g., |300 or |300x200)
    if re.match(r'^\d+$', alt_text):
        width = alt_text
        alt_text = ""
    elif re.match(r'^\d+x\d+$', alt_text):
        width, height = alt_text.split("x")
        alt_text = ""

    # === DYNAMIC ENV RESOLUTION ===
    # Fetch lists and configs dynamically passed in md.render(..., env={})
    media_paths = env.get("media_paths", [])
    build_dir_prefix = env.get("build_dir_prefix", "assets/")

    # Cache the lookup dictionary in the env object so we don't rebuild it
    # for every single image within the same markdown file.
    if "_media_lookup" not in env:
        env["_media_lookup"] = {os.path.basename(p): p for p in media_paths}
        # Also support exact vault paths if used
        env["_media_lookup"].update({p: p for p in media_paths})

    path_lookup = env["_media_lookup"]
    vault_path = path_lookup.get(filename, filename)

    # Construct web URL
    web_src = f"{build_dir_prefix}{os.path.basename(vault_path)}"

    # Determine HTML tag based on extension
    ext = os.path.splitext(vault_path)[1].lower()

    if ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp']:
        w_attr = f' width="{width}"' if width else ""
        h_attr = f' height="{height}"' if height else ""
        alt_attr = f' alt="{alt_text}"'
        return f'<img src="{web_src}"{alt_attr}{w_attr}{h_attr} />'

    elif ext in ['.mp4', '.webm', '.ogg', '.mov']:
        w_attr = f' width="{width}"' if width else ""
        return f'<video src="{web_src}" controls{w_attr}></video>'

    elif ext in ['.mp3', '.wav', '.m4a', '.flac']:
        return f'<audio src="{web_src}" controls></audio>'

    elif ext == '.pdf':
        return f'<iframe src="{web_src}" width="100%" height="600px"></iframe>'

    else:  # Fallback
        return f'<a href="{web_src}" class="internal-embed">{filename}</a>'


def obsidian_embed_plugin(md: MarkdownIt):
    """Registers the Obsidian embed rules to the MarkdownIt instance"""
    md.inline.ruler.before("image", "obsidian_embed", obsidian_embed_rule)
    md.add_render_rule("obsidian_embed", render_obsidian_embed)
