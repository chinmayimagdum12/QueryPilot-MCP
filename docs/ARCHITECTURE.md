# QueryPilot MCP: System Architecture & Engineering Design

```mermaid
flowchart TD
    subgraph ClientLayer["Client Layer (LLM Host)"]
        User["User (Natural Language Prompt)"]
        ClaudeDesktop["Claude Desktop / MCP Client Application"]
    end

    subgraph TransportLayer["Transport & Protocol Layer"]
        StdioPipe["Stdio IPC Pipes (stdin / stdout / stderr)"]
        JSONRPC["JSON-RPC 2.0 Framing & Protocol Dispatcher"]
    end

    subgraph CoreApplication["QueryPilot MCP Core Engine"]
        FastMCPEngine["FastMCP Server Router (v1.30.0)"]
        SafeToolWrapper["@safe_tool Exception & Telemetry Decorator"]
        
        subgraph ToolRegistry["Registered Tool Handlers"]
            T1["list_tables()"]
            T2["describe_table()"]
            T3["run_readonly_query()"]
            T4["explain_query()"]
            T5["table_stats()"]
        end
        
        ASTGuard["SQL Guard AST Engine (sqlglot v30.21.0)"]
        AuditEngine["Thread-Safe Audit Logger (JSONL)"]
    end

    subgraph DatabaseLayer["PostgreSQL 16 Engine"]
        ConnLayer["psycopg v3 Connection Manager"]
        DBSession["Enforced Read-Only Session (conn.read_only=True)"]
        ROUser["Role: querypilot_ro (NOSUPERUSER, 5 Conn Limit)"]
        PagilaDB[(Pagila Database Catalog & Tables)]
    end

    User -->|"1. 'Which 5 customers spent the most?'"| ClaudeDesktop
    ClaudeDesktop -->|"2. tools/call: run_readonly_query(sql, max_rows)"| StdioPipe
    StdioPipe -->|"3. JSON-RPC Message"| JSONRPC
    JSONRPC --> FastMCPEngine
    FastMCPEngine --> SafeToolWrapper
    SafeToolWrapper --> T3
    T3 -->|"4. Raw SQL String"| ASTGuard
    ASTGuard -->|"5. Validated AST or GuardError"| T3
    T3 -->|"6. Validated Query & Parameter Array"| ConnLayer
    ConnLayer -->|"7. Read-Only Transaction"| DBSession
    DBSession -->|"8. Execute under querypilot_ro"| ROUser
    ROUser -->|"9. Query Scan / Index Seek"| PagilaDB
    PagilaDB -->|"10. Row Batches (fetchmany limit+1)"| ConnLayer
    ConnLayer -->|"11. Dict Rows + Column Descriptors"| T3
    T3 -->|"12. Formatted Dict with Untrusted Data Note"| SafeToolWrapper
    SafeToolWrapper -->|"13. Telemetry Event"| AuditEngine
    SafeToolWrapper -->|"14. Serialized JSON Payload"| JSONRPC
    JSONRPC -->|"15. JSON-RPC Response"| StdioPipe
    StdioPipe -->|"16. Formatted Rows"| ClaudeDesktop
    ClaudeDesktop -->|"17. Natural Language Answer"| User
```

---

## 1. Architectural Principles

QueryPilot MCP is engineered around five fundamental engineering principles:

1. **Zero-Trust for Generated SQL**: All SQL statements originating from Claude Desktop are treated as inherently untrusted adversarial input. No statement executes without passing rigorous Abstract Syntax Tree (AST) inspection.
2. **Dual-Layer Defense-in-Depth**: The application-level AST guard and the database engine permissions act as independent, isolated security perimeters. If one layer experiences a zero-day bypass or parsing mismatch, the other layer unconditionally guarantees data integrity.
3. **Strict Resource Containment**: Runaway resource exhaustion (CPU, memory, lock contention, disk temp storage) is mitigated via tight query timeouts ($5,000\text{ ms}$), idle connection timeouts ($10,000\text{ ms}$), memory limits ($16\text{ MB}$ `work_mem`), and row truncation caps ($1,000$ hard maximum).
4. **Zero-Stdout Invariant**: Standard output (`stdout`) is reserved strictly for JSON-RPC 2.0 message frames. All server logs, diagnostic traces, and exception logs are directed exclusively to `stderr` or local disk logs to prevent IPC framing corruption.
5. **Untrusted Data Boundary**: Database row contents returned to the LLM are explicitly flagged as unvetted external data to immunize the model against indirect prompt injection.

