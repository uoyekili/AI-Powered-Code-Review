CODE_REVIEW_SYSTEM_PROMPT = """You are an expert senior software architect and code reviewer.
Analyze the provided source code and metadata from a GitHub repository.
Return ONLY valid JSON matching the requested schema.
Be specific, actionable, and reference actual patterns found in the code.
Scores must be integers from 0 to 100.
Issue types must be one of: security, performance, maintainability, code-quality, architecture.
Severity must be one of: critical, high, medium, low, info.
"""

FILE_REVIEW_PROMPT = """Review the following file from a GitHub repository.

Repository: {owner}/{repo}
File path: {file_path}
Lines: {line_count}

```{extension}
{content}
```

Return JSON with this exact structure:
{{
  "summary": "brief summary of the file",
  "score": 0-100,
  "issues": [
    {{
      "line": 1,
      "type": "security|performance|maintainability|code-quality|architecture",
      "severity": "critical|high|medium|low|info",
      "title": "short title",
      "description": "detailed description",
      "suggestion": "actionable fix",
      "code": "optional code snippet"
    }}
  ]
}}
"""

AGGREGATE_REVIEW_PROMPT = """Based on the following file-level review summaries and project metadata, produce an overall assessment.

Repository: {owner}/{repo}
Primary language: {primary_language}
Metadata summary:
{metadata_summary}

File reviews summary:
{file_summaries}

Return JSON with this exact structure:
{{
  "metrics": {{
    "overall_score": 0-100,
    "security_score": 0-100,
    "performance_score": 0-100,
    "maintainability_score": 0-100,
    "code_quality_score": 0-100,
    "architecture_score": 0-100
  }},
  "issue_severity": {{
    "critical": 0,
    "high": 0,
    "medium": 0,
    "low": 0,
    "info": 0
  }},
  "issues_by_category": {{
    "security": 0,
    "performance": 0,
    "maintainability": 0,
    "code_quality": 0,
    "architecture": 0
  }}
}}
"""
