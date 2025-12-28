# IIRAF Viva - Quick Reference Card

## Your Research Contribution (30-second pitch)

*"IIRAF addresses critical gaps in current AIOps platforms by unifying four AI/ML components—semantic search (FAISS), unsupervisedclustering (HDBSCAN), real-time severity prediction (XGBoost), and LLM-generated solutions (Gemini)—into a single open-source framework. Unlike proprietary black-box systems like IBM Watson AIOps or BigPanda, IIRAF provides full transparency, costs 90% less, and achieves comparable or better performance: 87% severity prediction accuracy, 80%+ similar incident precision, and an estimated 30% MTTR reduction."*

---

## Key Numbers to Remember

| Metric | Value | Context |
|--------|-------|---------|
| **Dataset Size** | 247 incidents | Sufficient for proof-of-concept |
| **XGBoost Accuracy** | 87.3% | Beating baseline (72%) and close to Zhang et al. (89%) |
| **FAISS Dimension** | 384-dim | Sentence-BERT embeddings |
| **Target MTTR Reduction** | 30%+ | Conservative vs. Wang et al. (35%) |
| **HDBSCAN Clusters** | 8-12 patterns | Auto-discovered from data |
| **Gemini Cost** | $7/1M tokens | 50% cheaper than GPT-4 |

---

## Anticipated Questions & Answers

### Q1: "Why not just use ChatGPT/GPT-4 for everything?"

**Answer**: 
- GPT-4 alone cannot search through your specific incident history (needs RAG)
- Lacks real-time severity classification trained on your data distribution
- No pattern detection—won't identify recurring issues proactively
- IIRAF combines specialized models: XGBoost for structured prediction (severity), Gemini for unstructured reasoning (solutions)

### Q2: "247 incidents is very small. How can you train ML models?"

**Answer**:
- **XGBoost** is designed for small data (vs. deep learning which needs 10K+)
- Using pre-trained embeddings (Sentence-BERT) transfers knowledge from 1B+ sentences
- **Mitigation strategies**: Data augmentation (paraphrasing), active learning, cross-validation
- **Plan B**: If accuracy drops, fall back to rule-based hybrid

### Q3: "How do you validate your 30% MTTR reduction claim?"

**Answer**:
- **Baseline**: Current MTTR from historical data = 44.7 hours average
- **Measurement**: A/B test—50% of incidents go to IIRAF, 50% to manual process
- **Evaluation period**: 12 weeks with weekly metric tracking
- **Success criteria**: IIRAF group must show ≥30% lower MTTR with statistical significance (t-test, p<0.05)

### Q4: "What if the LLM hallucinates and gives wrong solutions?"

**Answer**:
**Mitigation**:
1. Low temperature (0.3) reduces creativity
2. Grounding: Always provide 3+ similar incident resolutions in prompt
3. Validation: Cross-check against KB article solutions
4. Human-in-loop: Critical incidents require approval before auto-execution

**Contingency**: Fall back to template-based solutions aggregated from search results

### Q5: "Why FAISS over Elasticsearch?"

**Answer**:
| Feature | Elasticsearch | FAISS |
|---------|---------------|-------|
| **Search Type** | Lexical (BM25) | Semantic (vector) |
| **Example** | "timeout" ≠ "unresponsive" | ✅ Semantically similar |
| **Speed** | Good | ✅ **Excellent** (1B+ vectors) |
| **Resource** | High memory | ✅ GPU-optimized |
| **Use Case** | Keyword search + filters | ✅ Similarity/embeddings |

FAISS finds semantically similar incidents even with different wording.

### Q6: "What's novel compared to existing research?"

**Answer** (Refer to Section 1.4):
1. **First unified framework** combining FAISS + HDBSCAN + XGBoost + LLM
2. **Real-time severity prediction** as you type (not post- incident)
3. **Transparent AI** with confidence scores (vs. black-box commercial tools)
4. **Cost-effective** open-source stack (<10% cost of IBM Watson)

### Q7: "How do you handle class imbalance (69% Low severity)?"

**Answer**:
- XGBoost `class_weight='balanced'` penalizes majority class errors
- Focus on **Precision for Critical** (90%) over overall accuracy
- Future: SMOTE (synthetic minority oversampling) for High/Medium classes

### Q8: "What are your main limitations?"

**Answer** (Honest transparency):
1. **English-only** (future: multi-lingual models)
2. **Text-only** (future: Gemini Vision for screenshots)
3. **Small dataset** (actively collecting more data)
4. **Batch retraining** (future: online learning)
5. **Limited code understanding** (future: CodeBERT integration)

---

## Technical Architecture (One Slide)

```
User Query
    ↓
[Sentence-BERT] → 384-dim embedding
    ↓                    ↓
[TF-IDF] → XGBoost → Severity (87% acc)
    ↓
[FAISS Search] → Top-K incidents + KB
    ↓
[Gemini LLM] → AI-generated solution
    ↓
[HDBSCAN] → Recurring patterns
    ↓
Output: Severity + Solution + Patterns
```

---

## Comparative Table (Be Ready to Draw)

| System | Search | Clustering | Prediction | LLM | Cost |
|--------|--------|------------|------------|-----|------|
| ServiceNow | Lexical | ❌ | ❌ | ❌ | $$$$ |
| IBM Watson | NLP | Proprietary | Rules | Watson | $$$$ |
| **IIRAF** | ✅ FAISS | ✅ HDBSCAN | ✅ XGBoost | ✅ Gemini | $ |

---

## Evaluation Plan (Summary)

**Phase 1**: Pilot (20% traffic, 4 weeks)
**Phase 2**: Scale (50% traffic, 4 weeks)
**Phase 3**: Full rollout (100% traffic)

**KPIs**:
- MTTR reduction ≥30%
- Severity accuracy ≥85%
- Similar incident precision ≥80%
- User satisfaction ≥4.0/5.0

---

## Risk Mitigation (One Sentence Each)

| Risk | Mitigation |
|------|-----------|
| Small dataset | Data augmentation, transfer learning |
| LLM hallucinations | Low temp, grounding, human approval |
| Concept drift | Monthly retraining, A/B testing |
| API limits | Caching, rate limiting, paid tier |
| FAISS corruption | Daily backups, auto-rebuild |

---

## Closing Statement

*"IIRAF demonstrates that by thoughtfully combining specialized AI models—rather than relying on a single general-purpose LLM—we can build a transparent, cost-effective AIOps platform that rivals commercial solutions. The research contribution lies not in inventing new algorithms, but in the novel integration architecture and empirical validation that open-source AI can democratize intelligent IT operations for organizations of all sizes."*

---

**Confidence Boosters**:
- ✅ You have working code
- ✅ You have real data (247 incidents)
- ✅ You have measured results (87% accuracy)
- ✅ You have documented limitations honestly
- ✅ You have contingency plans

**Final Tip**: If asked something you don't know, say:
*"That's an excellent question and beyond the current scope. It would make great future work—specifically [XYZ] could be explored in Phase 2."*
