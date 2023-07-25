# Development Setup

### Environment Variables

- You will need to rename the .env.example files in the bot, frontend, and backend directory
    -  "*cp .env.example .env*"

    - these hold information that will be required by the bot:
        - backend url
        - frontend url
        - database information


### Running the Bot
- Note that you will need docker running (docker desktop) before running the command below.
- Running the command "*docker-compose up --build -d*" in the root directory should start up everything needed to get the bot started
    - You should have 4 docker images running on docker desktop after running the command 


# Directory Information

### Backend
- Has the information for the database and the api endpoints used to connect the frontend/discord bot to the database
<br/> <br/>
- The file *backend/api/views.py* has the information on what each endpoint does
- The file *backend/api/urls.py* has the endpoint urls that will be used by the other components of the project
- The file *backend/api/models.py* has the database table defintions
    - If you make changes to the models, you will need to run the commands `$ python manage.py makemigrations` and `$ python manage.py migrate` to update the database
    - Type `python manage.py createsuperuser` to create a superuser for the database
    - If you are using docker
      - Enter into the container `$ docker exec -it backend /bin/sh` or `$ docker exec -it {CONTAINER_ID} /bin/sh`
      - You can get the container id by typing `$ docker ps`
      - Run the commands above
      - Type `exit` to exit the container shell



### Frontend
- Has the code for the frontend section of the discord bot
- All relavent source files are in the directory *frontend/src/pages*


### Bot
- Has the code for the discord bot itself
- The file "*bot/discordbot.py*" has the code for the discord bot
- To start the bot by itself, you can run the command "*python discordbot.py*"
