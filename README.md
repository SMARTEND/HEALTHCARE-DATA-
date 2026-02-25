# 🏥 Healthcare Performance Dashboard

> An AI-powered analytics platform for private clinics and hospitals — built with No-Code tools.

---

## 📌 Overview

The **Healthcare Performance Dashboard** is an all-in-one analytics solution that gives clinic and hospital managers a real-time, centralized view of their key performance indicators (KPIs). It features an intelligent alert system and automated weekly AI-generated reports in Arabic, designed specifically for healthcare management teams.

---

## 🎯 Problem Statement

Healthcare facilities often struggle with scattered data across multiple systems, making it difficult for managers to make fast, informed decisions. This solution consolidates everything into a single, smart interface.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 📊 **Centralized KPI Dashboard** | All key metrics in one clean interface |
| 🤖 **AI-Automated Reports** | Weekly Arabic reports generated via ChatGPT API |
| 🔔 **Smart Alerts** | Instant notifications when metrics cross critical thresholds |
| 📈 **Doctor Performance Tracking** | Monitor productivity and patient ratings per doctor |
| 😊 **Patient Satisfaction** | Track patient experience scores over time |
| 💰 **Revenue Analytics** | Monitor financial performance and revenue streams |
| ❌ **Appointment Cancellations** | Analyze cancellation and no-show rates |

---

## 🛠️ Tech Stack

```
📦 No-Code Stack
├── 🎨 Frontend    → Bolt.new / Lovable   (UI & Dashboard)
├── ⚙️  Backend    → Bubble               (App logic & database)
├── 🔄 Automation  → Make (Integromat)    (Workflows & integrations)
├── 🤖 AI Engine   → ChatGPT API          (Report generation)
└── 📊 Data        → Airtable / Google Sheets
```

---

## 📐 Solution Architecture

```
[Clinic Data Sources]
        ↓
[Make Automation Workflows]
        ↓
[ChatGPT API] ──→ [Automated Arabic Weekly Report]
        ↓
[Performance Dashboard] ──→ [Real-time Alerts to Manager]
```

---

## 🚀 Getting Started

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Moha-111/HEALTHCARE-DATA-.git
   ```

2. **Open the dashboard in your browser:**
   ```
   index.html
   ```

3. **Connect Make Automation:**
   - Add your ChatGPT API key in Make settings
   - Activate the weekly report Scenario

4. **Update your clinic settings:**
   ```
   config/clinic-settings.json
   ```

---

## 📊 Tracked KPIs

- **Appointment Cancellation Rate**
- **Patient Satisfaction Score**
- **Daily / Weekly Revenue**
- **Doctor Performance Index**
- **Average Patient Wait Time**
- **Bed / Room Occupancy Rate**

---

## 📸 Screenshots

> *(Add dashboard screenshots here)*

---

## 🗺️ Roadmap

- [x] Initial dashboard prototype
- [x] Automated AI weekly reports in Arabic
- [ ] Mobile app for managers
- [ ] Integration with HIS systems
- [ ] AI-powered predictive analytics

---

## 👥 Developers

| Name | Role |
|---|---|
| **Mohammad** | Prepare Data For Exploration |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

> 💡 *"Better data = Faster decisions = Better healthcare."*
