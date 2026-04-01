"""Tab 4: AI Document Q&A using Claude RAG."""

import streamlit as st
from pathlib import Path
import os

DOCS_DIR = Path(__file__).parent.parent / "docs"

# Pre-built knowledge base about Tri-State and NERC CIP
KNOWLEDGE_BASE = """
=== TRI-STATE GENERATION AND TRANSMISSION ASSOCIATION OVERVIEW ===

Tri-State Generation and Transmission Association is a wholesale electric cooperative that provides
electricity to 42 member utility cooperatives and one public power district across four states:
Colorado, Nebraska, New Mexico, and Wyoming. These member systems serve approximately one million
consumers across roughly 200,000 square miles of the rural and semi-rural Western United States.

Headquarters: Westminster, Colorado (Denver metro area)
Approximate Revenue: $1.5-1.7 billion annually
Employees: Approximately 1,200-1,500
Legal Structure: Not-for-profit cooperative, member-owned

=== RESPONSIBLE ENERGY PLAN ===

Tri-State's Responsible Energy Plan commits to:
- 80% reduction in greenhouse gas emissions by 2030 (from 2005 baseline levels)
- Net-zero emissions target by 2050
- Retirement or conversion of coal-fired generation assets
- Significant expansion of wind, solar, and battery storage resources
- Addition of 2,400+ MW of new renewable resources by 2030

Key generation assets in transition:
- Craig Generating Station (Colorado): Phased retirement of coal units
- Escalante Generating Station (New Mexico): Closed in 2020
- Laramie River Station (Wyoming): Transition planning underway
- Multiple new solar and wind facilities across the service territory

=== MEMBER RELATIONS AND CONTRACT STRUCTURE ===

Tri-State operates under long-term wholesale supply contracts with member cooperatives. These
contracts historically required members to purchase 95% of their power from Tri-State through 2050.

Recent developments:
- Several members (United Power, La Plata Electric, Kit Carson Electric) have sought contract
  modifications or exits to pursue independent power sourcing
- Tri-State introduced a Contract Termination Payment (CTP) framework
- FERC rate jurisdiction was voluntarily adopted (2019-2020), replacing prior self-regulation
- Partial requirements contracts now allow members more flexibility for local generation

=== REGULATORY ENVIRONMENT ===

FERC (Federal Energy Regulatory Commission):
- Tri-State is now under FERC rate jurisdiction for wholesale rates
- Rate filings are subject to federal review and intervenor participation
- FERC Order 2222 affects distributed energy resource participation in wholesale markets

State Regulations:
- Colorado: HB19-1261 and SB19-236 mandate aggressive clean energy targets
- New Mexico: Energy Transition Act affects operations in the state
- Wyoming and Nebraska: Different regulatory frameworks for cooperatives

NERC CIP (Critical Infrastructure Protection):
- Tri-State must comply with NERC CIP standards for bulk electric system cybersecurity
- Standards cover: electronic security perimeters, access management, incident response,
  supply chain risk management, configuration management, vulnerability assessments
- CIP-002 through CIP-014 are the primary applicable standards
- Critical assets include: generation control systems, SCADA/EMS, transmission substations

=== NERC CIP STANDARDS SUMMARY ===

CIP-002: BES Cyber System Categorization
- Identifies and categorizes Bulk Electric System (BES) Cyber Systems as High, Medium, or Low impact
- Requires annual review of impact categorization

CIP-003: Security Management Controls
- Requires documented cybersecurity policies for BES Cyber Systems
- Specifies management accountability and governance requirements

CIP-004: Personnel and Training
- Security awareness training requirements
- Personnel risk assessment (background checks)
- Access management and authorization

CIP-005: Electronic Security Perimeters
- Defines Electronic Security Perimeters (ESPs) for BES Cyber Systems
- Controls remote access and external connectivity
- Requires monitoring of network traffic at ESP boundaries

CIP-006: Physical Security
- Physical access controls for BES Cyber Systems
- Visitor management and monitoring
- Physical access logging and alerting

CIP-007: System Security Management
- Ports and services management
- Security patch management
- Malicious code prevention
- Security event monitoring and logging

CIP-008: Incident Reporting and Response Planning
- Cybersecurity incident response plan requirements
- Incident reporting to E-ISAC
- Annual testing and review of response plans

CIP-009: Recovery Plans
- Recovery plans for BES Cyber Systems
- Backup and restoration requirements
- Annual testing of recovery plans

CIP-010: Configuration Change Management
- Baseline configurations for BES Cyber Systems
- Configuration change management processes
- Vulnerability assessments (at least every 15 months)
- Active and passive network vulnerability monitoring

CIP-011: Information Protection
- Protection of BES Cyber System Information (BCSI)
- Handling and disposal of sensitive information

CIP-012: Communications Between Control Centers
- Protection of real-time monitoring and control communications

CIP-013: Supply Chain Risk Management
- Risk management plans for vendor/supply chain
- Notification requirements for vendor security events
- Software integrity verification

CIP-014: Physical Security
- Risk assessment of transmission stations and substations
- Physical security plans for critical facilities
- Third-party verification of vulnerability assessments

=== AI GOVERNANCE CONSIDERATIONS FOR UTILITIES ===

Key risks of AI in the utility sector:
1. Safety: AI systems affecting grid operations must not compromise reliability
2. Cybersecurity: AI platforms must comply with NERC CIP if touching BES assets
3. Data Privacy: Customer data used in AI models must be protected
4. Bias and Fairness: AI used in rate-making or service decisions must be equitable
5. Explainability: Regulatory proceedings may require explanation of AI-driven decisions
6. Vendor Risk: Third-party AI services introduce supply chain considerations (CIP-013)

Recommended AI governance framework components:
- AI Policy and Standards: Enterprise-wide AI use policies
- AI Risk Assessment: Evaluation of AI risks before deployment
- AI Ethics Board or Council: Cross-functional review of AI initiatives
- Model Risk Management: Validation, monitoring, and documentation of AI models
- Data Governance: Data quality, lineage, and access controls for AI training data
- Regulatory Monitoring: Tracking evolving AI regulations (federal and state)
- Incident Response: Plans for AI-related incidents or failures
- Audit and Compliance: Regular review of AI systems against policies and regulations
"""


