# DevOps Practices with Git and Databricks: Development to Production Workflow

This document outlines how our team manages code development and deployment using **Git** for version control and **Databricks** for running data workflows. It describes the current branching strategy and step-by-step deployment process we follow, from initial development to final production. The goal is to explain these practices in simple terms for product managers, focusing on what we do (without suggesting any changes or improvements).

## Branching Strategy

In line with industry best practices, the team maintains multiple Git branches aligned with different environments (development, staging, limited release, and production). Each branch corresponds to a Databricks repository (folder) that holds the code for that stage. This separation into environment-specific branches (often called *maturity branches*) ensures that only code proven at one level moves on to the next. The key branches and their Databricks repo counterparts are:

* **Development Branch (`quant`)** – This is the main **development** branch in Git, where new code is pushed after initial local testing. It corresponds to the *Databricks* **`quant`** repository/folder, which is used as an internal development and testing environment. Code in this branch is under active development and may change frequently. Developers integrate their work here for **internal testing** and quality checks before it goes to any users.

* **Staging Branch (`quant_stg`)** – This Git branch represents the **staging** environment. It maps to the Databricks **`quant_stg`** repository, which is used for staging and **User Acceptance Testing (UAT)**. Only code that has passed the internal tests (in the `quant` branch) is merged into `quant_stg`. The staging branch holds **fully developed and tested** features ready for final validation. It acts as a rehearsal area where the team and a small set of users can verify that everything works as expected in a production-like setting.

* **Limited Release Branch (`quant_lr`)** – This is a Git branch for **limited release** deployments. It corresponds to the Databricks **`quant_lr`** repository, representing a limited release environment. This branch is used when a feature or update is **needed in production urgently or for a trial**, but the team isn’t entirely confident in its stability. Code merged into `quant_lr` is deployed to a subset of the production environment (a “canary” or limited rollout) to gather feedback and ensure it doesn’t cause issues before rolling out broadly. The limited release environment lets us deliver critical updates to a small group of users or on limited data, acting as a safety net by containing potential issues within a smaller scope.

* **Production Branch (`quant_live`)** – This is the **production** Git branch, mapped to the Databricks **`quant_live`** repository/folder. It contains the code that has been fully validated and approved to run for all users. Only **stable, thoroughly tested** code is merged into `quant_live`. The production branch is what powers the final live workflows and is the source of truth for our production data. Changes here trigger updates to the production jobs in Databricks, and ultimately all outputs generated from this branch are considered official production results.

* **Personal Development Folders (Databricks)** – In addition to the shared Git branches above, each developer also has a personal folder in Databricks for **individual code development and experimentation**. These personal folders are like sandboxes where code is initially written and run. They are not tracked in a shared Git branch. Instead, a developer works in their personal workspace, and once the code seems to be working locally, they commit those changes to the team’s Git repository (typically to the `quant` development branch). This way, the early, iterative work is isolated until it’s ready to be shared.

**Mapping of Git Branches to Databricks Repos and Purpose:**

| **Git Branch**               | **Databricks Repo/Folder**         | **Purpose / Environment**                                                                                   |
| ---------------------------- | ---------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| *(None – Personal)*          | Personal user folder               | Individual developer workspace for initial coding and testing.                                              |
| `quant` (Development)        | `quant` repo (Dev env)             | Team development & internal testing environment (writes to **`quant`** schema in Snowflake).                |
| `quant_stg` (Staging)        | `quant_stg` repo (UAT env)         | Staging/UAT environment for user acceptance testing (writes to **`quant_stg`** schema in Snowflake).        |
| `quant_lr` (Limited Release) | `quant_lr` repo (Limited Prod)     | Limited release environment – partial production deployment for early release features (monitored rollout). |
| `quant_live` (Production)    | `quant_live` repo (Production env) | Full production environment for all end users (writes to **`quant_live`** schema in Snowflake).             |

Our Databricks workspace is organized so that each of these repos holds the code matching the respective Git branch. For example, the **production** folder in Databricks always has the code from the `quant_live` branch (our production branch) checked out, ensuring the code running in production is exactly what’s in the `quant_live` Git branch. This clear separation helps prevent mix-ups – code in the development branch only runs in the dev environment, staging branch code runs in the UAT environment, and so on. It also means we can control access and permissions; for instance, only certain team members can merge into `quant_live` (production) and the production folder in Databricks is locked down to avoid accidental edits.

## Deployment Workflow

The deployment workflow from development to production follows these clear stages:

### 1. Development Stage

* Code is initially developed and informally tested within **individual personal Databricks folders**.
* Once informally validated, the code is pushed to the Git branch `quant`.

### 2. Quality Checks & Stability Monitoring

* Databricks `quant` repository syncs changes from the Git `quant` branch.
* Workflows are scheduled and monitored for several days to assess stability and quality.
* Pipeline outputs are written to Snowflake tables within the `quant` schema.
* Any issues require revisions back in the personal folder, after which changes are re-pushed to Git.
* Once stable, a **merge request** is created from `quant` to `quant_stg` branch on Git.
* At least one mandatory **code review** by another team member is conducted before approval.

### 3. User Acceptance Testing (UAT)

* Databricks `quant_stg` repository pulls updates from Git `quant_stg` branch.
* Workflows are executed for User Acceptance Testing (UAT).
* Pipeline outputs are stored in Snowflake under the `quant_stg` schema.
* Results are shared with end users for validation.
* After successful UAT, code is marked ready for production deployment.

### 4. Production Deployment

* Deployment occurs based on code maturity and reliability assessment:

  * **Limited Release**: If the code quality is acceptable but not fully reliable, it is merged into the Git `quant_lr` branch. Changes are synced into Databricks `quant_lr` repository. Limited-release workflows write outputs to Snowflake.
  * **Full Production Release**: If the code is fully reliable, it is merged into Git `quant_live` branch. Changes are synced into Databricks `quant_live` repository, and production workflows are executed, writing results to Snowflake tables within the `quant_live` schema.\

Throughout this lifecycle, each stage serves as a quality filter: development (quant) catches bugs early during integration testing, staging (quant_stg) ensures user requirements are met, limited release (quant_lr) limits the impact of any last uncertainties, and production (quant_live) delivers the final value. This structured approach, using clear Git branching and Databricks environments, ensures that our product data pipelines and features are robust and reliable by the time they reach our end users.