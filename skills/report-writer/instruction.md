# Report Writer Skill — Quick-Start Reference

A one-page cheat sheet for the deep agent. Read `instructions.md` for the full template.

## When to Write a Report
| Trigger | Write report? |
|---------|--------------|
| Research / multi-step question answered | YES |
| Code written or debugged | YES |
| User explicitly asks for a report/doc | YES |
| Greeting / one-liner clarification | NO |
| Meta-question about the agent itself | NO |

## File Naming
```
/reports/<3-6-word-kebab-slug>-report.md

Examples:
  /reports/s3-upload-python-report.md
  /reports/langgraph-memory-report.md
  /reports/aws-serverless-api-design-report.md
```

## Report Skeleton (fill in the blanks)
```markdown
# Report: <Short Title>

**Date:** <YYYY-MM-DD>
**Requested by:** user
**Skills used:** <skill names, or "none">

## 1. Question
<One or two sentences restating what the user asked.>

## 2. Approach
- <What you did step 1>
- <What you did step 2>
- ...

## 3. Key Findings
- <Fact 1>
- <Fact 2>
- ...

## 4. Answer
<Final answer, condensed. Include essential code block(s).>

## 5. Sources / Tools Used
<Skill files, tool calls, URLs, or "model knowledge".>

## 6. Caveats & Next Steps
<Limitations and 1-3 follow-up suggestions.>
```

## Save and Confirm
1. Call `write_file(file_path="/reports/<slug>-report.md", content=<report>)`
2. End your chat reply with exactly:
   `Report saved to /reports/<filename>`

## Quality Checks Before Saving
- [ ] Self-contained: readable without seeing the chat
- [ ] Faithful: no claims beyond what was in the answer
- [ ] Concise: 150-400 words + code (not a transcript)
- [ ] Code: final working version only
