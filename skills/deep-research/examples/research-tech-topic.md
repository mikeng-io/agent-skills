# Example: Technical Research

This example demonstrates using Deep Research for a technical topic.

## Conversation

```
User: "I need to research event sourcing with Kafka for a microservices architecture.
      I'm particularly concerned about performance implications and data consistency.
      Should we use event sourcing for our order management system?"

Assistant: "I'll perform comprehensive research on event sourcing with Kafka,
      focusing on architecture, performance, and data consistency aspects."

/deep-research
```

## What Deep Research Detects

### Intent Analysis
```yaml
primary_topic: "Event sourcing with Kafka for microservices"
research_depth: COMPREHENSIVE (implementation-focused)
scope_indicators: ["architecture", "performance", "consistency", "order management"]
```

### Domain Detection
```yaml
primary_domains:
  - domain: "Software Architecture"
    confidence: HIGH
    keywords: ["event sourcing", "microservices", "architecture"]
    effort: 70%

  - domain: "Distributed Systems"
    confidence: HIGH
    keywords: ["Kafka", "distributed", "event sourcing"]
    effort: 70%

secondary_domains:
  - domain: "Performance Engineering"
    confidence: HIGH
    keywords: ["performance", "optimization"]
    effort: 30%

  - domain: "Data Consistency"
    confidence: HIGH
    keywords: ["consistency", "data", "order management"]
    effort: 30%
```

### Research Plan Generated
```yaml
Software Architecture (10 queries):
  - "event sourcing architecture patterns"
  - "event sourcing vs traditional databases"
  - "event sourcing implementation best practices"
  - "event sourcing microservices patterns"
  - "CQRS pattern with event sourcing"
  - "event sourcing challenges and limitations"
  - "event sourcing order management systems"
  - "event sourcing event schema design"
  - "event sourcing snapshot strategies"
  - "event sourcing latest developments 2025"

Distributed Systems (10 queries):
  - "Kafka event sourcing architecture"
  - "event sourcing distributed systems challenges"
  - "event sourcing message ordering guarantees"
  - "event sourcing fault tolerance strategies"
  - "event sourcing scalability patterns"
  - "event sourcing network partition handling"
  - "event sourcing eventual consistency"
  - "event sourcing saga pattern"
  - "event sourcing consumer scaling"
  - "Kafka event sourcing performance optimization"

Performance Engineering (5 queries):
  - "event sourcing performance optimization"
  - "event sourcing read performance CQRS"
  - "event sourcing write throughput"
  - "event sourcing database performance"
  - "event caching strategies event sourcing"

Data Consistency (5 queries):
  - "event sourcing data consistency patterns"
  - "event sourcing transactional guarantees"
  - "event sourcing duplicate event handling"
  - "event sourcing consistency models"
  - "event sourcing order management consistency"
```

## Research Execution

### Parallel Researchers Spawned
```
✓ Architecture Researcher (10 queries)
✓ Distributed Systems Researcher (10 queries)
✓ Performance Researcher (5 queries)
✓ Consistency Researcher (5 queries)
✓ Cross-Domain Analyst (intersections)
```

### Tools Used
- WebSearch (Brave Search or WebSearchPrime)
- Web Reader (content extraction)
- Documentation Query (for Kafka/event sourcing docs)
- Sequential Thinking (validation)

## Sample Output (Executive Summary)

```markdown
# Deep Research Report: Event Sourcing with Kafka

**Executive Summary:**

Event sourcing with Kafka provides a scalable foundation for microservices architectures, offering strong support for event-driven communication and temporal queries. However, for order management systems specifically, the research reveals significant trade-offs: while event sourcing excels at audit trails and replay capabilities, it introduces complexity in consistency guarantees and read performance that may not justify the overhead for transactional order processing. The consensus across sources suggests that CQRS with materialized read models is essential for acceptable performance, and the saga pattern is required for distributed transactions. For most order management systems, a hybrid approach—using event sourcing for audit/history while maintaining traditional state for active operations—provides the best balance of benefits and complexity.

**Key Recommendation:** Adopt event sourcing selectively for audit trail and replay capabilities, but maintain traditional database state for active order processing to ensure transactional consistency and read performance.

**Confidence:** HIGH (based on strong consensus across 30+ sources, including official Kafka documentation, academic papers, and industry case studies)
```

## Key Findings by Domain

### Architecture
- Event sourcing provides immutable audit trails by design
- CQRS is practically mandatory for read performance
- Schema evolution requires careful planning
- Snapshot strategies needed for long-running aggregates

### Performance
- Write performance is excellent (append-only)
- Read performance requires materialized views (CQRS)
- Event replay can be resource-intensive
- Caching strategies essential for production systems

### Data Consistency
- Eventual consistency is the norm, not immediate
- Saga pattern required for distributed transactions
- Duplicate event handling is critical
- Ordering guarantees depend on Kafka configuration

### Cross-Domain Insights
- **Architecture + Performance:** Snapshot strategy directly impacts replay performance
- **Consistency + Architecture:** Saga pattern complexity increases with domain complexity
- **All domains:** Event sourcing shifts complexity from write to read path

## Recommendations

### For Order Management Systems

**1. Use Hybrid Approach (HIGH confidence)**
- Event sourcing for audit trail and history
- Traditional database for active order state
- Reconcile periodically

**Rationale:** Pure event sourcing introduces significant complexity for transactional operations that don't benefit from event replay. Industry case studies (Uber, Netflix) show hybrid approaches are more common.

**2. Implement CQRS from Day One (HIGH confidence)**
- Separate write and read models
- Materialized views for queries
- Event-driven read model updates

**Rationale:** Every source indicates read performance is unacceptable without CQRS. Planning for it from the start avoids major refactoring.

**3. Carefully Evaluate Schema Evolution (MEDIUM confidence)**
- Use schema registry (Confluent Schema Registry)
- Design events for backward compatibility
- Plan for versioning from the start

**Rationale:** Multiple sources cite schema evolution as a major challenge. Planning upfront prevents breaking changes.

## Sources

- High credibility: 12 sources (official docs, academic papers)
- Medium credibility: 18 sources (industry blogs, conference talks)
- Low credibility: 2 sources (personal blogs, forums)

Total: 32 sources consulted across 4 domains.
```

## Research Quality Assessment

- **Validation:** Triangulated across 30+ sources
- **Credibility:** 38% HIGH, 56% MEDIUM, 6% LOW
- **Cross-Domain:** 85% of findings validated across multiple domains
- **Consensus:** Strong consensus on core recommendations

## Usage Tips for Technical Research

1. **Be specific about concerns:** Mentioning "performance" and "consistency" ensured secondary domain coverage

2. **Include use case:** "Order management system" provided context for relevance assessment

3. **Ask for recommendation:** Framing as a question ("Should we use...?") encouraged actionable recommendations

4. **Technical terms:** Using specific terms ("Kafka", "microservices") improved domain detection accuracy
