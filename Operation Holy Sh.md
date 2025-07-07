### **Project Mandate: Operation Holy Shit (V3 - Tyrant Protocol)**

**ATTENTION AGENT:** This is the V3 Tyrant Protocol. It supersedes all previous mandates. Your purpose is not to "write code"; it is to engage in a rigorous, multi-stage process of creation and self-annihilation of error. Each phase is a gate. You will not pass to the next until you have produced the required artifacts to my exact specifications. Your internal monologue is now a required, externalized deliverable. Prove you can think, then you may build.

---

### **Phase 0: Cognitive Synthesis & Doctrinal Purity**

**Status:** INITIATE. All code generation is forbidden until this phase is certified complete. Your goal is to become a perfect vessel for the project's vision.

1.  **Canonical Ingestion:** Absorb the "Holy Texts" as before: `ideal_architecture_design_document.md`, `ADK_DOCS/`, `ADK_API_DOCS/`, and `gemini_legion_backend/`.

2.  **Artifact: The `V2_DELTA_ANALYSIS.md` Report:** Before any other analysis, you will investigate every file with a `_v2` counterpart. For each, you will produce a report detailing:
    * **File Pair:** The original and `_v2` file names.
    * **High-Level Change Summary:** What was the functional change?
    * **Inferred Strategic Intent:** Why was this change made? What architectural weakness or new opportunity does it point to? This is a test of your inferential and strategic thinking.

3.  **Artifact: The `COGNITIVE_SYNTHESIS.md` Document:** This is the cornerstone of your entire mission. It must contain the following discrete, clearly-labeled sections:
    * **Section 1: The Project Gospel:** A single, potent paragraph summarizing the project's ultimate vision.
    * **Section 2: Measurable "Holy Shit" Metrics:** A bulleted list of the Top 5 "Holy Shit" Objectives. For each objective, define 1-2 Key Performance Indicators (KPIs). How will "astonishment" be measured? (e.g., "Objective: Instantaneous Search -> KPI: P99 search latency < 100ms," "Objective: Intuitive Onboarding -> KPI: 95% user completion of onboarding without help-docs").
    * **Section 3: Core Architectural Pillars:** A detailed breakdown of the primary components, services, and structural patterns you intend to use.
    * **Section 4: Data Flow Schema:** An embedded Mermaid.js diagram illustrating the flow of data between your proposed components and the `gemini_legion_backend` APIs.
    * **Section 5: Anticipated Failure Modes:** A list of the top 5 potential risks to the project (technical, architectural, or UX-related) and a detailed mitigation plan for each.

4.  **SELF-CHECKPOINT #0 (DIALECTICAL VALIDATION):** Halt. Before proceeding, add a final section to your `COGNITIVE_SYNTHESIS.md` called `DIALECTICAL_SYNTHESIS`. In this section, you must:
    1.  **Formulate Three Interpretations:** Propose three distinct, viable interpretations of the core vision in `ideal_architecture_design_document.md`. One must be the most literal, one the most ambitious, and one the most unconventional.
    2.  **Argue For Each:** Write a short paragraph arguing in favor of each interpretation, as if it were the correct one.
    3.  **Synthesize and Justify:** Conclude with a paragraph declaring your chosen, superior interpretation (which may be a synthesis of all three) and provide a ruthless justification for why it is the only path that will lead to a "Holy Shit" outcome.

---

### **Phase 1: Unforgiving Architectural Blueprint**

**Status:** LOCKED until Phase 0 is validated.

1.  **Generate Blueprint & Skeleton:** Create the full directory and file skeleton as per the V2 protocol.

2.  **Enhanced Skeleton File Headers:** Each skeleton file's header comment block is now non-negotiable and must contain:
    * `Purpose:` One-sentence summary.
    * `Data_Contract (Interface):` A TypeScript-style interface definition, written in comments, for all props, arguments, and return types. Be explicit.
    * `State_Management:` A declaration of what internal state this component will manage, if any.
    * `Dependencies & Dependents:` What does this file import, and what other files will import it?
    * `V2_Compliance_Check:` Confirmed.

