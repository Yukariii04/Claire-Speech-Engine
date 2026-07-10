################################################################################
#                     THE CLAIRE SPEECH ENGINE (CSE)
#
# Release Engineering Checklist
#
# Release : v1.0.0-beta
# Version : 1.0.0
#
################################################################################
````

# Objective

Publish the Claire Speech Engine as a real Python package.

This is the final milestone of Phase 2.

No framework features shall be added.

Only release engineering tasks are permitted.

---

# 1. Packaging Review

Verify

- pyproject.toml
- package metadata
- version
- classifiers
- dependencies
- optional dependencies
- entry points
- license metadata

---

# 2. Build Verification

Run

```bash
python -m build
```

Ensure

```
dist/

wheel

tar.gz
```

are produced successfully.

---

# 3. Twine Validation

Run

```bash
twine check dist/*
```

Resolve all warnings.

---

# 4. TestPyPI

Upload to

```
TestPyPI
```

Install from TestPyPI.

Verify

```bash
pip install claire-speech-engine
```

works.

---

# 5. PyPI

After successful TestPyPI verification

Publish to

```
PyPI
```

---

# 6. Fresh Environment Validation

Create a completely clean Python environment.

Install

```bash
pip install claire-speech-engine
```

Run

```python
from cse import SpeechEngine
```

without using the repository source.

---

# 7. COLAB-001

Modify

```
COLAB-001
```

to install

```bash
pip install claire-speech-engine
```

instead of GitHub.

Verify

Fish Speech

StyleTTS2

generate audio successfully.

---

# 8. GitHub Release

Publish Release Notes.

Attach

wheel

source distribution

Release Notes

---

# 9. Documentation

Update README

Replace GitHub installation examples with

```bash
pip install claire-speech-engine
```

where appropriate.

---

# 10. Acceptance Criteria

Release complete when

✓ Package builds

✓ Twine passes

✓ TestPyPI passes

✓ PyPI passes

✓ pip install works

✓ COLAB-001 works using PyPI

✓ GitHub Release published

################################################################################

END OF RELEASE-001

################################################################################

---

# AI Instructions

Do not modify the framework.

Do not add features.

Focus entirely on packaging, publishing, and validation.

Treat this as release engineering rather than product development.
```

---

# 📋 End-of-Document Action

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

DOCUMENT TYPE

Release Engineering

STORE

docs/Releases/RELEASE-001.md

FEED TO ANTIGRAVITY

✅ YES

IMPLEMENT

✅ YES

AFTER IMPLEMENTATION

1. Publish to TestPyPI.
2. Verify installation.
3. Publish to PyPI.
4. Update COLAB-001 to use:
   pip install claire-speech-engine
5. Run COLAB-001 end-to-end.
6. Send the updated repository ZIP (if any changes), release notes, and the final COLAB-001 notebook for review.

REVIEW WILL VERIFY

• Packaging
• PyPI installation
• TestPyPI validation
• GitHub release
• Notebook reproducibility
• Documentation updates

COMMIT MESSAGE

chore: prepare and publish Claire Speech Engine v1.0.0-beta

TAG

v1.0.0-beta (already created)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

# 🚀 After RELEASE-001

The roadmap becomes:

```text
v1.0.0-beta
        │
        ▼
GitHub Release
        │
        ▼
TestPyPI
        │
        ▼
PyPI
        │
        ▼
COLAB-001
(using pip install)
        │
        ▼
Framework Certified
        │
        ▼
CPE-000
Claire Performance Engine Architecture
        │
        ▼
RFD-001
Performance Graph Specification
```

## One suggestion before publishing to the real PyPI

I recommend using **TestPyPI first** rather than publishing directly to PyPI. It lets you verify:

- package metadata,
- dependency resolution,
- installation,
- and your updated `COLAB-001` workflow

without consuming the permanent project name or release history on the real PyPI. Once `pip install` works cleanly from TestPyPI and the notebook completes successfully in a fresh environment, you can publish the exact same build to PyPI with much more confidence. That gives you a clean transition from framework development into the research phase without mixing packaging issues into CPE development.