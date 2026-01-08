# 🚌🚗 RU-PATH: AI-Powered Campus Navigation & Parking Assistant

## 📌 Project Overview

RU-PATH is an AI-powered conversational assistant designed to help students, faculty, and visitors navigate Rutgers University–New Brunswick more efficiently. The system answers natural-language questions related to parking permits, parking lots, bus routes, bus stops, and building navigation across all Rutgers campuses (Busch, Livingston, College Ave, Cook/Douglass).

The project addresses real-world campus mobility challenges using Artificial Intelligence, Retrieval-Augmented Generation (RAG), and structured campus datasets, resulting in an intelligent, context-aware chatbot capable of multi-turn conversations.

---

## ❗ Problem Statement

Rutgers New Brunswick is a large, multi-campus university, and users frequently face the following issues:

### 🚘 Parking Challenges
- Multiple permit types (Primary, Secondary, Commuter, Resident)
- Complex and time-dependent parking rules
- Difficulty finding eligible parking near specific buildings
- Lack of clear, centralized parking guidance

### 🚌 Bus Navigation Challenges
- Multiple bus routes with overlapping stops
- Difficulty determining which bus to take and where to board
- Existing resources are static, fragmented, and non-interactive

### ⚠️ Lack of a Unified Intelligent System
- Information scattered across websites, PDFs, and maps
- No conversational interface
- No reasoning across parking, bus, and building data

As a result, users often waste time, take inefficient routes, or violate parking rules.

---

## 🎯 Project Goal

The goal of RU-PATH was to build a single AI assistant that can:
- 🧠 Understand natural-language campus navigation queries
- 📊 Retrieve accurate campus-specific data
- 🔗 Reason across parking, bus, and building information
- 💬 Support multi-turn conversations
- ✅ Provide clear, actionable guidance

---

## 💡 Solution Overview

RU-PATH is built using a Retrieval-Augmented Generation (RAG) architecture that combines structured Rutgers campus datasets with a Large Language Model (LLM). The system retrieves only the most relevant campus information using vector similarity search and then generates accurate, context-aware responses.

---

## 🏗️ System Architecture

### 📂 Data Layer
Manually curated and structured Rutgers datasets stored in JSON format, including:
- 🚗 Parking lots and permit eligibility
- 🚌 Bus routes and stops
- 🏫 Campus buildings and locations
- ⏰ Parking rules and time restrictions

Each entry contains campus metadata, location details, and usage constraints.

### 🔍 Retrieval Layer (RAG)
- Campus data is embedded and stored in a vector database
- User queries are embedded and matched using semantic similarity
- Only relevant context is retrieved to ground responses

### 🤖 Reasoning Layer
- The LLM interprets user intent and retrieved context
- Generates step-by-step, grounded responses
- Maintains conversation context for follow-up questions

### 🧪 Backend
- Flask-based API
- Handles user queries and routing
- Manages conversation state
- Integrates retrieval and reasoning pipeline

---

## 🗣️ Example Queries Supported

- 🅿️ Where can I park near Hill Center with a commuter permit?
- 🚌 Which bus should I take from Livingston to Busch?
- 📍 What is the closest bus stop to ARC?
- ⏰ Can I park in Lot 51 after 6 PM?
- 🧭 How do I go from Allison Road Classroom Building to SHI?

---

## 📈 Evaluation & Results

- ✅ Tested on 350+ real-world campus queries
- 🎯 Achieved approximately 89% accuracy
- 🧪 Covered parking rules, bus routing, and building navigation
- 🔍 Failure cases were analyzed and documented

Performance improved through dataset refinement, improved query handling, and better retrieval chunking.

---

## ⚙️ Challenges Faced and Solutions

### 🧩 Inconsistent Campus Data
Campus information was scattered and inconsistent.  
**Solution:** Manual data curation, normalization, and standardization across datasets.

### ❌ LLM Hallucinations
The model occasionally generated confident but incorrect answers.  
**Solution:** Strict RAG constraints and limiting responses to retrieved context only.

### 🔄 Multi-Turn Context Loss
Follow-up questions sometimes lost context.  
**Solution:** Implemented session-based memory and conversation history tracking.

### ❓ Ambiguous Queries
Users often asked underspecified questions.  
**Solution:** Clarification prompts and assumption handling with transparent explanations.

---

## 👥 Team Contributions

### 👨‍💻 Raj Shah – Lead AI & Backend Engineer
- 🏗️ Designed the overall system architecture
- 🔍 Implemented the Retrieval-Augmented Generation pipeline
- 🧪 Built and integrated the Flask backend
- 🧠 Implemented vector search and embeddings
- 💬 Handled multi-turn conversation logic
- 🚀 Led debugging, optimization, and performance tuning
- 📊 Coordinated dataset integration and system testing

Raj played a critical role in transforming the idea into a production-ready AI system.

### 🤝 Other Team Contributions
- 📁 Dataset collection and validation
- 🧪 Query testing and evaluation
- 👤 User interaction testing
- 📝 Documentation and reporting
- 📊 Performance analysis and error review

---

## 🚀 Future Improvements

- 📡 Real-time bus tracking integration
- 🅿️ Live parking availability
- 📱 Mobile application interface
- 🎯 Personalized recommendations
- ☁️ Cloud deployment and scalability enhancements

---

## 🏁 Conclusion

RU-PATH demonstrates how AI, structured data, and Retrieval-Augmented Generation can be combined to solve real-world campus navigation problems. By unifying parking, bus, and building information into a single conversational system, RU-PATH significantly improves accessibility, efficiency, and user experience across Rutgers University.
