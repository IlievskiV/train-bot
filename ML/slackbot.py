import time
from slackclient import SlackClient
import pyowm
from ML.predict import *

BOT_ID = 'U34T5FLKX'
AT_BOT = "<@" + BOT_ID + ">"
EXPECTED_FORMAT = "Departure city, Arrival city, hh:mm"

# instantiate Slack & Twilio clients staff to be moved in env vars
slack_client = SlackClient('xoxb-106923530677-7Kr3xs08MZao1VTvbFSskiRU')
owm = pyowm.OWM('e67357c59746fa7f54d5d4fb8c7b1755')


def check(response):
    if len(response) == 2:
        data = []
        if response[0] == '':
            data = [x.strip() for x in response[1].strip().split(',')]
            print(data)
        elif response[1] == '':
            data = [x.strip() for x in response[0].strip().split(',')]
        if len(data) == 3:
            time = data[2].split(':')
            if len(time) == 2 and 0 <= int(time[0]) < 24 and 0 <= int(time[1]) < 60:
                return data
    return None


def weather(city):
    """
    :param city: city for which we need the weather, it
    need to be of the format city,{country code}
    Returns the weather status in lower case
    """
    observation = owm.weather_at_place(city)
    w = observation.get_weather().get_detailed_status().lower()
    return w


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    if command is None:
        response = {
            'answer': "Hey, you talkin' about me? If you need my help, don't mention me in the middle of your sentence. And remember your question should be of the form: " + EXPECTED_FORMAT}
    else:
        # place holder, the prediction function should be called here
        time = command[2].split(':')
        response = {'answer': ''}
        response['answer'] = predit(command[0], command[1], time[0], time[1])
        # if the input was not correct it should inform the client
        if 'error' in response:
            response = {'answer': "I don't see what you are talking about. Please send me existing data."}
        response['answer'].append(" It is good to know that at " + command[1] + \
                            " you can expect " + weather(command[1]+",ch")+".")

    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response['answer'], as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                splitted_array = output['text'].split(AT_BOT)
                data = check(splitted_array)
                return data, output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
