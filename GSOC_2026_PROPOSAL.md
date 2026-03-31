# GSoC 2026: AI-Powered Configuration Navigator

## Project Information

| Field | Value |
|-------|-------|
| **Project** | AI-Powered Configuration Navigator |
| **Organization** | Drupal |
| **Mentor** | Aditya Bathani (adityabathani.4478@gmail.com) |
| **Size** | 350 Hours |
| **Difficulty** | Intermediate |

## Proposal Link

https://www.drupal.org/project/gsoc/issues/3569913

---

## Abstract

Build an AI-powered assistant that helps Drupal site builders find configuration pages using natural language queries. The system will integrate with Drupal's existing AI module ecosystem (AI Core, AI Search, AI Assistants) rather than building from scratch.

---

## Architecture Overview

Based on mentor guidance:

```
┌─────────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  AI Search Block (extend existing)                              │
│  - Floating widget in admin pages                               │
│  - POST to /api/v1/knowledge-assistant/query                    │
│  - Stream response with source links                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DRUPAL AI LAYER                               │
├─────────────────────────────────────────────────────────────────┤
│  AI Assistants API (existing framework)                          │
│  AI Provider Interface (OpenAI, Anthropic, Ollama)               │
│  EmbeddingProviderInterface (pluggable)                          │
│    - Ollama (default for config metadata - privacy)              │
│    - OpenAI text-embedding-3-small (optional for content)         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    VECTOR DATABASE LAYER                         │
├─────────────────────────────────────────────────────────────────┤
│  VectorBackendInterface (pluggable)                              │
│    - upsert(id, vector, metadata)                                │
│    - query(vector, k, filters)                                   │
│    - delete(id)                                                  │
│  Implementations:                                                │
│    - SQLite VDB (default)                                        │
│    - pgvector (alternative)                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CONFIG INDEXER LAYER                          │
├─────────────────────────────────────────────────────────────────┤
│  ConfigMetadataIndexer service                                   │
│  - Crawl routes, menu links, permissions, help text              │
│  - Generate embeddings for config descriptions                    │
│  - Store in vector database                                      │
│  - Plugin API for contrib modules                                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Weekly Breakdown (12 Weeks / 350 Hours)

### Phase 1: Foundation & Architecture (Weeks 1-3)

#### Week 1: Project Setup & Research (25 hours)

**Goals:**
- Set up development environment
- Study existing AI module architecture
- Create project skeleton

**Tasks:**
1. Set up Drupal 11 development environment with DDEV
2. Install and configure AI module ecosystem:
   - AI Core 1.3.x
   - AI Search 2.0.x
   - AI VDB Provider SQLite
   - AI Provider Ollama (for local embeddings)
3. Study AI module source code:
   - AI Provider Interface architecture
   - AI Search embedding strategies
   - AI Assistants API framework
4. Create `ai_config_navigator` module scaffold
5. Document findings in module README

**Deliverables:**
- Working Drupal instance with AI modules
- Module scaffold with .info.yml, .services.yml
- Architecture documentation

**Resources:**
- https://www.drupal.org/project/ai
- https://www.drupal.org/project/ai_search

---

#### Week 2: Vector Backend Interface (30 hours)

**Goals:**
- Define VectorBackendInterface
- Implement SQLite VDB provider
- Create basic CRUD operations

**Tasks:**
1. Define `VectorBackendInterface`:
   ```php
   interface VectorBackendInterface {
     public function upsert(string $id, array $vector, array $metadata): void;
     public function query(array $vector, int $k, array $filters = []): array;
     public function delete(string $id): void;
     public function deleteMultiple(array $ids): void;
   }
   ```
2. Implement `SqliteVdbBackend` plugin:
   - Create SQLite database schema
   - Implement vector similarity search (cosine similarity)
   - Add metadata filtering support
3. Create plugin manager for vector backends
4. Write unit tests for interface
5. Add configuration form for VDB settings

**Deliverables:**
- `VectorBackendInterface` with full API
- Working SQLite implementation
- Unit tests passing
- Configuration UI

**Mentor Guidance:**
> "Use SQLite VDB by default, but from the start, wrap it behind a suitable VectorBackendInterface. Do not hardcode SQLite anywhere in the RAG pipeline."

---

#### Week 3: Embedding Provider Interface (30 hours)

**Goals:**
- Define EmbeddingProviderInterface
- Implement Ollama provider (default for privacy)
- Create OpenAI provider (optional for content)

**Tasks:**
1. Define `EmbeddingProviderInterface`:
   ```php
   interface EmbeddingProviderInterface {
     public function embed(string $text): array;
     public function embedMultiple(array $texts): array;
     public function getDimension(): int;
   }
   ```
2. Implement `OllamaEmbeddingProvider`:
   - Connect to local Ollama instance
   - Use nomic-embed-text or similar model
   - Handle connection errors gracefully
3. Implement `OpenAiEmbeddingProvider`:
   - Use text-embedding-3-small model
   - Add opt-in configuration
4. Create provider plugin manager
5. Write functional tests

**Deliverables:**
- `EmbeddingProviderInterface` with full API
- Ollama provider (local, privacy-first)
- OpenAI provider (opt-in for content)
- Configuration UI with privacy warnings

**Mentor Guidance:**
> "Config metadata reveals site architecture and should never leave the server. Set Ollama as default for config/schema indexing. Allow API-based providers only for content nodes where admin opts in."

---

### Phase 2: Config Metadata Indexer (Weeks 4-6)

#### Week 4: Route & Menu Crawler (30 hours)

**Goals:**
- Crawl Drupal routes for admin pages
- Extract menu links with hierarchy
- Capture permission requirements

**Tasks:**
1. Create `ConfigMetadataIndexer` service:
   ```php
   class ConfigMetadataIndexer {
     public function indexRoutes(): array;
     public function indexMenuLinks(): array;
     public function indexPermissions(): array;
     public function indexHelpText(): array;
   }
   ```
2. Implement route crawler:
   - Use `\Drupal::service('router.route_provider')`
   - Filter for admin routes (`/admin/*`)
   - Extract route defaults (title, description)
3. Implement menu link crawler:
   - Use `\Drupal::service('plugin.manager.menu.link')`
   - Build hierarchy tree
   - Extract parent-child relationships
4. Implement permission crawler:
   - Use `\Drupal::service('user.permissions')`
   - Map routes to required permissions
5. Create config metadata entity type for storage

**Deliverables:**
- Route crawler extracting all admin routes
- Menu link hierarchy captured
- Permission mappings documented
- Custom entity for config metadata

**Resources:**
- https://www.drupal.org/docs/drupal-apis/routing-system
- https://api.drupal.org/api/drupal/core!modules!system!system.module/function/system_menu_block/11.x

---

#### Week 5: Help Text & Description Extraction (25 hours)

**Goals:**
- Extract help text from Drupal core
- Capture module-provided descriptions
- Build rich metadata records

**Tasks:**
1. Implement help text crawler:
   - Use `hook_help()` implementations
   - Parse `.admin.inc` files for descriptions
   - Extract form descriptions
2. Enhance metadata records:
   ```php
   class ConfigMetadataRecord {
     public string $id;           // Route name
     public string $path;         // /admin/config/...
     public string $title;
     public string $description;
     public string $help_text;
     public string $module;
     public array $permissions;
     public array $keywords;
     public array $synonyms;
     public ?string $parent_menu;
   }
   ```
3. Generate keywords/synonyms:
   - Extract from title and description
   - Add Drupal-specific terminology
   - Support manual overrides via config
4. Create batch processing for large sites
5. Write kernel tests

**Deliverables:**
- Help text extraction for core modules
- Rich metadata records with all fields
- Batch processing for indexing
- Kernel tests passing

---

#### Week 6: Embedding Generation & Storage (30 hours)

**Goals:**
- Generate embeddings for all config metadata
- Store in vector database
- Implement incremental updates

**Tasks:**
1. Create `ConfigEmbeddingGenerator` service:
   - Combine title + description + help_text + keywords
   - Use configured embedding provider
   - Handle rate limiting
2. Implement embedding storage:
   - Use VectorBackendInterface
   - Store metadata alongside vectors
   - Add module name as filterable field
3. Create indexing commands:
   - Drush command: `drush ai-config-index`
   - Admin UI for reindexing
4. Implement incremental updates:
   - Hook into module enable/disable
   - Hook into configuration save
   - Queue workers for background processing
5. Add indexing status UI

**Deliverables:**
- Embedding generation pipeline
- Vector storage implementation
- Drush commands for indexing
- Incremental update hooks
- Admin UI for status

---

### Phase 3: RAG Pipeline & Query Processing (Weeks 7-9)

#### Week 7: Query Processing & Retrieval (30 hours)

**Goals:**
- Implement query embedding
- Build retrieval pipeline
- Add permission filtering

**Tasks:**
1. Create `ConfigQueryProcessor` service:
   ```php
   class ConfigQueryProcessor {
     public function process(string $query, AccountInterface $user): array;
     public function retrieveCandidates(string $query, int $k = 5): array;
     public function filterByPermissions(array $results, AccountInterface $user): array;
   }
   ```
2. Implement query embedding:
   - Use same embedding provider as indexer
   - Add query preprocessing (lowercase, etc.)
3. Implement similarity search:
   - Query vector database
   - Return top-k candidates
   - Include similarity scores
4. Implement permission filtering:
   - Check user permissions against metadata
   - Filter out inaccessible routes
   - Log filtered results for analytics
5. Add query logging for feedback

**Deliverables:**
- Query processor service
- Permission-aware retrieval
- Query logging system
- Functional tests

---

#### Week 8: RAG Pipeline Integration (30 hours)

**Goals:**
- Integrate with AI Assistants API
- Build prompt templates
- Create context builder

**Tasks:**
1. Create `ConfigRagTool` extending AI Search RagTool:
   - Inject config metadata index
   - Override retrieval logic
   - Add admin-specific filters
2. Build prompt template:
   ```
   You are a Drupal configuration navigator assistant.
   
   Available configuration pages:
   {candidates}
   
   User question: {query}
   
   Respond with:
   - Best matching page with path
   - Brief explanation of why it matches
   - Alternative pages if relevant
   - Never invent paths not in the list
   ```
3. Implement context builder:
   - Format candidates for LLM context
   - Include paths as clickable links
   - Add permission warnings if needed
4. Integrate with AI provider abstraction:
   - Support OpenAI, Anthropic, Ollama
   - Handle streaming responses
5. Write integration tests

**Deliverables:**
- RAG tool for AI Assistants
- Prompt templates optimized for config nav
- Context builder with proper formatting
- Integration tests

**Resources:**
- AI Search module RagTool implementation

---

#### Week 9: REST API & Streaming (25 hours)

**Goals:**
- Create REST endpoint for queries
- Implement streaming responses
- Add conversation history

**Tasks:**
1. Create REST resource:
   ```php
   /**
    * @REST\GET("/api/v1/knowledge-assistant/query")
    */
   class ConfigNavigatorResource {
     public function get(Request $request): Response;
     public function post(Request $request): Response;
   }
   ```
2. Implement streaming:
   - Use Server-Sent Events (SSE)
   - Stream tokens from LLM
   - Include metadata (sources, scores)
3. Add conversation history:
   - Store in user session or database
   - Include previous context in queries
   - Support follow-up questions
4. Implement rate limiting:
   - Per-user query limits
   - Cache common queries
5. Add CSRF protection

**Deliverables:**
- REST API endpoint
- SSE streaming implementation
- Conversation history storage
- Rate limiting
- API documentation

**Mentor Guidance:**
> "Keep the frontend simple: input -> POST -> stream response -> render with source links."

---

### Phase 4: User Interface (Weeks 10-11)

#### Week 10: Admin Block Widget (30 hours)

**Goals:**
- Extend AI Search block
- Create floating widget for admin pages
- Implement keyboard navigation

**Tasks:**
1. Create block plugin:
   ```php
   /**
    * @Block(
    *   id = "ai_config_navigator_widget",
    *   admin_label = @Translation("AI Config Navigator"),
    * )
    */
   class ConfigNavigatorBlock extends BlockBase {
     public function build(): array;
   }
   ```
2. Implement JavaScript widget:
   - Vanilla JS or minimal library
   - Floating button in bottom-right
   - Expandable chat interface
   - Keyboard shortcuts (Alt+K like Coffee module)
3. Build chat UI:
   - Input field
   - Message bubbles
   - Candidate cards with paths
   - Click-to-navigate functionality
4. Add visual highlighting:
   - Highlight target config page when navigated
   - Show breadcrumb trail
   - Indicate current location
5. Implement accessibility:
   - ARIA labels
   - Screen reader support
   - Keyboard navigation

**Deliverables:**
- Block plugin with configuration
- JavaScript widget with chat UI
- Keyboard shortcuts
- Visual highlighting
- Accessibility compliance

**Mentor Guidance:**
> "Don't start from scratch, don't fork DeepChat, expand the block of the current AI Search module. A Drupal block plugin that renders a thin JS layer should be the widget."

**Reference:**
- Coffee module keyboard shortcuts (Alt+D)
- Admin Toolbar dropdown UI

---

#### Week 11: User Feedback & Learning (20 hours)

**Goals:**
- Implement feedback collection
- Add analytics for query success
- Create admin dashboard

**Tasks:**
1. Implement feedback mechanism:
   - Thumbs up/down on responses
   - Report incorrect navigation
   - Suggest better matches
2. Create analytics storage:
   - Track query success rate
   - Measure time-to-navigation
   - Identify failed queries
3. Build admin dashboard:
   - Query analytics visualization
   - Top queries list
   - Failed queries report
   - Feedback summary
4. Implement improvement loop:
   - Use feedback to adjust scores
   - Manual override for common queries
   - A/B test prompt variations
5. Export functionality for analysis

**Deliverables:**
- Feedback UI components
- Analytics database schema
- Admin dashboard with charts
- Feedback processing queue

---

### Phase 5: Polish & Documentation (Week 12)

#### Week 12: Testing, Documentation & Deployment (25 hours)

**Goals:**
- Complete test coverage
- Write documentation
- Prepare for deployment

**Tasks:**
1. Complete test suite:
   - Unit tests (90%+ coverage)
   - Kernel tests for integration
   - Functional tests for UI
   - Performance tests for large indexes
2. Write documentation:
   - User guide for site builders
   - Developer API documentation
   - Administrator configuration guide
   - Contrib module integration guide
3. Create example configurations:
   - Default config for common setups
   - Privacy-first config (Ollama only)
   - Enterprise config (pgvector, OpenAI)
4. Security review:
   - Permission checks
   - Input sanitization
   - Rate limiting verification
   - CSRF protection
5. Prepare release:
   - Create release notes
   - Tag alpha release
   - Set up issue queue categories

**Deliverables:**
- Complete test suite passing
- User and developer documentation
- Example configurations
- Security review checklist
- Alpha release tag

---

## Deliverables Summary

| Phase | Weeks | Key Deliverables |
|-------|-------|------------------|
| Foundation | 1-3 | VectorBackendInterface, EmbeddingProviderInterface, SQLite VDB, Ollama provider |
| Indexer | 4-6 | ConfigMetadataIndexer, route/menu crawler, help text extraction, embedding pipeline |
| RAG Pipeline | 7-9 | Query processor, RAG tool, REST API, streaming, conversation history |
| UI | 10-11 | Admin block widget, floating chat UI, keyboard shortcuts, feedback system |
| Polish | 12 | Tests, documentation, security review, alpha release |

---

## Technical Decisions (Based on Mentor Guidance)

### 1. Vector Store Backend

**Decision:** SQLite VDB as default, pgvector as alternative

**Rationale from mentor:**
> "Use SQLite VDB by default, but wrap it behind VectorBackendInterface. The interface should have upsert, query, delete; do not hardcode SQLite anywhere in the RAG pipeline."

### 2. Chat UI

**Decision:** Extend AI Search block, thin JS layer, vanilla JS

**Rationale from mentor:**
> "Don't start from scratch, don't fork DeepChat. Expand the block of the current AI Search module. A Drupal block plugin that renders a thin JS layer should be the widget. POSTing to the new REST endpoint."

### 3. Privacy & Local Models

**Decision:** Ollama as default for config metadata, OpenAI opt-in for content

**Rationale from mentor:**
> "Config metadata clearly reveals site architecture and should never leave the server. Allow API-based providers only for content nodes where the site admin has specifically opted in. This division - local for structure, optional remote for content - is a compelling GSoC narrative."

---

## Existing Module Integration

### AI Core
- Use AI Provider Interface for LLM calls
- Leverage existing provider ecosystem (OpenAI, Anthropic, Ollama)
- Benefit from provider abstraction layer

### AI Search
- Extend RagTool for retrieval
- Use embedding strategies for chunking
- Integrate with Search API backend

### AI VDB Providers
- Implement VectorBackendInterface
- Reuse SQLite provider as reference
- Support Milvus, Pinecone, pgvector

### Admin Toolbar / Coffee
- Inspiration for keyboard navigation
- UI patterns for admin interface
- Dropdown menu integration

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| LLM hallucination | Strict prompt constraints, only use indexed paths |
| Permission bypass | Server-side permission checks, filter before display |
| Slow queries | Cache embeddings, optimize vector search, add query limits |
| Large indexes | Batch processing, queue workers, incremental updates |
| Privacy leak | Local embeddings for config, opt-in for external APIs |

---

## Success Metrics

1. **Accuracy:** 90%+ correct navigation on test queries
2. **Speed:** <2 second response time for typical queries
3. **Privacy:** Zero config metadata sent to external APIs by default
4. **Usability:** Keyboard navigation working, accessibility compliant
5. **Coverage:** 100% of core admin routes indexed

---

## References

- Project Proposal: https://www.drupal.org/project/gsoc/issues/3569913
- AI Module: https://www.drupal.org/project/ai
- AI Search: https://www.drupal.org/project/ai_search
- Routing System: https://www.drupal.org/docs/drupal-apis/routing-system
- Configuration Management: https://www.drupal.org/docs/configuration-management
- Admin Toolbar: https://www.drupal.org/project/admin_toolbar
- Coffee Module: https://www.drupal.org/project/coffee

---

## Proof of Concept

- **Live Demo:** https://config-nav-cyan-grass.reflex.run/
- **GitHub:** https://github.com/error9098x/drupal-ai-config-navigator
- **Screenshots:** See GitHub repository

The PoC demonstrates the core interaction model using:
- Reflex (Python full-stack)
- Groq (LLM inference)
- rapidfuzz (fuzzy matching)
- 100 Drupal admin config pages indexed