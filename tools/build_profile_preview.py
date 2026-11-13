# /// script
# requires-python = ">=3.11"
# dependencies = ["markdown-it-py>=3,<5"]
# ///
"""Refresh the local README preview: uv run --no-cache tools/build_profile_preview.py.

The surrounding theme controls and stylesheet stay in preview.html; its article
is always rebuilt from README.md so project descriptions cannot drift apart.
"""
from pathlib import Path

from markdown_it import MarkdownIt

ROOT = Path(__file__).resolve().parents[1]
preview = ROOT / "preview.html"
shell, marker, _ = preview.read_text().partition("<article>")
if not marker:
    raise RuntimeError("preview.html must contain the preview shell and <article> marker")
body = MarkdownIt("commonmark", {"html": True}).render((ROOT / "README.md").read_text())
# This preview is trusted local README HTML, not a general-purpose Markdown host.
controls = """</article></main><script>
const params = new URLSearchParams(location.search);
const theme = params.get('theme') || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
document.documentElement.dataset.theme = theme === 'dark' ? 'dark' : 'light';
document.querySelector('#replay').href = `?theme=${document.documentElement.dataset.theme}`;
</script><script src="assets/summary-replay.js"></script></body></html>
"""
preview.write_text(shell + marker + "\n" + body + controls)
print("Rebuilt preview.html from README.md")
