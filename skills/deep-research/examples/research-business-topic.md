# Example: Business Research

This example demonstrates using Deep Research for a business topic.

## Conversation

```
User: "I need to understand the business implications of AI regulation in the EU
      for our SaaS product. We're a B2B SaaS company offering AI-powered analytics.
      What should we prepare for in terms of compliance and business impact?"

Assistant: "I'll research the AI regulation landscape in the EU, focusing on
      business implications for SaaS companies and compliance requirements."

/deep-research
```

## What Deep Research Detects

### Intent Analysis
```yaml
primary_topic: "EU AI Regulation business impact for SaaS"
research_depth: STANDARD (business-focused)
scope_indicators: ["SaaS", "B2B", "compliance", "business impact"]
```

### Domain Detection
```yaml
primary_domains:
  - domain: "Law/Regulation"
    confidence: HIGH
    keywords: ["AI regulation", "EU", "compliance"]
    effort: 70%

  - domain: "Business"
    confidence: HIGH
    keywords: ["SaaS", "B2B", "business impact"]
    effort: 70%

secondary_domains:
  - domain: "Technology/AI"
    confidence: MEDIUM
    keywords: ["AI", "analytics", "AI-powered"]
    effort: 30%

  - domain: "Ethics"
    confidence: MEDIUM
    keywords: ["AI regulation", "ethics"]
    effort: 30%
```

### Research Plan Generated
```yaml
Law/Regulation (10 queries):
  - "EU AI Act 2025 requirements"
  - "EU AI Act compliance for SaaS companies"
  - "EU AI Act risk classification system"
  - "EU AI Act penalties and enforcement"
  - "EU AI Act B2B SaaS implications"
  - "EU AI Act AI analytics classification"
  - "EU AI Act timeline implementation"
  - "EU AI Act vs GDPR differences"
  - "EU AI Act conformity assessment"
  - "EU AI Act documentation requirements"

Business (10 queries):
  - "EU AI Act business impact SaaS"
  - "AI regulation SaaS market impact"
  - "EU AI Act cost of compliance"
  - "AI regulation competitive advantage SaaS"
  - "EU AI Act B2B SaaS opportunities"
  - "AI compliance as business differentiator"
  - "EU AI Act SaaS pricing implications"
  - "AI regulation SaaS vendor risk"
  - "EU AI Act market entry requirements"
  - "AI compliance certification business value"

Technology/AI (5 queries):
  - "EU AI Act technical requirements"
  - "AI-powered analytics risk classification"
  - "AI transparency requirements SaaS"
  - "AI model documentation compliance"
  - "AI governance technical implementation"

Ethics (5 queries):
  - "AI ethics regulation alignment"
  - "EU AI Act ethical AI principles"
  - "AI bias detection compliance"
  - "ethical AI business value"
  - "AI ethics certification frameworks"
```

## Sample Output (Executive Summary)

```markdown
# Deep Research Report: EU AI Regulation Business Impact for SaaS

**Executive Summary:**

The EU AI Act introduces a risk-based regulatory framework that will significantly impact B2B SaaS companies offering AI-powered analytics. Under the Act, AI-powered analytics would likely be classified as "limited risk" or "high-risk" depending on specific use cases, requiring conformity assessments, technical documentation, and transparency obligations. The business impact is substantial: compliance costs for SME SaaS companies are estimated at €50K-200K annually, primarily for documentation, monitoring, and potential third-party audits. However, research reveals a strategic opportunity—early compliance can become a competitive differentiator, with 73% of enterprise B2B customers indicating they would pay a premium for AI-compliant vendors. The Act will be fully enforceable by 2027, with phased implementation starting in 2025. For B2B SaaS analytics companies, the recommended approach is to begin compliance preparation immediately, focusing on documentation, transparency features, and AI governance systems—not just to avoid penalties (up to 6% of global revenue), but to capture first-mover advantage in the compliance-aware market.

**Key Recommendation:** Begin immediate compliance preparation with focus on documentation and transparency; position compliance as a competitive differentiator in enterprise sales.

**Confidence:** MEDIUM (regulation still evolving, but based on official EU documents and expert analysis)
```

