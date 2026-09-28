# Research Use Cases

Concrete ways to use this platform as a research tool for Human-AI collaboration studies.

## 1. Claim Verification (primary use case)

Upload a document, extract factual claims, and verify them with web search and scraping.

- Protocol: [demo-claim-verification.md](demo-claim-verification.md)
- Metrics: factuality, citation quality, coverage, latency, token cost

## 2. Tool-Augmented vs. Tool-Free Answering

Compare answers with tools enabled/disabled on the same questions.

```csv
question_id,condition,tools_used,answer,claims,supported_claims,unsupported_claims,latency_ms,tokens
1,no_tools,"",...,3,1,2,4100,520
1,tools,"search,scrape",...,3,3,0,9200,1450
```

## 3. Multi-Provider Comparison

The platform supports OpenAI, Anthropic, and Google models behind one API.
Compare the same prompt across providers using `/api/v1/chat/stream`:

```bash
for model in gpt-4o-mini claude-3-5-sonnet gemini-1.5-flash; do
  curl -s http://localhost:3211/api/v1/chat/complete \
    -H "Content-Type: application/json" \
    -d "{\"provider\":\"$provider\",\"message\":\"...\"}" > "out-$model.json"
done
```

Metrics: answer quality rubric, latency, cost per 1k tokens.

## 4. File-Context Reasoning

Upload policy documents and ask the system to answer compliance questions with citations.

- Endpoints: `POST /api/v1/files/upload`, then reference the file in chat
- Metrics: answer accuracy vs. a gold-standard key, citation precision

## 5. Interaction Studies (Human-AI)

The streaming chat UI records conversation history. For behavioral studies:

- Task participants through scenario-based questions
- Export conversation logs from the DB
- Code user prompts (delegation, verification, correction) for analysis

## Data Recording Template

```csv
session_id,condition,provider,message_number,prompt_tokens,completion_tokens,latency_ms,user_rating,notes
```

## Privacy Checklist Before Running a Study

- [ ] Use synthetic or de-identified documents
- [ ] Store API keys via environment variables only
- [ ] Clear `uploads/` between participants
- [ ] Disclose that prompts are sent to third-party LLM providers
