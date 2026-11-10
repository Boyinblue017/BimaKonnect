# BimaKonnect 

**An AI-Powered Insurance Literacy Assistant for Africa**

BimaKonnect is an AI-powered insurance literacy platform designed to simplify insurance education and improve financial inclusion across Africa. The platform helps users understand insurance products through conversational interactions available on web, mobile, SMS, and USSD channels.

Our mission is to make insurance accessible, understandable, and approachable for individuals who are underserved or excluded from traditional insurance systems.

---

## Problem Statement

Insurance penetration in Africa remains critically low due to several challenges:

* Limited awareness and understanding of insurance products.
* Complex policy terms and conditions.
* Lack of trust in insurance providers.
* Limited access to insurance education, especially in rural and informal sectors.
* Low digital and financial literacy.

Millions of individuals, farmers, SMEs, and informal workers remain uninsured because they do not fully understand how insurance works or why it matters.

---

## Solution

BimaKonnect addresses these challenges by providing an intelligent, user-friendly platform that:

* Explains insurance concepts in simple language.
* Recommends suitable insurance products based on user needs.
* Provides an insurance glossary and educational resources.
* Offers insurance assistance through SMS and USSD for users without smartphones.
* Supports multilingual interactions to increase accessibility.

---

## Key Features

### AI Insurance Assistant

A conversational chatbot that answers insurance-related questions in plain language.

**Example:**

**User:** What is motor insurance?

**BimaKonnect:** Motor insurance protects you financially if your vehicle is involved in an accident, stolen, or damaged.

---

### Insurance Recommendation Quiz

A simple questionnaire that recommends appropriate insurance products based on the user's profile.

Recommendations may include:

* Health Insurance
* Motor Insurance
* Agricultural Insurance
* Life Insurance
* SME Insurance

---

### Insurance Glossary

A searchable dictionary that explains common insurance terms such as:

* Premium
* Deductible
* Beneficiary
* Claim
* Underwriting

---

### SMS and USSD Support

Users can access insurance information through:

* SMS
* USSD

This ensures accessibility for users with limited internet connectivity or non-smartphone devices.

---

### Multilingual Support (Planned)

Support for:

* English
* Swahili
* Additional local languages in future releases

---

## Target Users

* Informal workers
* Boda boda riders
* Smallholder farmers
* Small and Medium Enterprises (SMEs)
* Students and young professionals
* Low-income households
* Individuals seeking insurance information

---

## Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript

### Backend

* Python
* Flask

### Database

* SQLite

### APIs

* Africa's Talking SMS API
* Africa's Talking USSD API

### Deployment

* Render

---

## Project structure

```text
.
├── backend/
│   ├── app.py
│   ├── data/
│   ├── routes/
│   └── services/
├── frontend/
│   ├── src/                 # Tailwind CSS source
│   ├── static/
│   │   ├── css/             # Stylesheets served by Flask
│   │   └── js/              # Browser scripts served by Flask
│   └── templates/           # Jinja HTML pages
├── tests/
│   ├── api.http             # Manual API requests
│   └── test_mvp.py          # Automated backend tests
├── documents/               # Project reference documents
├── package.json             # Frontend build tooling
├── requirements.txt         # Python dependencies
├── render.yaml              # Render deployment configuration
└── README.md
```

---

## Minimum Viable Product (MVP)

The current MVP includes:

* A responsive, single-page web experience served by Flask.
* A plain-language assistant for health, motor, life, crop, and small-business insurance, including simple Swahili prompts.
* A transparent needs quiz that explains why each cover is worth exploring.
* A searchable insurance glossary with everyday examples.
* A claims guidance wizard with safety-first next steps and tailored document checklists for motor, health, crop, SME, and life cover.
* Required email/password accounts, with password hashes stored in SQLite and authenticated access to the learning tools.
* A directory of admin-managed insurance specialists with public contact profiles and one editable 1–5-star rating per signed-in user and specialist.
* A health endpoint suitable for deployment monitoring.

