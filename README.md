# Erasmus Meta Genetic Programming: Generation III

:warning: **EGP is under construction: Feel free to browse but don't hope to find organised documentation & a usable application (yet).** :warning:

![EGP Logo: The tree of life with the milkyway shining through its branches](https://github.com/user-attachments/assets/bc6f624e-8047-4667-bd75-3f57985ed5c1)

Erasmus Meta Genetic Programming, Erasmsus GP or just EGP, emulates the principles of evolution through a synthetic framework, using functional primitives creating a dynamic and adaptive artificial ecosystem to solve problems.

## Documentation Index

### 🏁 Introduction

- [**Overview**](docs/intro/overview.md) – How EGP works at a high level.
- [**Background**](docs/intro/background.md) – An introduction to Genetic Programming.
- [**Goals**](docs/intro/goals.md) – What EGP aims to achieve.
- [**Why? (FAQ)**](docs/intro/why.md) – Common questions and answers.
- [**Architecture**](docs/intro/architecture.md) – The high-level system structure.
- [**Implementation**](docs/intro/implementation.md) – Technical details of the implementation.
- [**Alternate View**](docs/intro/alternate.md) – "Evolution: A Synthetic Approach."

### 📐 Design & Development

- [**Design Principles**](docs/design/principles.md) – The core philosophy.
- [**Design Concepts**](docs/design/concepts.md) – Fundamental ideas.
- [**Selection Algorithm**](docs/design/selection.md) – How evolution is driven.
- [**Setup & Development**](docs/development/setup.md) – Getting started as a developer.
- [**Style Guide**](docs/development/style_guide.md) – Coding standards.
- [**Lifecycle**](docs/development/lifecycle.md) – System lifecycle and states.

### 🏗️ Components Deep-Dive

- [**Common Utilities**](docs/components/common/object_deduplicator.md) – Shared logic and logo.
- [**Database**](docs/components/database/database.md) – Schema and [manager architecture](docs/components/database/manager_architecture.md).
- **Core Engine (egppy):**
  - [**Genotype**](docs/components/core/genotype.md) – Structure of genetic material.
  - [**Gene Pool**](docs/components/core/gene_pool.md) – Managing genetic diversity.
  - [**Populations**](docs/components/core/populations.md) – Groups of individuals.
  - [**Genetic Codes**](docs/components/core/genetic_code/definitions.md) – Rules and [relationships](docs/components/core/genetic_code/relationships.md).
  - [**Physics**](docs/components/core/physics/overview.md) – [Mutation](docs/components/core/physics/mutation.md), [Insertion](docs/components/core/physics/insertion.md), and [Selection](docs/components/core/physics/selection.md).
- [**Worker**](docs/components/worker/design.md) – [Executor](docs/components/worker/executor.md) and [workflow](docs/components/worker/workflow.md).
- [**Storage**](docs/components/storage/stores.md) – Data persistence.
- [**Problems**](docs/components/problems/overview.md) – [Genesis](docs/components/problems/genesis.md) and [Tic-Tac-Toe](docs/components/problems/tic-tac-toe.md).