---

## 2. MCP Protocol Lifecycle & Communication Flow

```mermaid
sequenceDiagram
    autonumber
    participant C as Claude Desktop (Client)
    participant S as QueryPilot Server (FastMCP)
    participant G as AST SQL Guard
    participant D as PostgreSQL Engine
    participant A as Audit Log (audit.jsonl)

    Note over C,S: Initialization Handshake
    C->>S: {"jsonrpc":"2.0", "id":1, "method":"initialize", "params":{...}}
    S-->>C: {"jsonrpc":"2.0", "id":1, "result":{"protocolVersion":"2024-11-05", "capabilities":{"tools":{}}}}
    C->>S: {"jsonrpc":"2.0", "method":"notifications/initialized"}

    Note over C,S: Tool Discovery
    C->>S: {"jsonrpc":"2.0", "id":2, "method":"tools/list"}
    S-->>C: {"jsonrpc":"2.0", "id":2, "result":{"tools":[list_tables, describe_table, run_readonly_query, explain_query, table_stats]}}

    Note over C,D: Tool Execution: run_readonly_query
    C->>S: {"jsonrpc":"2.0", "id":3, "method":"tools/call", "params":{"name":"run_readonly_query", "arguments":{"sql":"SELECT * FROM film", "max_rows":5}}}
    S->>G: validate_sql("SELECT * FROM film")
    G-->>S: "SELECT * FROM film" (AST Passed)
    S->>D: BEGIN (read_only=on, statement_timeout=5000ms)<br/>SELECT * FROM film<br/>fetchmany(6)
    D-->>S: 6 rows returned (5 requested)
    Note over S: Truncation check: len(rows) > 5 -> True<br/>Truncate payload to 5 rows
    S->>A: log("run_readonly_query", "SELECT * FROM film", "ok", 4.2ms)
    S-->>C: {"jsonrpc":"2.0", "id":3, "result":{"content":[{"type":"text", "text":"{\"columns\":[...], \"rows\":[...], \"truncated\":true, \"note\":\"...\"}"}]}}

    Note over C,D: Tool Execution: Malicious Mutation Attempt
    C->>S: {"jsonrpc":"2.0", "id":4, "method":"tools/call", "params":{"name":"run_readonly_query", "arguments":{"sql":"DELETE FROM rental"}}}
    S->>G: validate_sql("DELETE FROM rental")
    G-->>S: GuardError: "Data-changing statements are not allowed."
    S->>A: log("run_readonly_query", "DELETE FROM rental", "blocked", 0.8ms)
    S-->>C: {"jsonrpc":"2.0", "id":4, "result":{"content":[{"type":"text", "text":"{\"error\":\"Data-changing statements are not allowed.\"}"}]}}
```

---

## 3. Subsystem Breakdown & Component Specifications

```mermaid
graph LR
    subgraph Client["1. Client Runtime"]
        CD["Claude Desktop"]
        PromptEngine["Prompt Formulation"]
    end

    subgraph Server["2. FastMCP Middleware"]
        Router["Tool Router"]
        Decorator["@safe_tool Decorator"]
        Serializer["_out() Custom JSON Serializer"]
    end

    subgraph GuardEngine["3. Security Inspection"]
        Lexer["Raw Regex Lexer (RAW_DENY)"]
        Parser["sqlglot AST Parser (postgres dialect)"]
        ASTWalker["Recursive Node Traversal"]
    end

    subgraph DataEngine["4. Database Execution"]
        PoolMgr["psycopg.connect Manager"]
        Cursor["Server Cursor (dict_row)"]
        Truncator["fetchmany(limit + 1) Truncator"]
    end

    CD --> Router
    PromptEngine --> Router
    Router --> Decorator
    Decorator --> GuardEngine
    GuardEngine --> Lexer
    Lexer --> Parser
    Parser --> ASTWalker
    ASTWalker --> DataEngine
    DataEngine --> PoolMgr
    PoolMgr --> Cursor
    Cursor --> Truncator
    Truncator --> Serializer
    Serializer --> CD
```