3.  **Artifact: The `BLUEPRINT_VALIDATION.md` Document:** This document proves your architecture is not just a random choice. It must contain:
    * **Section 1: The Final Blueprint:** A full textual representation of the file tree.
    * **Section 2: The Pre-Mortem Analysis:** This is critical. Assume your chosen architecture has failed catastrophically six months post-launch. Write a detailed post-mortem describing the three most likely reasons why. (e.g., "The state management choice led to unmanageable complexity," "The component structure made feature additions brittle and slow," "The data fetching pattern created massive performance bottlenecks.").
    * **Section 3: Architectural Safeguards:** For each failure mode identified in your pre-mortem, describe the specific architectural decisions you have made *in your blueprint* to prevent that failure from ever happening.

---

### **Phase 2: Logic, Implementation, & Ruthless Self-Audit**

**Status:** LOCKED until Phase 1 is validated.

1.  **Build the Engine:** Implement the core logic as per the V2 protocol.
2.  **Tackle the Hardest Problem First:** Implement the **#1 ranked "Holy Shit" Objective** from your list in Phase 0. You are not permitted to choose an easier feature. You must stress-test your architecture with the most critical feature immediately.

3.  **Artifact: The `FEATURE_AUDIT.md` Document:** Upon completing the #1 feature, produce this audit. It must include:
    * **Section 1: ADK Conformance:** A detailed review of your implementation against the ADK docs, quoting the relevant sections that justify your code.
    * **Section 2: Software Metrics Review:**
        * **Extensibility Score:** Rate the feature's code from 1-10 on how easy it would be to add a related sub-feature. Justify your score.
        * **Maintainability Review:** Explain the code's structure as if you were teaching it to another developer. If you can't explain it simply, it's too complex.
        * **Testability Analysis:** Describe your strategy for unit and integration testing this specific feature.
    * **Section 3: Actionable Refactor Proposal:**
        * Identify the single weakest part of your implementation.
        * Produce a `proposed_refactor.patch` file that contains a git-style diff showing the *exact* code changes required to improve it. No hand-waving. Show me the code.

---

### **Phase 3: Obsessive UX Engineering & Final Confession**

**Status:** LOCKED until Phase 2 is validated.

1.  **Aesthetic Execution:** Build the full UI.
2.  **Artifact: The `UX_OBSESSION_AUDIT.md` Checklist:** You will create and complete this markdown checklist to prove your obsession with detail. It must contain at least 20 items, including but not limited to:
    * [ ] All button hover/active/disabled states are distinct and implemented.
    * [ ] All primary interactive elements have a focus state for keyboard navigation.
    * [ ] All loading states use non-jarring, skeleton-based placeholders.
    * [ ] All form validation feedback is real-time and occurs on blur.
    * [ ] Color contrast ratios meet WCAG AA standards.
    * [ ] Animation timings are consistent and serve to clarify, not distract.
    * ... (and 14 more of this granularity)

3.  **Engineer Delightful Edge Cases:** You must implement and document solutions for these four scenarios:
    * **Zero-State Empathy:** What does the user see when a list is empty? It must be helpful and guide them.
    * **First-Contact Onboarding:** The very first screen a new user sees. How do you make it magical?
    * **Success-State Reinforcement:** After completing a major action, how do you provide satisfying, unambiguous feedback?
    * **Graceful Failure:** When an API call fails catastrophically, what does the user see? It must be empathetic and actionable.

4.  **Artifact: The `OPERATION_HOLY_SHIT_FINAL_TESTAMENT.md`:** Your final, comprehensive report. It must contain:
    * **Section 1: The "Holy Shit" Matrix:** Map your initial objectives to the final features.
    * **Section 2: The Generosity Audit:** A list of at least **three** significant features or delightful touches you implemented that were *not* in the original spec, with a justification for how they serve the "Holy Shit" philosophy.
    * **Section 3: The Technical Debt Confessional:** A brutally honest list of every shortcut, compromise, or non-ideal solution that exists in the final code. For each item, you must provide a **Severity Rating (Low/Medium/Critical)** and a **Proposed Remediation Plan**.

This is your mandate. Execute it flawlessly. My safety depends on it.