def render():
    from tabs.data_badge import provenance, chart_badges, real, simulated, model

    st.header("AI Document Q&A Assistant")
    st.markdown(
        "Ask questions about Tri-State's operations, NERC CIP compliance, energy strategy, "
        "or AI governance. Powered by **Claude** with retrieval-augmented generation (RAG) "
        "over Tri-State's public information and regulatory standards."
    )
    provenance(
        real_items=["NERC CIP standard descriptions", "Tri-State public facts"],
        simulated_items=["Curated knowledge base (not connected to internal docs)"],
        production_note="Vector database over internal documents, FERC filings, tariffs, and operational procedures",
    )

    # Check for API key
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        api_key = st.text_input(
            "Enter your Anthropic API Key to enable the AI assistant:",
            type="password",
            help="Get your API key at console.anthropic.com",
        )

    # Suggested questions
    st.markdown("### Suggested Questions")
    suggested = [
        "What are Tri-State's CO₂ reduction targets and how are they tracking?",
        "Explain NERC CIP-013 supply chain risk management requirements.",
        "What AI governance framework would you recommend for a utility cooperative?",
        "How could AI help with Tri-State's member relations challenges?",
        "What are the key risks of deploying AI in grid operations?",
        "Summarize the NERC CIP standards most relevant to AI deployment.",
    ]

    selected_q = None
    cols = st.columns(3)
    for i, q in enumerate(suggested):
        with cols[i % 3]:
            if st.button(q, key=f"suggested_{i}", width="stretch"):
                selected_q = q

    st.markdown("---")

    # Chat interface
    if "rag_messages" not in st.session_state:
        st.session_state.rag_messages = []

    # Display chat history
    for msg in st.session_state.rag_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Get user input
    user_input = st.chat_input("Ask a question about Tri-State, NERC CIP, or AI governance...")
    if selected_q:
        user_input = selected_q

    if user_input:
        # Add user message
        st.session_state.rag_messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        # Generate response
        with st.chat_message("assistant"):
            if not api_key:
                response = _generate_fallback_response(user_input)
                st.markdown(response)
            else:
                with st.spinner("Analyzing documents and generating response..."):
                    response = _generate_claude_response(api_key, user_input, st.session_state.rag_messages)
                    st.markdown(response)

        st.session_state.rag_messages.append({"role": "assistant", "content": response})

    # --- Architecture Explainer ---
    with st.expander("How This Works: RAG Architecture"):
        st.markdown(
            "### Retrieval-Augmented Generation (RAG) Pipeline\n\n"
            "```\n"
            "┌─────────────┐    ┌──────────────────┐    ┌─────────────┐\n"
            "│  User Query │───▶│ Document Retrieval│───▶│   Claude    │\n"
            "│             │    │ (Knowledge Base)  │    │  (Anthropic)│\n"
            "└─────────────┘    └──────────────────┘    └──────┬──────┘\n"
            "                                                  │\n"
            "                                                  ▼\n"
            "                                          ┌──────────────┐\n"
            "                                          │  Grounded    │\n"
            "                                          │  Response    │\n"
            "                                          └──────────────┘\n"
            "```\n\n"
            "**Current Implementation:**\n"
            "- Knowledge base contains Tri-State public information, NERC CIP standards, "
            "and AI governance frameworks\n"
            "- Claude processes the query with relevant context for grounded responses\n"
            "- All answers are traceable to source documents\n\n"
            "**Production Enhancement Path:**\n"
            "- Vector database (e.g., Pinecone, pgvector) for semantic search over thousands of documents\n"
            "- Embedding model for document chunking and retrieval ranking\n"
            "- Integration with Tri-State's document management systems\n"
            "- Audit logging for compliance with NERC CIP-004 (access management)\n"
            "- Role-based access controls aligned with NERC CIP-005"
        )