## Key Findings by Domain

### Law/Regulation
- EU AI Act introduces risk-based classification (unacceptable, high, limited, minimal)
- AI-powered analytics typically classified as "limited" or "high" risk
- Compliance requires conformity assessment, technical documentation, monitoring
- Penalties up to 6% of global worldwide turnover
- Phased implementation: 2025-2027

### Business
- Compliance costs for SME SaaS: €50K-200K annually
- Enterprise customers prefer AI-compliant vendors (73% survey)
- Early adopters gaining competitive advantage
- Compliance can be priced into enterprise contracts
- Market分化 between compliant and non-compliant vendors expected

### Technology
- Technical documentation requirements are extensive
- Transparency and explainability features required
- Data governance and quality standards mandated
- Human oversight requirements for high-risk systems
- Continuous monitoring and logging required

### Ethics
- Ethical AI principles align with compliance requirements
- Bias detection and mitigation increasingly expected
- Ethical certifications emerging (IEEE, ISO)
- Ethics-by-design reduces compliance burden

### Cross-Domain Insights
- **Regulation + Business:** Compliance costs create barrier to entry (reduces competition)
- **Technology + Ethics:** Ethical design reduces compliance burden long-term
- **Business + Ethics:** Ethics-based marketing resonates with enterprise buyers

## Recommendations

### For B2B SaaS Analytics Companies

**1. Begin Compliance Preparation Now (HIGH confidence)**
- Conduct internal risk classification
- Start technical documentation
- Implement AI governance framework
- Budget for compliance costs

**Rationale:** Compliance takes 12-24 months for established systems. Early movers capture advantage.

**2. Position Compliance as Competitive Differentiator (HIGH confidence)**
- Market compliance certification in sales
- Offer compliance features as premium tier
- Publish transparency reports
- Highlight compliance in enterprise proposals

**Rationale:** Enterprise buyers willing to pay premium for compliant vendors. First-mover advantage exists.

**3. Implement Ethics-by-Design (MEDIUM confidence)**
- Bias detection and monitoring
- Explainability features
- Human oversight mechanisms
- Ethical review processes

**Rationale:** Ethics reduces compliance burden and appeals to enterprise buyers.

**4. Prepare for Risk Classification Specific to Use Cases (HIGH confidence)**
- Document each AI use case
- Prepare risk assessment for each
- Implement appropriate controls per risk level
- Maintain separate documentation for each use case

**Rationale:** Risk classification is use-case specific, not product-wide. Proper classification reduces requirements.

## Business Strategy Implications

### Market Opportunities
- "Compliance-ready" positioning in enterprise sales
- Premium pricing for compliant features
- Competitive moat through compliance investment
- Early mover advantage in evolving market

### Risk Mitigation
- Avoid 6% revenue penalties
- Protect market access to EU customers
- Prevent vendor lock-in to non-compliant tools
- Future-proof against similar regulations (UK, US)

### Investment Priorities
1. Documentation and governance systems (immediate)
2. Transparency and explainability features (6-12 months)
3. Third-party compliance certification (12-18 months)
4. Ethics frameworks and bias detection (ongoing)

## Sources

- High credibility: 18 sources (EU official documents, legal analysis, academic papers)
- Medium credibility: 14 sources (industry reports, business publications, expert commentary)
- Low credibility: 3 sources (blog posts, forums)

Total: 35 sources consulted across 4 domains.

## Research Quality Assessment

- **Validation:** Triangulated across 30+ sources
- **Credibility:** 51% HIGH, 40% MEDIUM, 9% LOW
- **Cross-Domain:** 75% of findings validated across multiple domains
- **Consensus:** Strong consensus on regulatory framework; moderate on business impact estimates

## Usage Tips for Business Research

1. **Specify business model:** "B2B SaaS" helped identify relevant business impacts

2. **Include product context:** "AI-powered analytics" enabled risk classification research

3. **Ask strategic questions:** "What should we prepare for?" encouraged forward-looking recommendations

4. **Business terminology:** Using terms like "competitive advantage" and "market impact" improved business domain analysis
