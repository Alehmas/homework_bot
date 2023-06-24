#  Telegram bot to control the status of homework

##  Description
Telegram bot that calls the Praktikum.Homework API service and finds out the status of your homework:
whether your homework was reviewed, whether it was checked, and if it was checked,
then the reviewer accepted it or returned it for revision.

##  Technologies used
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![Telegram](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)

##  Functionality
The bot can:
- polls the Praktikum.Homework API service every 10 minutes and checks the status 
of the homework submitted for review
- when updating the status, it analyzes the API response and sends you a corresponding 
notification in Telegram
- logs its work and informs you about important problems with a message in Telegram

##  Running the project locally
- Clone repository
```
git@github.com:Oleg-2006/homework_bot.git
```
- Change to new directory
```
cd homework_bot/
```
- Initialize virtual environment
```
python -m venv venv
```
- Activate virtual environment
```
source venv/Scripts/activate
```
- Install project dependencies
```
pip install -r requirements.txt
```
- Setting environment variables
Create an .env file in which to register identifiers and tokens for working with 
the Telegram API and Yandex.Domashka:
    * Specify your service token Praktikum.Home
    ```
    PRACTICUM_TOKEN=<PRACTICUM_TOKEN>
    ```
    * Specify the API token of the Telegram bot. (Use @BotFather in Telegram to create a new bot and get API TOKEN)
    ```
    TELEGRAM_TOKEN=<API TOKEN>
    ```
    * Specify the Telegram ID to which the bot will send messages (check with @userinfobot):
    ```
    TELEGRAM_CHAT_ID=<TELEGRAM_CHAT_ID>
    ```
- In the root directory, run the command to start the bot
```
python homework.py
```
##  Running the project on the server
the example uses Heroku hosting
- Register on Heroku
- Create an application (button New → Create new app).
  Come up with and enter a name for the application.
  Select a region that is geographically close to you.
- Now link your Heroku account to GitHub: in the Heroku interface go to the Deploy
  section, in the Deployment method section, select GitHub and click on the Connect 
  to GitHu button to link accounts, you will be prompted to authenticate through GitHub.
  Then, in the window that opens, specify the name of the repository where the code is located.
  It remains only to click on the Deploy Branch button:
  Heroku will install all the dependencies and publish the application on the server.
  In order for everything to start, two service files need to be placed in the repository:
    - **requirements.txt** with a list of dependencies so Heroku knows what packages it needs to install;
    - the **Procfile** file, which must contain the "entry point" - the file that must be executed to start the project.

- Add `PRACTICUM_TOKEN`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`
  You can add environment variables manually in the Heroku settings, in the Settings → Config Vars section

- Start the bot. Go to the Resources tab and activate the switch opposite the
  worker python homework.py line. To do this, click on the pencil icon to the right of the switch, 
  activate the switch and confirm the action by clicking on the Confirm button that appears.

[An example](https://github.com/heroku/python-sample) of hosting a project on Heroku is available.
Detailed instructions are in [documentation](https://devcenter.heroku.com/categories/deployment)

##  Description of functions
- `main()` it describes the main logic of the program.
All other functions run .ncz from it.
The sequence of actions is as follows:
    - Make a request to the API.
    - Check the answer.
    - If there are updates, get the work status from the update and send a message to Telegram.
    - Wait a while and make a new request.

- `check_tokens()` checks the availability of environment variables that are necessary for the program to work. 
If at least one environment variable is missing, the function returns False, otherwise True.

- `get_api_answer()` makes a request to a single API service endpoint.
The function receives a timestamp as a parameter.
If the request is successful, returns the API response, converting it from JSON format to Python data types.

- `check_response()` checks the API response for correctness.
As a parameter, the function receives an API response cast to Python data types.
If the API response matches expectations, then the function returns a list of homework (it can be empty),
available in the API response with the key 'homeworks'.

- `parse_status()` extracts the status of this work from information about a particular homework.
As a parameter, the function receives only one element from the list of homework.
If successful, the function returns a string prepared for sending to Telegram,
containing one of the verdicts of the HOMEWORK_STATUSES dictionary.

- `send_message()` sends a message to the Telegram chat specified by the TELEGRAM_CHAT_ID environment variable.
It takes two parameters as input: an instance of the Bot class and a string with the message text.

## Logging
Logged events:
- lack of required environment variables during bot launch (**CRITICAL** level)
- successful sending of any message to Telegram (**INFO** level)
- crash when sending a message to Telegram (**ERROR** level)
- unavailability of https://practicum.yandex.ru/api/user_api/homework_statuses/ endpoint (**ERROR** level)
- any other failures when requesting an endpoint (**ERROR** level)
- lack of expected keys in the API response (**ERROR** level);
- undocumented homework status found in API response (**ERROR** level);
- absence of new statuses in the response (**DEBUG** level).

Events of the ERROR level are not only logged, but information about them is also sent to your Telegram in those cases
when it is technically possible (if the Telegram API stops responding or when the program starts, there is no
the desired environment variable - nothing will be sent).

## Authors
- [Aleh Maslau](https://github.com/Oleg-2006)