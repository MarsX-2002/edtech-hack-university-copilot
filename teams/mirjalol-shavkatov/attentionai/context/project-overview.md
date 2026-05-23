# Career AI Assistant

## Overview

Career AI Assistant is a multilingual Telegram bot MVP designed for university career centers. Grounded in the university's career materials and partner job listings, it helps students create Skill Passports, construct ATS-friendly resumes, simulate mock interviews using the STAR method, and match with vacancies. Career center admins gain analytics dashboards and broadcast messaging tools.

## Goals

1. Assess student skills and provide personalized gap analyses.
2. Build ATS-optimized resumes and professional profiles.
3. Conduct text-based interactive mock interviews evaluating answers using the STAR method.
4. Match students automatically to partner vacancies based on skill alignment.
5. Provide administrative controls: analytics reporting and group broadcast notifications.
6. Support Uzbek (primary), Russian, and English.

## Core User Flow

1. Student interacts with the Telegram bot and selects their preferred language.
2. Student registers their profile details.
3. Student accesses features via the main keyboard menu:
   - **Skill Passport**: Enters tech skills, projects, and gets a gap analysis & 3-month plan.
   - **Resume Builder**: Enters target job details and gets an ATS-friendly markdown resume.
   - **Interview Practice**: Picks question types, answers questions, and receives STAR evaluations.
   - **Vacancies**: Receives automatically scored job matches with direct application links.
   - **Career Advice**: Asks general career/networking questions answered via RAG.
4. Admins use `/admin` or `/stats` to view aggregated feature usage, average interview scores, and target role distribution.
5. Admins use `/broadcast <msg>` to send announcements to all registered students.

## Scope

### In Scope
- Telegram Bot interface.
- Local JSON database storage for persistent records.
- Chroma DB vector search for career documents.
- Multi-step conversational state machine with full back/cancel options.
- Multi-language dictionary and runtime translation switching.
- Standard fallback mode for offline/mock presentation.

### Out of Scope
- Streamlit web interface.
- Student authentication or OAuth (uses Telegram User ID instead).
- Payment gateways.
- Multi-tenant SaaS setups.
