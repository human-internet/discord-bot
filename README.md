# discord-bot

# Development
#### Backend directory
To start up the backend, ensure you have docker installed and runnning:
  Note that servers will need to specify their client id and secret
    There is one default server implemented in the backend (the discord test server)
  1) cp .env.example .env (run once on setup only)
  2) docker-compose up -d
  3) python manage.py migrate (run once on setup only)
  4) python manage.py runserver

#### Frontend directory
To start up the frontend:
  1) cp .env.example .env (run once on setup only)
  2) npm install (run once on setup only)
  3) npm start

#### Bot directory
To start up the discord bot:
  1) cp .env.example .env (run once on setup only)
  2) pip install -r requirements.txt (run once on setup only)
  3) python discordbot.py
