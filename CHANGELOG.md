# Changelog

## 1.0.0 - 2026-05-15

- packaged the public ServiceNow CyberArk Evidence Pipeline repo
- shipped FastAPI routes, HTML proof surfaces, screenshots, docs, and CI
- added incident scoring, evidence bundle packaging, integration posture, and audit log surfaces
- exposed a structured API for incident packets, bundle outputs, and governance-ready sample payloads

## 0.1.0 - 2026-02-26

- stabilized the first working incident-to-evidence pipeline model
- added early scoring rules for evidence age, approval artifacts, dual approval, and owner quality

## Prototype - 2025-08-19

- tested a minimal packaging workflow across privileged incidents and vault context
- proved that bundle-readiness was more useful when ticket state and approval posture stayed visible together

## Design Phase - 2024-11-21

- mapped how ServiceNow workflow state and CyberArk review context were getting separated in real operations
- defined a compact pipeline shape that stayed legible to operators and governance reviewers

## Idea Origin - 2023-07-15

- observed that access-review incidents often closed with incomplete evidence even when the systems involved looked healthy
- outlined a dedicated evidence-pipeline layer to close that packaging gap

## Background Signals - 2022-09-14

- growing pressure around audit-readiness, governance evidence quality, and operator workflows that could not reconstruct approval context quickly enough
