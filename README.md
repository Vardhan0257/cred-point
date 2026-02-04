# Cybersecurity CPE Tracker

A web application built with Flask and Firebase/Firestore to help cybersecurity professionals track Continuing Professional Education (CPE) points for certifications such as CEH, (ISC)², and others. 

---

## Collaboration Note:
This is a collaborative project built by  Maddilavan Indraneeli Vardhan (https://github.com/Vardhan0257) and Jaladi Sravya (https://github.com/Sravya0605).  
Main repo: [https://github.com/Vardhan0257/cred-point](https://github.com/Vardhan0257/cred-point)


## Features

- **Event Submission:** Users can enter event details, upload proof of attendance, and specify the CPE credits awarded.
- **CPE Progress Tracking:** Monitor accumulated points against certification renewal requirements.
- **Renewal Countdown:** Displays the time remaining until the next certification renewal date.
- **Recommendations:** Personalized suggestions for gaining remaining CPE credits.
- **Newsletter Page:** Lists cybersecurity events that do not offer CPE credits but may be of interest.
- **CPE Credit Estimation (Planned):** Potential integration with certification bodies' guidelines to automatically allot CPE credits based on event type and criteria.
- **Export Reports:** Generate CSV and PDF reports of your CPE activities and certifications.

---

## Tech Stack

- **Backend:** Flask (Python)
- **Database:** Firebase Firestore
- **Frontend:** HTML, CSS, JavaScript (Flask templating)
- **Authentication:** Firebase Authentication (if applicable)
- **PDF Generation:** ReportLab
- **Hosting:** Compatible with any WSGI server (e.g., Gunicorn)

---

## Getting Started

### Prerequisites

- Python 3.8+
- Firebase account with Firestore and Authentication configured
- Flask installed (`pip install flask`)
- Firebase Admin SDK (`pip install firebase-admin`)

### Installation

1. Clone this repository:
   git clone https://github.com/<your-username>/CPECreditTracker.git
   cd CPECreditTracker

2. Create and activate a virtual environment
    python -m venv venv
    source venv/bin/activate
            or
    source venv\Scripts\activate (windows)

3. Install dependencies:
    pip install -r requirements.txt

4. Set up Firebase:
- Create a Firebase project
- Enable Firestore and Authentication as needed
- Download Firebase Admin SDK credentials JSON file and save it in the project directory (e.g., `firebase_credentials.json`)

5. Configure environment variables or update the app configuration:
    Ensure the app knows where to find the Firebase credentials:
    bash: export GOOGLE_APPLICATION_CREDENTIALS="firebase_credentials.json"
    Or update the path in firebase_config.py.

### Running the Application

1. Start the Flask server:
    bash: flask run or python app.py

2. Access the app at `http://localhost:5000`

---

## Usage

- Register/login (if authentication is implemented).
- Add and manage certifications with required CPE details.
- Submit cybersecurity events and upload proof documents.
- Track your progress towards certification renewal.
- Generate reports (CSV/PDF) for submission or record-keeping.
- Explore the newsletter page for upcoming non-CPE cybersecurity events.

---

## Screenshots

**Dashboard**  
![Dashboard](screenShots/dashboard.png)

**Certifications Page**  
![Certifications](screenShots/certifications.png)

**Add Certifications**  
![Add Certifications](screenShots/add_certification.png)

**Recommendations**  
![Recommendations](screenShots/recommendations.png)

**Add Recommendations**  
![Add Recommendations](screenShots/add_recommendations.png)

**My Recommendations**  
![My Recommendations Page](screenShots/my_recommendations_page.png)

**Add Activities**  
![Add Activities](screenShots/add_activities.png)

**Newsletter**  
![Newsletter](screenShots/newsletter.png)

---

## Contribution

Contributions and suggestions are welcome! Please read our Contribution Guidelines before submitting a pull request.

---

## License

This project is open source and available under the MIT License.

---

## Contact

For questions or collaboration inquiries, please reach out via vardhanm0257@gmail.com or jaladisravya7@gmail.com or visit the GitHub repository.

---

## Acknowledgments

- Inspired by the need to simplify CPE tracking for cybersecurity professionals.
- Thanks to the Firebase team.
