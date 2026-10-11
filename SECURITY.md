# Security policy

## Supported versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes (alpha) |

## Scope

OpenFeed is a **knowledge commons and protocol sketch**, not a remote execution platform. Knowledge Packs are data documents. Operators must decide what their agents may fetch, trust, or publish.

## Please report

- Unsafe defaults in library/CLI/MCP helpers
- Path traversal or unexpected file access when reading packs
- Misleading validation that could hide malicious pack structure
- Supply-chain issues in release artifacts (when published to PyPI)

## Out of scope

- Requests for help with unauthorized access, scraping private data, or bypassing security
- Social-engineering content aimed at operators or users

## How to report

Open a **private** security advisory on GitHub if available, or contact the repository owner via a **private** channel. Do not file public issues with exploit details until a fix is coordinated.

We aim to acknowledge reports within a reasonable time for an alpha volunteer project.
