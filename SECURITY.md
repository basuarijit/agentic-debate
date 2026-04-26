# Security

## Secrets

Do not commit secrets, API keys, tokens, private certificates, or credentials.

Use environment variables and local `.env` files for runtime secrets. Commit only `.env.example` files with variable names and safe placeholder values.

## Planned Controls

Future DevSecOps work should define:

- Secret scanning
- Dependency vulnerability scanning
- Static analysis
- Test gates
- Build provenance
- Environment-specific deployment controls

## Reporting

During development, security issues should be captured as backlog items and linked to the relevant requirement, user story, or design decision.

