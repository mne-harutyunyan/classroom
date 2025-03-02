#Classrooms
🎓 Academy Classrooms Backend
This is a complete backend rebuild for academyclassrooms.com, developed using Quart (an asynchronous Python web framework) and MongoDB for efficient and scalable data management.

🚀 Project Overview
This API facilitates classroom reservations for an academic platform, providing essential functionalities for both students and administrators.

📋 User Features
View available classrooms.
Request classroom reservations.
Receive notifications via Twilio when reservation requests are approved or rejected.
🔒 Admin Features
Approve or reject classroom reservations directly via Slack.
Receive Slack notifications for new reservation requests.
Manage classroom data (Add, Edit, Delete).
🛠️ Setup & Requirements
Installation
Install dependencies:
bash
Copy
Edit
pip install -r requirements.txt
Run the server using Uvicorn:
bash
Copy
Edit
uvicorn app:app --host 0.0.0.0 --port 8000  
Use ngrok for Slack integration testing:
bash
Copy
Edit
ngrok http 8000 
