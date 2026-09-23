# Ashleaf — Project Name and Repository Rename

Date: 2026-09-23

Status: adopted for the public project

## Decision

**Ashleaf** is the umbrella name for the open-source virtual-unwrapping research project. It joins the ash that preserved the Herculaneum scrolls with the leaves or pages we seek to recover. It is short, human, memorable, and broad enough to encompass geometry, winding evidence, surface extraction, ink detection, and future end-to-end work.

**FrameBridge** remains the name of the first released tool: the coordinate-safe, sparse validation layer for winding evidence. This keeps the product identity specific without making the whole repository sound limited to the September experiment.

Public presentation:

> Ashleaf — virtual unwrapping research for the Herculaneum scrolls. FrameBridge is its first open-source tool.

The original `new_vesuvius` name was a temporary workspace label. The GitHub repository is renamed to `stanleyngugi/ashleaf`; the public canonical URL is <https://github.com/stanleyngugi/ashleaf>. Existing historical links may redirect, but new documentation and outreach should use the canonical URL. The local workspace folder is intentionally left in place to avoid disrupting active tooling and ignored research data; a local folder name need not match the GitHub repository name.

## Migration checklist

- [x] User selected Ashleaf as the project name.
- [x] Rename GitHub repository and verify canonical URL and public visibility (`stanleyngugi/ashleaf`, public).
- [x] Update README title and project/tool hierarchy.
- [x] Update package distribution metadata while retaining `scroll_lab` import compatibility.
- [x] Update hard-coded public repository links and Colab clone instructions.
- [x] Update local `origin` URL to `https://github.com/stanleyngugi/ashleaf.git`.
- [x] Push the rename documentation as `9734b9edf36a7df7ecb9d76876a5bf1920e27b50` and verify `main` is synchronized with `origin/main`.
- [x] Run 64 unit tests and a dry-run editable installation check (`Would install ashleaf-0.1.0`).

The name check was a quick web/GitHub collision scan, not trademark clearance. No trademark, domain, PyPI publication, or exclusive use claim is made. The build-backend dry run created local `egg-info` metadata; those generated files were removed and `*.egg-info/` is ignored going forward.

GitHub's API resolves the former `stanleyngugi/new_vesuvius` path to the canonical `stanleyngugi/ashleaf` repository. This preserves access to links in already-published discussions while new links use the Ashleaf URL.
