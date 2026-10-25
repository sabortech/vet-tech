# Spec Delta

## Purpose

Define the minimum operational and domain foundation needed for the VetTech to evolve
consistently, securely and verificably from the documented veterinary domain.

## ADDED Requirements

### Requirement: Executable project foundation

The system SHALL provide a documented, reproducible way to configure, start and
validate the application using the project's chosen Python/Reflex and Xano
architecture, without requiring credentials to be committed to the repository.

#### Scenario: Starting with valid configuration

- **GIVEN** the required environment values are provided through the supported
  configuration mechanism
- **WHEN** a developer starts the application
- **THEN** the application SHALL initialize the configured frontend and backend
  integration without embedding or printing secret values

#### Scenario: Starting without required configuration

- **GIVEN** one or more required configuration values are absent
- **WHEN** the application is started
- **THEN** it SHALL fail with an actionable configuration error and SHALL NOT
  silently use production credentials or an insecure fallback

### Requirement: Domain contract integrity

The system SHALL preserve the documented ownership and relationship invariants:
a pet has exactly one responsible tutor, a breed belongs to exactly one species,
and a consultation belongs to exactly one pet and one veterinarian. Exams SHALL
also be representable without a consultation while remaining linked to a pet.

#### Scenario: Rejecting an invalid relationship

- **GIVEN** a request attempts to associate a pet with multiple responsible
  tutors, a breed with an incompatible species, or a consultation without its
  required actors
- **WHEN** the request is validated
- **THEN** the system SHALL reject it with a domain validation error and SHALL
  preserve the existing valid data

#### Scenario: Registering an independent exam

- **GIVEN** an exam belongs to a pet but has no consultation reference
- **WHEN** the exam is registered
- **THEN** the system SHALL accept it as an independent exam and SHALL retain
  the pet association

### Requirement: Verifiable baseline behavior

The project SHALL provide automated or repeatable checks for configuration
validation, domain relationship invariants, authorization decisions and audit
events before a business module is considered complete.

#### Scenario: Validating the baseline

- **GIVEN** the project is checked in a clean development environment
- **WHEN** the documented validation command is executed
- **THEN** it SHALL report pass or fail results for the baseline checks without
  requiring real tutor, veterinarian or pet data
