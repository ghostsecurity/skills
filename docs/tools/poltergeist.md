# Poltergeist

Poltergeist is the secret scanner in Ghost Security AppSec Skills. It scans source code for leaked API keys, tokens, certificates, and credentials using a dual-engine architecture that combines speed with precision.

## Architecture

### Dual-engine design

Poltergeist uses two regex engines and selects the best one automatically:

**Hyperscan engine** -- a high-performance multi-pattern matcher. It evaluates all rules simultaneously in a single pass over the file content, maintaining consistent scan times regardless of rule count. Hyperscan scans the Linux kernel (1.4 GB) in about 8 seconds at every benchmarked rule count from 16 to 1016.

**Go regex engine** -- a fallback engine for environments where Hyperscan isn't available, and the default for single-pattern scans. Performance scales linearly with rule count.

In `auto` mode (the default), Poltergeist uses Hyperscan for multi-pattern scans when available, and Go regex for single patterns or when Hyperscan isn't installed.

### Entropy analysis

Every match is evaluated for Shannon entropy (a measure of randomness). Each rule defines a minimum entropy threshold tuned to its specific pattern. Matches below the threshold are filtered out by default.

For example:
- A generic password variable (`ghost.generic.3`) has a threshold of 3.5 bits, because passwords can be relatively short
- An AWS session token (`ghost.aws.2`) has a threshold of 5.5 bits, because these tokens are long base64 strings with high randomness
- An OpenAI API key (`ghost.openai.1`) has a threshold of 5.1 bits

The `-low-entropy` flag shows matches below threshold, useful for debugging rules or investigating potential issues.

### Automatic redaction

Poltergeist redacts secrets in its output by default. Redaction offsets are specified in individual rules and vary by secret type:

```text
sk-proj-0JdlO*****vSYA    (OpenAI key)
Bu/9*****KBBJ             (AWS secret)
```

Scan output is safe to share, log, or include in reports without exposing actual credential values.

## Key features

- **163 built-in rules** covering 108 providers, including cloud providers, AI services, git platforms, CI/CD, communication tools, databases, payment processors, and more
- **Dual-engine** architecture with automatic engine selection
- **Entropy filtering** to reduce false positives from low-randomness matches
- **Automatic redaction** of secrets in all output formats
- **Multiple output formats** -- text (colored), JSON (machine-readable), Markdown (reports)
- **Custom rules** -- extend with your own YAML rule files
- **Binary file detection** -- automatically skips binary files, archives, and media
- **Embedded rules** -- rules compiled into the binary, no external files needed at runtime

## CLI reference

### Usage

```shell
poltergeist [options] <path> [pattern1] [pattern2] ...
```

Scans the file or directory at `<path>`. Optionally provide one or more regex patterns to match. Inline patterns replace the built-in rules and combine with any `-rules` file. The built-in rules load only when neither `-rules` nor an inline pattern is given.

### Flags

| Flag | Default | Description |
|---|---|---|
| `-engine` | `auto` | Pattern matching engine: `auto`, `go`, or `hyperscan` |
| `-rules` | -- | Path to YAML rule file or directory of rule files |
| `-format` | `text` | Output format: `text`, `json`, or `md` |
| `-output` | -- | Write output to file (auto-detects format from `.json` or `.md` extension) |
| `-dnr` | `false` | Do not redact: show full secret values. In JSON output, each result also carries a `match` field with the full value. Markdown output stays redacted |
| `-low-entropy` | `false` | Show matches below entropy threshold |
| `-no-color` | `false` | Disable colored text output |
| `-version` | -- | Show version information |
| `-help` | -- | Show usage information |

### Examples

```shell
# Scan a directory with default rules
poltergeist /path/to/code

# JSON output to a file for CI/CD integration
poltergeist -output results.json /path/to/code

# Markdown report to file
poltergeist -output report.md /path/to/code

# Custom rules
poltergeist -rules ./my-rules.yaml /path/to/code

# Force Hyperscan engine
poltergeist -engine hyperscan /path/to/code

# Show low-entropy matches for investigation
poltergeist -low-entropy /path/to/code

# Combine custom rules with inline patterns
poltergeist -rules ./rules /path/to/code "api[_-]?key\s*[:=]\s*['\"]([^'\"]+)"
```

### Output formats

**Text** (default) -- colored, human-readable output grouped by file:

```text
──────────────────────────────────────────────────
 SCAN SUMMARY
──────────────────────────────────────────────────

Files scanned:  1
Total content:  180 B
Secrets found:  1

● src/config/api.ts  (1 matches)
  └─ Line 1: OpenAI API Key
     sk-proj-0JdlO*****vSYA
     ID: ghost.openai.1
     Entropy: 5.75 | Threshold: 5.10 | Met: Yes

──────────────────────────────────────────────────
Files skipped: 0 (binary/large files)
Scan completed in 676.125µs

! Review and address the secrets above.
```

**JSON** -- structured output for programmatic consumption:

```json
{
  "summary": {
    "files_scanned": 1,
    "files_skipped": 0,
    "total_bytes": 180,
    "matches_found": 1,
    "high_entropy_matches": 1,
    "low_entropy_matches": 0
  },
  "results": [
    {
      "file_path": "src/config/api.ts",
      "line_number": 1,
      "redacted": "sk-proj-0JdlO*****vSYA",
      "rule_name": "OpenAI API Key",
      "rule_id": "ghost.openai.1",
      "entropy": 5.746020300696253,
      "rule_entropy_threshold": 5.1,
      "rule_entropy_threshold_met": true
    }
  ]
}
```