The assistant is educational by design: it does not generate policy quotes, determine eligibility, or replace a licensed insurance professional.

## Privacy

BimaKonnect stores account email addresses, password hashes, and account creation times. Specialist profiles include public contact details, and ratings are associated with the rating user's account. It does not deliberately store submitted chat questions, quiz answers, or claims-guide selections in an application database. Email verification and user password reset are not yet available. Users should not submit sensitive personal, medical, financial, policy, or identity information. Read the full [Privacy Policy](frontend/templates/privacy.html) before using or deploying the service.

Before public launch, replace the placeholder privacy contact in the policy, identify the production hosting provider, and obtain a legal review for each country where BimaKonnect operates. The policy is not legal advice.

## Run locally

From the project root, activate the included virtual environment (or create your own), then run either command:

```bash
pip install -r requirements.txt
python -m backend.app
```

Open [http://localhost:5000](http://localhost:5000). The API health check is available at `/api/health`.
The app creates its SQLite account database at `backend/instance/bimakonnect.sqlite3` by default. Set `SECRET_KEY` to a stable, private value when running outside local development; set `BIMAKONNECT_DATABASE` to the desired SQLite file path if needed.
To provision the initial administrator, set `ADMIN_EMAIL` and `ADMIN_PASSWORD` before starting the app. Use a unique password of at least 12 characters. If the email already belongs to an account, startup promotes that account to administrator and retains its current password. Administrators can add specialists at `/admin/specialists`; specialists should change the temporary password and maintain their profile at `/specialist/account`.

## Frontend assets

HTML pages live in `frontend/templates`; Flask-served assets live in `frontend/static/css` and `frontend/static/js`. The dashboard uses Tailwind CSS. After changing utility classes in templates or JavaScript, run `npm install` and `npm run build:css` to rebuild `frontend/static/css/tailwind.css`. Phosphor icons are loaded from jsDelivr.

Run automated tests from the repository root with `python -m unittest discover -s tests`. Manual API requests are in `tests/api.http`; the protected POST requests require a signed-in session cookie and its matching CSRF token.

## Deployment

The included `render.yaml` deploys the app to Render with `gunicorn backend.app:app`, creates a secret session key, enables secure cookies, and monitors `/api/health`. Configure `ADMIN_EMAIL` and `ADMIN_PASSWORD` as private Render environment variables to provision the first administrator. SQLite data on Render's default filesystem is ephemeral; before accepting real accounts, attach persistent storage and set `BIMAKONNECT_DATABASE` to a database file on that storage. Account verification, regular-user password reset, and account deletion are not yet self-service features.

## Recommended next milestones

1. Add a verified product catalogue from participating insurers, with country-specific wording and effective dates.
2. Integrate Africa's Talking SMS/USSD after credentials, a callback URL, and the desired menu flow are defined.
3. Add human handoff and consent-based analytics; do not collect sensitive health or financial details in the chat.
4. Have licensed local insurance partners review all educational content before a public launch.

---

## Future Enhancements

* Voice assistant integration
* Advanced AI recommendation engine
* WhatsApp integration
* Personalized insurance dashboards
* Premium calculators
* Claims guidance assistant
* Additional language support

---

## Social Impact

BimaKonnect aims to:

* Increase insurance literacy across Africa.
* Improve financial inclusion for underserved communities.
* Build trust in insurance products.
* Enable informed decision-making.
* Expand access to insurance education through low-cost digital channels.

---

## Hackathon Goals

* Build a functional and scalable MVP.
* Demonstrate the use of Africa's Talking APIs.
* Promote financial inclusion through technology.
* Deliver an impactful solution tailored to African insurance challenges.

---

## Team Vision

**"Insurance should not be complicated. Everyone deserves to understand and access financial protection regardless of income, education level, or location."**

BimaKonnect exists to bridge the insurance knowledge gap and empower Africans to make informed decisions about their financial security.

---

## License

This project is currently developed for educational and hackathon purposes. Future licensing terms will be determined as the project evolves.
