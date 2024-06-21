# Development Setup

### Environment Variables

- You will need to COPY and RENAME the .env.example files in the following directories:
    - /bot
    - /frontend
    - /backend 
    - and the root directory
        -  Use `cp .env.example .env`

    - These hold information that will be required by the bot:
        - backend url
        - frontend url
        - database information


### Running the Bot
- Note that you will need docker running (docker desktop) before running the command below.
- Running the command `docker-compose -f docker-compose.dev.yml up --build -d` in the root directory should start up everything needed to get the bot started.
- Alternatively, you can run `./app.sh start dev` if you are on a Mac or Linux PC. If `./app.sh start dev` does not work, type `chmod 0755 app.sh`, then `./app.sh start dev`
    - You should have 4 docker images running on docker desktop after running the command 


# Directory Information

### Backend
- Has the information for the database and the api endpoints used to connect the frontend/discord bot to the database
<br/> <br/>
- The file *backend/api/views.py* has the information on what each endpoint does
- The file *backend/api/urls.py* has the endpoint urls that will be used by the other components of the project
- The file *backend/api/models.py* has the database table definitions
    - If you make changes to the models, you will need to run the following commands:
        - `$ python manage.py makemigrations` and then
        - `$ python manage.py migrate` to update the database
    - Type `python manage.py createsuperuser` to create a superuser for the database
    - If you are using docker
      - Enter into the container `$ docker exec -it {CONTAINER_ID} /bin/sh`
      - You can get the container ID by typing `$ docker ps`
      - Run the `python` commands above
      - Type `exit` to exit the container shell



### Frontend
- Has the code for the frontend section of the discord bot
- All relevant source files are in the directory *frontend/src/pages*


### Bot
- Has the code for the discord bot itself
- The file *bot/discordbot.py* has the code for the discord bot
- To start the bot by itself, you can run the command `python discordbot.py`