**Markdown** -- report format with tables and findings sections, suitable for documentation or issue tracking.

### Exit codes

The exit codes are the same in every output format.

- `0` -- scan completed, no secrets found
- `1` -- scan completed and secrets were found, or the scan failed

## Rule authoring

There are two main strategies for writing secret detection patterns with Poltergeist:

- Explicit secret format, when the format is known and static
- Variable declaration detection (targeting likely ways the secret might be declared as a variable)

In general, we prefer to write more rules that are more precise, more specific, and easier to reason about, rather than fewer rules that are more general. The performance penalty of more rules is negligible.

### Explicit secret format

When the format is known and static, we can use a regex pattern to match the secret. Often these types of secrets have a known prefix, a fixed length, and sometimes a magic string (e.g. OpenAI API keys have a magic string `T3BlbkFJ`).

### Variable declaration detection

When the format is not known, we look for likely ways the secret might be present in source code when declared as a variable. We look for variables that are unique to the secret provider. For example, Azure Storage Account keys are a fixed length, but no predictable format. We try to match variations on `Azure` (case insensitive) and a high entropy fixed length string. Avoid generic variable names like `TOKEN` as it will be more difficult to map back to a specific secret provider.

#### Capture group

Currently we only expect one capture group from the regex pattern. If the secret is a known format, the capture group should be just the secret itself.

The Huggingface rule, for example:

```
(?x)
  \b
    (hf_(?i)[A-Z0-9]{34})
  \b
```

Matches the token like `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` exactly.

However, if we are looking for a variable declaration secret, we capture the variable name in addition to the secret value.

The Clearbit rule, for example:

```
(?x)
  \b
    (
      (?i)clearbit\w*(?:token|key|secret)\w*
      [\W]{0,40}?
      [A-Z0-9_-]{35}
    )
  \b
```

Matches the `CLEARBIT_TOKEN` variable as well as the secret value in the case of `export CLEARBIT_TOKEN="td3aCzKhouIIgiua1d6Yvl5veaTNHMFbb7H"`.

Though this lowers the entropy of the match overall, it allows us to see (even in redacted logs) more information about the match. It is easier to understand how to match occurred and potentially if/how the match is a false positive.

#### Non-word matcher

We enlarged the non-word matcher from 10 to 40 characters to allow for more whitespace between the variable name and the secret(`[\W]{0,10}?` -> `[\W]{0,40}?`).

### Backwards compatibility

Do not change rule numbers. If a rule needs to be deprecated, delete it without changing the number of other rules.

### YAML Format

Example Poltergeist rule file:

```yaml
rules:
  - name: Anthropic API Key
    id: ghost.anthropic.1
    description: Matches an Anthropic API key.
    tags:
      - api
      - anthropic
    pattern: |
      (?x)
        \b
          (sk-ant-api\d{2}-(?i)[A-Z0-9_-]{86}-(?i)[A-Z0-9_]{6}AA)
        \b
    entropy: 5.1
    redact: [16, 4]
    tests:
      assert:
        - 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
      assert_not:
        - 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
    history:
      - 2025-08-02 initial version
```

#### Rule Components

**Required**

- `name`: The name of the rule
- `id`: Globally unique identifier for the rule
- `description`: The description of the rule. This is user facing content
- `tags`: The tags used to categorize the rule
- `pattern`: The regex pattern for matching
- `entropy`: The minimum entropy threshold for matches
- `redact`: The prefix and suffix of the match to preserve, redact the rest
- `tests`: The test cases for rule validation
- `history`: The change history of the rule (at least one entry)

**Optional**

- `refs`: URLs of external resources supporting the secret detection approach or explaining when/where/how the secret is typically used
- `notes`: useful notes or references for future rule authors/editors

### False Positive Mitigation

We employ some common techniques to reduce false positives in real-time during the scan.

### Boundaries

Use word boundaries (`\b`) when possible to reduce false positives. Word boundaries indicate where non-word characters occur. This helps prevent false positives from matching in the middle of a word.

### Entropy

Use entropy to filter out false positives. True secrets, keys, and cryptographic material should have high entropy. Specifying the `entropy` field forces the rule to only match secrets with an entropy greater than or equal to the specified value.

The calculated Shannon entropy and the rule threshold are both included in the output, allowing you to see exactly why a match was flagged or filtered.

### Stop Words

Stop words are words that are common in the English language and should not appear in most valid secrets.

**Not implemented**: we aren't yet checking for stop words in the matching engine, but the accompanying [skill](../capabilities/secret-scanning.md) DOES consider common stop words during analysis

### Redaction

The redaction points are the prefix and suffix of the match to preserve, the rest of the match is redacted.

For example, if the match is `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`, and the redaction points are `[16, 4]`, the redacted match will be:

```
sk-ant-api03-bvf*****oAAA
```

The first `16` and the last `4` characters are preserved. The rest of the match is redacted.

### Performance Tips

1. **Use specific patterns**: More specific regex patterns are faster than broad ones
2. **Boundaries**: Use `\b` boundaries in regex patterns when possible to reduce false positives

## Skill integration

When used through the `ghost-scan-secrets` skill, Poltergeist's JSON output feeds into AI context assessment. The skill parses matches into candidates, assesses each one (real vs. placeholder, hardcoded vs. environment variable, production vs. test), and writes confirmed findings with severity assessments and remediation guidance. See [Secret scanning](../capabilities/secret-scanning.md) for details.

---

Previous: [Reporting](../capabilities/reporting.md) | Next: [Wraith](wraith.md) | [Docs home](../../README.md#documentation)