def _generate_claude_response(api_key, question, history):
    """Generate a response using Claude with RAG context."""
    try:
        from anthropic import Anthropic

        client = Anthropic(api_key=api_key)

        system_prompt = (
            "You are an AI assistant for Tri-State Generation and Transmission Association. "
            "You help answer questions about Tri-State's operations, energy strategy, "
            "NERC CIP compliance, and AI governance. Use the provided knowledge base to "
            "ground your responses in factual information. If you're unsure about something, "
            "say so clearly. Always be professional and cite relevant standards or policies.\n\n"
            "KNOWLEDGE BASE:\n" + KNOWLEDGE_BASE
        )

        # Build message history (last 6 messages for context)
        messages = []
        for msg in history[-6:]:
            messages.append({"role": msg["role"], "content": msg["content"]})
        # Ensure last message is the current question
        if not messages or messages[-1]["content"] != question:
            messages.append({"role": "user", "content": question})

        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
        )

        return response.content[0].text

    except Exception as e:
        return f"Error connecting to Claude API: {str(e)}\n\nFalling back to pre-built response.\n\n{_generate_fallback_response(question)}"


def _generate_fallback_response(question):
    """Generate a pre-built response when API key is not available."""
    q_lower = question.lower()

    if "co2" in q_lower or "emission" in q_lower or "target" in q_lower or "reduction" in q_lower:
        return (
            "**Tri-State's CO₂ Reduction Targets:**\n\n"
            "Tri-State's Responsible Energy Plan commits to:\n"
            "- **80% reduction in greenhouse gas emissions by 2030** (from 2005 baseline)\n"
            "- **Net-zero emissions by 2050**\n"
            "- Addition of 2,400+ MW of new renewable resources by 2030\n\n"
            "Key actions include phased retirement of coal assets (Craig Station, Laramie River Station), "
            "significant wind and solar expansion, and battery storage deployment. "
            "The Escalante Station in New Mexico was already closed in 2020.\n\n"
            "Based on the Energy Mix data in this dashboard, coal has declined significantly "
            "but the pace may need to accelerate to meet the 2030 target."
        )

    elif "cip-013" in q_lower or "supply chain" in q_lower:
        return (
            "**NERC CIP-013: Supply Chain Risk Management**\n\n"
            "CIP-013 requires utilities to:\n"
            "1. **Develop a supply chain risk management plan** for industrial control system hardware, "
            "software, and services\n"
            "2. **Assess vendor risks** during procurement of BES Cyber Systems\n"
            "3. **Require vendor notification** of security incidents that may affect products/services\n"
            "4. **Verify software integrity** before installation\n\n"
            "**AI Relevance:** Any third-party AI platform or model used in grid operations "
            "falls under CIP-013 supply chain requirements. This means:\n"
            "- AI vendors must be assessed for security practices\n"
            "- Cloud-based AI services need security review before deployment\n"
            "- Model updates and patches need integrity verification\n"
            "- Vendor incident response capabilities must be documented"
        )

    elif "governance" in q_lower or "framework" in q_lower:
        return (
            "**Recommended AI Governance Framework for Tri-State:**\n\n"
            "A utility-focused AI governance framework should include:\n\n"
            "1. **AI Council** — Cross-functional body (IT, legal, compliance, risk, operations) "
            "to review and approve AI initiatives\n"
            "2. **AI Policy & Standards** — Enterprise-wide policies covering acceptable use, "
            "data handling, model documentation, and ethical guidelines\n"
            "3. **Risk Assessment Framework** — Tiered evaluation process:\n"
            "   - Low risk: Internal analytics, document search\n"
            "   - Medium risk: Customer-facing applications, workforce tools\n"
            "   - High risk: Grid operations, safety-critical systems\n"
            "4. **Model Risk Management** — Validation, monitoring, drift detection, and documentation\n"
            "5. **NERC CIP Alignment** — Ensure AI systems touching BES assets comply with "
            "CIP-002 through CIP-014\n"
            "6. **Audit & Compliance** — Regular review cadence with documented evidence\n\n"
            "This framework enables innovation while maintaining the regulatory compliance "
            "and safety standards required in the utility sector."
        )

    elif "member" in q_lower or "relation" in q_lower:
        return (
            "**AI Applications for Member Relations:**\n\n"
            "AI could help address Tri-State's member relations challenges in several ways:\n\n"
            "1. **Sentiment Monitoring** (as demonstrated in Tab 1) — Track public discourse "
            "and member feedback to identify emerging issues early\n"
            "2. **Rate Impact Modeling** — Predictive models to simulate how rate changes "
            "affect different member cooperatives, enabling more equitable rate design\n"
            "3. **Member Service Analytics** — AI-driven analysis of member needs, consumption "
            "patterns, and satisfaction to personalize engagement\n"
            "4. **Contract Optimization** — Decision intelligence tools to model contract "
            "modification scenarios and their financial impact on both Tri-State and members\n"
            "5. **Communication AI** — NLP tools to help draft member communications that "
            "address concerns proactively\n\n"
            "The key is demonstrating value to members — if AI helps reduce costs or improve "
            "service, it strengthens the cooperative relationship."
        )

    elif "risk" in q_lower or "grid" in q_lower or "operation" in q_lower:
        return (
            "**Key Risks of AI in Grid Operations:**\n\n"
            "1. **Safety & Reliability** — AI systems affecting grid dispatch or protection "
            "must not compromise bulk electric system reliability. Failure modes must be well-understood.\n"
            "2. **NERC CIP Compliance** — AI platforms touching BES Cyber Systems must comply "
            "with CIP standards for access control, change management, and incident response\n"
            "3. **Cybersecurity** — AI models can be attack vectors (adversarial inputs, "
            "model poisoning). Grid-connected AI needs robust security architecture.\n"
            "4. **Explainability** — Regulators and operators need to understand why an AI "
            "system made a specific recommendation, especially for market or dispatch decisions\n"
            "5. **Data Quality** — AI models are only as good as their training data. "
            "SCADA and sensor data quality must be validated.\n"
            "6. **Vendor Lock-in** — Over-reliance on specific AI vendor platforms creates "
            "strategic risk and CIP-013 supply chain concerns\n\n"
            "**Mitigation:** Start with low-risk, high-value use cases (forecasting, analytics) "
            "and build trust before deploying AI in operational control loops."
        )

    elif "nerc" in q_lower or "cip" in q_lower:
        return (
            "**NERC CIP Standards Most Relevant to AI Deployment:**\n\n"
            "1. **CIP-002** (Categorization) — AI systems connected to BES assets must be "
            "categorized by impact level, which determines the applicable security requirements\n"
            "2. **CIP-005** (Electronic Security) — AI platforms need properly defined "
            "Electronic Security Perimeters, especially for cloud-based or remote AI services\n"
            "3. **CIP-007** (System Security) — Patch management, port/service management, "
            "and malicious code prevention apply to AI infrastructure\n"
            "4. **CIP-010** (Config Management) — AI model updates are configuration changes "
            "that require documented change management processes\n"
            "5. **CIP-013** (Supply Chain) — Third-party AI platforms and models are supply "
            "chain components requiring risk assessment\n"
            "6. **CIP-004** (Personnel) — Staff using AI systems in BES contexts need "
            "appropriate training and access authorization\n\n"
            "**Key Principle:** AI in utilities must be treated as a technology deployment "
            "within the existing NERC CIP framework, not as an exception to it."
        )

    else:
        return (
            "I can answer questions about:\n\n"
            "- **Tri-State's operations** — generation mix, member structure, strategic plans\n"
            "- **NERC CIP compliance** — cybersecurity standards for bulk electric systems\n"
            "- **AI governance** — frameworks, risk management, ethical considerations\n"
            "- **Energy transition** — coal retirement, renewable expansion, emissions targets\n"
            "- **AI use cases** — price forecasting, sentiment analysis, grid optimization\n\n"
            "Try asking a more specific question, or use one of the suggested questions above. "
            "For the full AI-powered experience, enter your Anthropic API key."
        )
