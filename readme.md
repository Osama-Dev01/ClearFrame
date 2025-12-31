**Note:** The detailed System Design Report is included in the repository as `ClearFrame_FinalYearProject_Report.docx` . It contains complete architecture diagrams, use-case details, domain model, sequence diagrams, class diagrams, and testing tables.

# ClearFrame: AI-Powered Misinformation Detection System for Social Media

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)  
![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)  
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)  
![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react)  
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791?logo=postgresql)  
![Hugging Face](https://img.shields.io/badge/🤗-Hugging%20Face-yellow)

**ClearFrame** is a Final Year Project (Session 2021–2025) developed at the Department of Computer Science, National University of Computer and Emerging Sciences (FAST-NU), Islamabad, Pakistan.



**Project Team:**  
- Osama Ali (21I-0587)  
- Talha Sohail (21I-0374)  
- Muhammad Huzaifa (21I-2975)

**Supervised by:** Mr. Majid Hussain  
**Co-Supervised by:** Dr. Zeshan Khan

## Project Overview

<p align="center">
  <img src="assets/clearframe.png" alt="ClearFrame Overview" width="600">
</p>

ClearFrame is a comprehensive **AI-driven misinformation detection and fact-checking system** tailored to combat the rapid spread of false and misleading information on social media platforms, with a strong focus on Pakistan-relevant contexts. It delivers real-time, automated verification of news, claims, and statements shared on Twitter (X) and Facebook, supporting multilingual (Urdu + English) content common in the region.

The system integrates advanced Natural Language Processing, retrieval-augmented pipelines, graph-based trend analysis, and structured crowdsourced verification to provide accurate, transparent, and timely fact-checking results.

### Problem Statement
Misinformation and disinformation spread virally on social media, significantly influencing public opinion in critical areas such as politics, economy, sports, international relations, and religious content. Traditional fact-checking is slow and manual—ClearFrame solves this through automated, real-time verification enhanced by human oversight.

### Key Objectives
- Real-time automated claim detection and verification
- Robust handling of mixed Urdu–English content
- Cross-referencing with credible sources using retrieval-augmented techniques
- Detection of coordinated misinformation via network analysis
- Improved accuracy through structured crowdsourced verification
- Minimal user effort via seamless browser integration

## Core Modules

1. **Text Extraction and Contextual Categorization**  
   - Extracts text from posts (including OCR for images when required)  
   - Classifies content into Pakistan-relevant categories: Politics & Government, Sports, International Relations, Finance & Economy, Islamic Content  
   - Filters out personal opinions, jokes, and non-verifiable statements

2. **Cross-Verification Engine**  
   - Extracts key entities and claims  
   - Performs semantic matching against a curated Pakistan-specific database of official accounts  
   - Employs **Retrieval-Augmented Generation (RAG)-style pipelines** using Google Custom Search API and web results for dynamic fact-checking  
   - Produces detailed verification reports with credibility scores and direct source links

3. **Narrative and Trend Analysis**  
   - Represents user-post interactions as graphs  
   - Utilizes **Graph Neural Networks (GNNs)** trained on datasets like FakeNewsNet to identify propagation anomalies, key influencers, and coordinated misinformation clusters

4. **Crowdsourced Verification**  
   - Regular users can flag suspicious content  
   - Verified members vote (True/False/Unverified) and submit evidence/justification  
   - Community votes are aggregated to refine and enhance automated verification accuracy

5. **User Interface**  
   - **Chrome Browser Extension**: Seamless on-the-fly verification with visual badges (True/False/Unverified), confidence meter, and one-click source access—designed for **minimum user effort**  
   - **Web Dashboard**: For viewing detection history, flagging, voting, and admin management

## Technical Details

### Backend & Infrastructure
- **API Server**: FastAPI (Python) – high-performance, asynchronous backend for real-time processing
- **Database**: PostgreSQL – stores user accounts, verification history, official source database, and crowdsourced contributions
- **Web Dashboard**: React.js – modern, responsive frontend for admin and verified member interactions

### Key Hugging Face Models

#### Named Entity Recognition (NER)
- **Urdu NER**: [`mirfan899/urdu-bert-ner`](https://huggingface.co/mirfan899/urdu-bert-ner) – fine-tuned for accurate entity extraction in Urdu script
- **English/Multilingual NER**: [`Davlan/xlm-roberta-base-ner-hrl`](https://huggingface.co/Davlan/xlm-roberta-base-ner-hrl) – high-performance for English and code-mixed text

#### Natural Language Inference (NLI) / Entailment
- **Urdu & Multilingual NLI**: [`joeddav/xlm-roberta-large-xnli`](https://huggingface.co/joeddav/xlm-roberta-large-xnli) – zero-shot cross-lingual inference for Urdu and mixed-language claim verification
- **English NLI**: [`facebook/bart-large-mnli`](https://huggingface.co/facebook/bart-large-mnli) – strong entailment classification for English claims

#### Base Multilingual Model
- **XLM-RoBERTa** (various sizes) – core model for contextual categorization, semantic similarity, and filtering non-verifiable content

### Data Pipeline & Model Enhancement
- Custom **web scraping scripts** to collect Pakistan-specific data from official accounts, news outlets, and fact-checking platforms
- Extensive **text normalization and preparation** (handling Roman Urdu, code-switching, typos, and script variations)
- Scraped datasets used for fine-tuning and adapting models to local linguistic patterns

### External Integrations
- Twitter API v2 & Facebook Graph API
- Google Custom Search API
- OCR for image-based text extraction

### Performance
- **Average Response Time**: ~10 seconds from post detection to final verification result display (encompassing entity extraction, retrieval, inference, and scoring)

## Key Features Summary
- Real-time automated verification with RAG-enhanced cross-checking
- Strong multilingual (Urdu + English) support tailored for Pakistani social media
- Crowdsourced enhancement for greater accuracy on ambiguous or emerging claims
- Chrome extension enabling effortless, instant fact-checking while browsing
- Transparent results with source links and confidence indicators

## Conclusion

ClearFrame delivers a robust, scalable, and contextually relevant solution to misinformation within Pakistan's digital ecosystem. By combining state-of-the-art NLP models, retrieval-augmented verification, graph-based trend detection, and structured community input, it empowers users to engage with social media more confidently and responsibly.

**Repository Contents**: Source code (backend, frontend, Chrome extension), final project report (`ClearFrame_FinalYearProject_Report.docx`), architecture diagrams, model notebooks, and data scraping utilities.

For questions, contributions, or collaboration, feel free to open an issue!