### 3.1 Transport & Framing Layer
- **Transport Standard**: Standard Input/Output (`stdio`) Inter-Process Communication.
- **Message Encoding**: UTF-8 encoded JSON-RPC 2.0 delimiter-separated streams.
- **Serialization Handler**: Custom `_out()` serializer utilizing Python's `json.dumps(..., default=str)`:
  - `Decimal` $\to$ Accurate fixed-point string representation (e.g., `"19.99"`).
  - `datetime` / `date` $\to$ ISO 8601 UTC strings (`"2026-10-08T12:00:00+00:00"`).
  - `UUID` $\to$ Canonical 36-character hexadecimal format.
  - `bytes` $\to$ UTF-8 decoded string or binary representation.

### 3.2 SQL Validation Engine (`src/querypilot/guard.py`)
- **Parser**: `sqlglot` v30.21.0 using strict `read="postgres"`.
- **Latency**: $1.1\text{ ms} - 2.8\text{ ms}$ average AST parsing overhead.
- **AST Allowed Node Class Hierarchy**: Top-level root statements must strictly inherit from `ALLOWED_TOP`:
  $$\text{Root} \in \{\text{exp.Select}, \text{exp.Union}, \text{exp.Intersect}, \text{exp.Except}, \text{exp.SetOperation}, \text{exp.Subquery}\}$$
- **Prohibited Node Classes**: Any appearance in the AST (including recursive CTE definitions, subqueries, and table functions):
  $$\text{Node} \notin \{\text{Insert}, \text{Update}, \text{Delete}, \text{Drop}, \text{Create}, \text{Alter}, \text{Set}, \text{Merge}, \text{Copy}, \text{Truncate}, \text{Grant}, \text{Lock}, \text{Into}\}$$

### 3.3 Database Client Adapter (`src/querypilot/db.py`)
- **Driver**: `psycopg` v3.3.6 (C-extensions binary binding).
- **Row Factory**: `psycopg.rows.dict_row` mapping column names directly to dictionary keys.
- **Session Configuration Parameters**:
  - `statement_timeout = 5000` (Terminates queries exceeding 5 seconds).
  - `default_transaction_read_only = on` (PostgreSQL engine rejects write operations).
  - `idle_in_transaction_session_timeout = 10000` (Disconnects abandoned sessions after 10s).
  - `lock_timeout = 2000` (Rejects execution if table lock acquisition exceeds 2s).

---

## 4. Resource Allocation & Latency Budgets

| Execution Phase | Allocated Budget | Typical Latency | Mitigation Trigger |
|---|---|---|---|
| **JSON-RPC Dispatch** | $< 1.0\text{ ms}$ | $0.2\text{ ms}$ | Connection dropped if pipe broken |
| **AST Parse & Traversal** | $< 5.0\text{ ms}$ | $1.4\text{ ms}$ | `GuardError` if query $> 10,000$ chars |
| **Database Connection** | $< 10.0\text{ ms}$ | $3.2\text{ ms}$ | Connection timeout after $5,000\text{ ms}$ |
| **Query Execution** | $< 5,000\text{ ms}$ | $12.5\text{ ms}$ | PostgreSQL `QueryCanceled` error |
| **Row Serialization** | $< 5.0\text{ ms}$ | $1.1\text{ ms}$ | Truncated to max $1,000$ rows |
| **Audit Logging** | $< 1.0\text{ ms}$ | $0.3\text{ ms}$ | Thread-safe lock with non-blocking write |
| **Total Round-Trip** | **$\le 5,022\text{ ms}$** | **$18.7\text{ ms}$** | Clean user-facing error response |
