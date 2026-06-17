#!/usr/bin/env python3
"""One-off helper: apply Phase 1 description updates. Not part of CI."""

from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "skills"

DESCRIPTIONS: dict[str, str] = {
    "accessibility-wcag": (
        "Applies WCAG 2.2 AA-aligned accessibility checks to interfaces, forms, "
        "dashboards and components. Use when building or reviewing any user-facing "
        "UI, content, or agent supervision screen."
    ),
    "agentic-ux-patterns": (
        "Designs interfaces for supervising, approving, steering and auditing AI "
        "agent actions with evidence and uncertainty surfaced. Use when building "
        "agent workflows, approval gates, or audit surfaces."
    ),
    "apply-laws-of-ai": (
        "Mandatory immutable baseline applying an Asimov-inspired hierarchy of AI "
        "safety laws. Use when at every session start and before any other skill, "
        "plan, routing decision, tool use, or material edit. Also known as "
        "apply_laws_of_AI."
    ),
    "bdd-practice": (
        "Applies behaviour-driven development with business-readable scenarios "
        "linked to executable acceptance tests. Use when defining externally "
        "visible behaviour, acceptance criteria, or user-facing workflows before "
        "implementation."
    ),
    "business-capability-modelling": (
        "Models stable business capabilities, levels, ownership, maturity and "
        "heatmaps. Use when mapping organisational abilities, decomposing strategy, "
        "or assigning capability ownership."
    ),
    "business-information-concept-modelling": (
        "Derives business concepts and relationships from capabilities, value "
        "streams and processes. Use when linking business architecture artefacts "
        "to information concepts for data modelling."
    ),
    "capability-maturity-assessment": (
        "Assesses current and target maturity, gaps, risks and roadmap priorities. "
        "Use when prioritising capability improvement or planning architecture "
        "roadmaps."
    ),
    "cdc-and-source-to-stream-ingestion": (
        "Designs CDC and streaming ingestion from operational sources to event "
        "streams. Use when capturing database changes, replicating operational data, "
        "or building source-to-stream pipelines."
    ),
    "conceptual-data-modelling": (
        "Identifies business concepts, entities and relationships without premature "
        "physical design. Use when starting data architecture or aligning business "
        "language with information models."
    ),
    "data-contract-design": (
        "Defines producer-consumer contracts for schema, semantics, quality, "
        "compatibility and operations. Use when formalising API, event, or dataset "
        "agreements between teams."
    ),
    "data-governance-and-quality": (
        "Defines ownership, policies, quality rules, controls, monitoring and "
        "remediation. Use when establishing data governance, quality SLAs, or "
        "remediation workflows."
    ),
    "data-integration-and-interoperability": (
        "Designs batch, API, event, CDC, semantic and file-based integration "
        "patterns. Use when connecting systems, choosing integration styles, or "
        "resolving interoperability gaps."
    ),
    "data-lifecycle-and-retention-management": (
        "Designs lifecycle, retention, archival, deletion, legal hold and disposal "
        "controls. Use when defining data retention policies, archival strategy, or "
        "compliant deletion."
    ),
    "data-lineage-and-provenance": (
        "Tracks source-to-target lineage, transformation history, evidence, "
        "ownership and provenance. Use when documenting data flows, audit trails, or "
        "impact analysis for changes."
    ),
    "data-product-dashboard-design": (
        "Designs actionable data product dashboards for quality, lineage, "
        "validation, quarantine and operations. Use when building data-ops, quality, "
        "or lineage dashboards."
    ),
    "data-product-design": (
        "Designs governed, domain-owned, discoverable and reusable data products. "
        "Use when packaging datasets as products, defining ownership, or reviewing "
        "product readiness."
    ),
    "data-security-and-privacy-architecture": (
        "Designs classification, access, masking, privacy, entitlement and "
        "sensitive-data controls. Use when securing shared data, defining privacy "
        "controls, or classifying datasets."
    ),
    "ddd-practice": (
        "Applies domain-driven design with bounded contexts, aggregates, and "
        "ubiquitous language. Use when modelling complex business domains, defining "
        "boundaries, or protecting invariants."
    ),
    "design-system-practice": (
        "Maintains consistent, accessible design systems using tokens, components "
        "and documented patterns. Use when creating or evolving a shared UI "
        "component library or design tokens."
    ),
    "dora-four-keys": (
        "Uses DevOps Research and Assessment Four Keys to improve delivery "
        "performance without gaming metrics. Use when measuring deployment frequency, "
        "lead time, change failure rate, or recovery time."
    ),
    "dry-principle": (
        "Applies DRY to remove harmful duplication while avoiding misleading "
        "abstraction. Use when refactoring repeated knowledge, schemas, validation "
        "rules, or agent instructions."
    ),
    "event-driven-architecture": (
        "Designs event-driven systems with asynchronous flows, brokers, producers, "
        "consumers and contracts. Use when architecting asynchronous, decoupled, or "
        "event-first systems."
    ),
    "event-governance-and-lineage": (
        "Governs event ownership, classification, metadata, lineage, quality and "
        "lifecycle. Use when governing shared event catalogues, schemas, or stream "
        "ownership."
    ),
    "event-modelling": (
        "Discovers and models business events, commands, decisions and state "
        "changes. Use when event-storming, designing event timelines, or defining "
        "domain events."
    ),
    "event-streaming-platform-design": (
        "Designs shared streaming platforms, topics, partitions, tenancy, retention "
        "and replay. Use when selecting or designing Kafka, Pulsar, or Event Hubs-"
        "style platforms."
    ),
    "frontend-state-and-interaction-design": (
        "Designs predictable states for loading, empty, error, partial, long-running "
        "and approval workflows. Use when implementing async UI, agent tasks, or "
        "multi-step forms."
    ),
    "incident-response-and-postmortems": (
        "Handles incidents, recovery, postmortems and corrective actions with "
        "blameless, evidence-led practice. Use when responding to outages, writing "
        "postmortems, or defining incident runbooks."
    ),
    "kg-enabled-rag": (
        "Builds, refactors and hardens Neo4j-native KG-enabled RAG with LangGraph, "
        "hybrid retrieval, text-to-Cypher, and provenance. Use when implementing "
        "GraphRAG, graph-backed retrieval, or guarded text-to-Cypher pipelines."
    ),
    "kiss-principle": (
        "Applies KISS to simplify code, architecture, workflows and agent designs "
        "without losing required behaviour. Use when reducing over-engineering, "
        "speculative abstractions, or unnecessary agent complexity."
    ),
    "lakehouse-and-medallion-architecture": (
        "Designs raw, quarantine, cleansed, refined and serving lakehouse layers. "
        "Use when structuring medallion pipelines, lakehouse zones, or batch and "
        "stream serving layers."
    ),
    "logical-data-modelling": (
        "Defines logical entities, attributes, identifiers, relationships and "
        "constraints. Use when translating conceptual models to logical schemas or "
        "normalising entity designs."
    ),
    "master-and-reference-data-management": (
        "Designs master data, reference data, identifiers, hierarchies, survivorship "
        "and stewardship. Use when defining golden records, controlled "
        "vocabularies, or MDM patterns."
    ),
    "metadata-management": (
        "Designs metadata for discoverability, governance, quality, lineage and "
        "operations. Use when building catalogues, data discovery, or operational "
        "metadata standards."
    ),
    "observability-and-telemetry": (
        "Designs actionable logs, metrics, traces, dashboards and alerts for "
        "reliable operations. Use when instrumenting services, defining SLIs, or "
        "improving on-call signal quality."
    ),
    "ontology-and-knowledge-graph-modelling": (
        "Designs ontology-driven knowledge graphs for explainable KG-RAG. Use when "
        "modelling semantic graphs, ontologies, or graph schemas for retrieval."
    ),
    "operating-model-design": (
        "Designs how people, process, technology, data, governance and delivery "
        "align. Use when defining operating models, ways of working, or organisation-"
        "to-technology alignment."
    ),
    "organisation-and-role-design": (
        "Defines roles, decision rights, accountabilities, team boundaries and "
        "ownership. Use when designing teams, RACI matrices, or architecture "
        "governance roles."
    ),
    "process-modelling": (
        "Models operational steps, decisions, hand-offs, controls, exceptions and "
        "automation opportunities. Use when documenting processes, BPMN workflows, or "
        "automation candidates."
    ),
    "real-time-operability": (
        "Designs operational controls for streaming: lag, freshness, replay, back-"
        "pressure and SLOs. Use when operating Kafka or streaming platforms or "
        "defining stream SLOs."
    ),
    "release-engineering-and-progressive-delivery": (
        "Improves deployment safety with canary, blue/green, feature flags and "
        "rollback. Use when designing release strategies, progressive delivery, or "
        "deployment gates."
    ),
    "schema-registry-and-contracts": (
        "Defines event schemas, compatibility, versioning and producer-consumer "
        "obligations. Use when governing Avro, JSON, or Protobuf schemas and registry "
        "compatibility policies."
    ),
    "slo-error-budget-management": (
        "Defines SLIs, SLOs, error budgets, burn rates and release gates. Use when "
        "setting reliability targets, error budgets, or release gating policies."
    ),
    "solid-principles": (
        "Applies SOLID for modularity, dependency boundaries and testability without "
        "over-engineering. Use when refactoring modules, services, agents, or "
        "dependency boundaries."
    ),
    "sre-practice": (
        "Applies SRE practices for reliability, operability and resilience "
        "objectives. Use when owning production services, defining SLOs, or "
        "improving operational maturity."
    ),
    "strategy-to-execution-traceability": (
        "Traces objectives to outcomes, capabilities, initiatives, metrics and "
        "evidence. Use when linking strategy to delivery, KPIs, or architecture "
        "roadmaps."
    ),
    "stream-processing-patterns": (
        "Designs stream filtering, enrichment, joins, windows and stateful "
        "processing. Use when implementing Flink, Spark Streaming, or kstreams-style "
        "processing logic."
    ),
    "tdd-practice": (
        "Applies TDD: failing test first, smallest passing change, refactor under "
        "test protection. Use when adding behaviour, fixing defects, or refactoring "
        "with executable expectations."
    ),
    "toil-reduction-and-automation": (
        "Reduces repetitive operational work through safe, tested, observable "
        "automation. Use when identifying toil, automating runbooks, or improving "
        "operator efficiency."
    ),
    "ui-component-design": (
        "Designs reusable, accessible UI components with clear props, states, "
        "variants and tests. Use when building tables, forms, modals, cards, or "
        "design-system components."
    ),
    "user-research-and-usability-testing": (
        "Plans lightweight research and usability testing for workflows and "
        "dashboards. Use when validating UX assumptions, forms, or agent approval "
        "flows with users."
    ),
    "ux-design-principles": (
        "Applies UX principles for clear, task-centred journeys, navigation and "
        "forms. Use when designing new screens, workflows, information architecture, "
        "or user journeys."
    ),
    "value-stream-modelling": (
        "Models value from trigger to outcome across stakeholders, capabilities and "
        "systems. Use when mapping end-to-end value flow or identifying waste and "
        "bottlenecks."
    ),
}


def update_description(path: Path, new_desc: str) -> bool:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(
        r"^(description:\s*).+$",
        rf"\1{new_desc}",
        text,
        count=1,
        flags=re.M,
    )
    if count != 1:
        raise ValueError(f"Could not update description in {path}")
    path.write_text(updated, encoding="utf-8")
    return True


def main() -> int:
    updated = 0
    for skill_name, desc in sorted(DESCRIPTIONS.items()):
        matches = list(ROOT.rglob(f"*/{skill_name}/SKILL.md"))
        if len(matches) != 1:
            print(f"SKIP {skill_name}: found {len(matches)} paths")
            continue
        update_description(matches[0], desc)
        updated += 1
        print(f"OK {skill_name}")
    print(f"Updated {updated} descriptions.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
