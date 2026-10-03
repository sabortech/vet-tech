# Spec Delta

## Purpose

Control access to veterinary records through explicit tutor consent and preserve
an auditable history of every sensitive operation on a pet's health information.

## ADDED Requirements

### Requirement: Explicit veterinarian authorization

The system SHALL allow a veterinarian to view, edit or export a pet's record
only while an authorization granted by that pet's tutor is active. Only the
responsible tutor SHALL be able to create, maintain or revoke that
authorization.

#### Scenario: Authorized record access

- **GIVEN** the pet's tutor granted an active authorization to the veterinarian
- **WHEN** the veterinarian requests an allowed record operation
- **THEN** the system SHALL permit the operation

#### Scenario: Unauthorized or revoked record access

- **GIVEN** no active authorization exists, or an existing authorization was
  revoked
- **WHEN** the veterinarian requests to view, edit or export the pet's record
- **THEN** the system SHALL deny the operation immediately

#### Scenario: Unauthorized authorization management

- **GIVEN** the requester is not the responsible tutor of the pet
- **WHEN** the requester attempts to create, change or revoke an authorization
- **THEN** the system SHALL deny the operation

### Requirement: Immutable access audit

The system SHALL create an audit record for every veterinarian record view,
edit or export, containing the pet, veterinarian, action and timestamp. Audit
records SHALL NOT be editable or deletable by application users.

#### Scenario: Auditing a successful sensitive operation

- **GIVEN** a veterinarian has an active authorization
- **WHEN** the veterinarian views, edits or exports the pet's record
- **THEN** the system SHALL complete the operation and create exactly one audit
  record describing it

#### Scenario: Auditing a denied operation

- **GIVEN** a veterinarian does not have an active authorization
- **WHEN** the veterinarian attempts a sensitive record operation
- **THEN** the system SHALL deny access and SHALL NOT create a successful-action
  audit record

#### Scenario: Preventing audit tampering

- **GIVEN** an audit record has been created
- **WHEN** any application user attempts to modify or delete it
- **THEN** the system SHALL reject the request and preserve the original record
