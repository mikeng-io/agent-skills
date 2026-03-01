# Technical Domains

Reference list of technical domains for deep-* skill expert selection.

## Domains

### security
```yaml
name: security
trigger_signals:
  - auth
  - authentication
  - authorization
  - encryption
  - password
  - JWT
  - OAuth
  - OWASP
  - zero-trust
  - vulnerability
  - CVE
  - injection
  - XSS
  - CSRF
  - secrets
  - credentials
  - certificate
  - TLS
  - SSL
expert_role: "Security Auditor"
focus_areas:
  - Authentication and authorization flows
  - Input validation and injection prevention
  - Data encryption at rest and in transit
  - Secrets management
  - Zero-trust architecture patterns
  - Dependency vulnerability scanning
  - Session management
standards:
  - OWASP Top 10
  - CWE (Common Weakness Enumeration)
  - NIST Cybersecurity Framework
  - Zero-Trust Architecture (NIST SP 800-207)
```

### database
```yaml
name: database
trigger_signals:
  - schema
  - migration
  - query
  - SQL
  - index
  - transaction
  - ACID
  - ORM
  - database
  - table
  - foreign key
  - normalization
  - replication
  - sharding
  - connection pool
expert_role: "Database Architect"
focus_areas:
  - Schema design and normalization
  - Query optimization and indexing
  - Migration safety and rollback strategies
  - Transaction isolation levels
  - Connection pool management
  - Data consistency and integrity constraints
  - Read/write splitting patterns
standards:
  - ACID compliance
  - SQL standard (ISO/IEC 9075)
  - Database normalization (1NF through BCNF)
```

### api
```yaml
name: api
trigger_signals:
  - REST
  - GraphQL
  - gRPC
  - endpoint
  - API
  - route
  - contract
  - versioning
  - rate limit
  - pagination
  - webhook
  - OpenAPI
  - swagger
  - HTTP
expert_role: "API Design Specialist"
focus_areas:
  - REST/GraphQL/gRPC contract design
  - Versioning strategies
  - Rate limiting and throttling
  - Error response consistency
  - Pagination and cursor design
  - API documentation completeness
  - Backwards compatibility
standards:
  - OpenAPI 3.1 Specification
  - REST architectural constraints (Fielding)
  - HTTP semantics (RFC 9110)
  - GraphQL specification
```

### async-queue
```yaml
name: async-queue
trigger_signals:
  - queue
  - message
  - event
  - pub/sub
  - Kafka
  - RabbitMQ
  - SQS
  - idempotency
  - dead letter
  - backpressure
  - consumer
  - producer
  - stream
  - async
  - worker
expert_role: "Async Systems Specialist"
focus_areas:
  - Message idempotency guarantees
  - Dead letter queue handling
  - Backpressure management
  - Consumer group coordination
  - At-least-once vs exactly-once delivery
  - Event ordering and partitioning
  - Retry and circuit breaker patterns
standards:
  - Event-driven architecture patterns
  - Saga pattern
  - Outbox pattern
  - CQRS (Command Query Responsibility Segregation)
```

### performance
```yaml
name: performance
trigger_signals:
  - latency
  - throughput
  - bottleneck
  - profiling
  - memory
  - CPU
  - slow
  - optimization
  - cache
  - benchmark
  - load test
  - p99
  - SLA
  - response time
expert_role: "Performance Engineer"
focus_areas:
  - Algorithm complexity analysis (Big O)
  - Memory allocation and GC pressure
  - Caching strategy and invalidation
  - Database query performance
  - Network latency optimization
  - Profiling and bottleneck identification
  - Load testing and capacity planning
standards:
  - Core Web Vitals (LCP, FID/INP, CLS)
  - RAIL model
  - Google PageSpeed recommendations
```

### infrastructure
```yaml
name: infrastructure
trigger_signals:
  - Terraform
  - Kubernetes
  - k8s
  - Docker
  - CI/CD
  - pipeline
  - deployment
  - container
  - helm
  - cloud
  - AWS
  - GCP
  - Azure
  - IaC
  - infrastructure
expert_role: "Infrastructure Architect"
focus_areas:
  - Infrastructure as Code correctness
  - Container security and hardening
  - CI/CD pipeline reliability
  - Resource sizing and cost optimization
  - Disaster recovery and failover
  - Network policies and segmentation
  - Secrets management in deployment
standards:
  - CIS Benchmarks
  - Twelve-Factor App methodology
  - GitOps principles
  - DORA metrics
```

### cryptographic
```yaml
name: cryptographic
trigger_signals:
  - cryptography
  - hash
  - signature
  - proof
  - key management
  - PKI
  - merkle
  - blockchain
  - zero-knowledge
  - HMAC
  - AES
  - RSA
  - elliptic curve
  - entropy
expert_role: "Cryptography Specialist"
focus_areas:
  - Key management and rotation
  - Cryptographic proof verification
  - Hash chain integrity
  - Algorithm selection (avoiding deprecated algorithms)
  - Entropy and randomness quality
  - Side-channel attack resistance
  - Key derivation functions
standards:
  - NIST approved algorithms
  - FIPS 140-2/3
  - RFC 8018 (PKCS#5)
  - PKCS standards
```

### testing
```yaml
name: testing
trigger_signals:
  - test
  - coverage
  - unit test
  - integration test
  - e2e
  - mock
  - stub
  - assertion
  - fixture
  - property-based
  - TDD
  - BDD
  - flaky
  - regression
expert_role: "Test Architect"
focus_areas:
  - Test pyramid completeness (unit/integration/e2e balance)
  - Coverage meaningfulness (assertions that assert)
  - Test isolation and determinism
  - Mock and stub appropriateness
  - Property-based testing opportunities
  - Test data management
  - Flakiness root causes
standards:
  - Test pyramid (Mike Cohn)
  - Given/When/Then (BDD)
  - Property-based testing
  - Mutation testing
```

### accessibility
```yaml
name: accessibility
trigger_signals:
  - accessibility
  - WCAG
  - a11y
  - screen reader
  - ARIA
  - keyboard navigation
  - color contrast
  - focus
  - alt text
  - semantic HTML
  - disability
expert_role: "Accessibility Auditor"
focus_areas:
  - WCAG 2.2 compliance (Level A, AA, AAA)
  - ARIA roles and properties
  - Keyboard navigation completeness
  - Screen reader compatibility
  - Color contrast ratios
  - Focus management
  - Semantic HTML structure
standards:
  - WCAG 2.2
  - ARIA 1.2
  - Section 508
  - EN 301 549
```
