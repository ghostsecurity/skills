# Repository Context

## Repository Overview
[2-5 sentence overview of the entire repository]

---

## Project: [human-readable name]

### Detection
- **ID**: [base_path (type), e.g., ". (backend)", "api (frontend)"]
- **Type**: [backend|frontend|mobile|cli|library|iac]
- **Base Path**: [relative path or "."]
- **Languages**: [comma-separated]
- **Frameworks**: [comma-separated, or "none"]
- **Dependency Files**: [comma-separated paths]
- **Extensions**: [comma-separated, e.g., ".go", ".ts"]
- **Evidence**: [1-3 sentences from detector explaining why this is a distinct project]

### Summary
[~300 word architectural summary from summarizer]

### Sensitive Data Types
[comma-separated from: PII, payment, login, health, financial, biometric, location, secrets — or "none"]

### Business Criticality
[high|medium|low]

### Component Map
| Directory | Type | Criticality | Description |
|-----------|------|-------------|-------------|
| src/controllers | controller | 0.9 | HTTP request handlers for API endpoints |
| src/middleware | middleware | 1.0 | Auth and validation middleware |
| src/models | models | 0.6 | Data models and entity definitions |
| ... | ... | ... | ... |

### Evidence
[From summarizer: specific files examined, patterns found, reasoning for classifications]

---

## Project: [next project]
[same structure repeats]
