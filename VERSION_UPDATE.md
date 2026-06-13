# Version Update Records

| Date | Name | Summary | Author | Notes |
|------|------|---------|--------|-------|
| 2026-06-12 | AI Review Groq Fallback | Added Groq as third fallback provider (Gemini → NVIDIA → Groq) | opencode | code_review.py rewritten with 3-tier fallback; GROQ_API_KEY secret added; ruleset narrowed to main only |
| 2026-06-12 | Security Fixes | Add .env to .gitignore; fix SECURITY.md to use private reporting | opencode | Prevents accidental secret commits; fixes contradictory public-issue disclosure policy |
