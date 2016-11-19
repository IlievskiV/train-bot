import time
from slackclient import SlackClient

BOT_ID = 'U34T5FLKX'
AT_BOT = "<@" + BOT_ID + ">"

# instantiate Slack & Twilio clients
slack_client = SlackClient('xoxb-106923530677-P2QYlS5doMvGmL4ZxzaSJPVP')


def check(response):
    if len(response) == 2:
        data = []
        if response[0] == '':
            data = [x.strip() for x in response[1].strip().split(" ")]
            print(data)
        elif response[1] == '':
            data = [x.strip() for x in response[0].strip().split(" ")]
        if len(data) == 3:
            return True
    return False


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    if command is None:
        response = {
            'answer': "Hey, you talkin' about me? If you need my help, don't mention me in the middle of your sentence."}
    else:
        response = {'answer': "Bojan i Vladimir rabotat uste, nabrzo se gotovi"}
        if 'error' in response:
            response = {'answer': "I don't see what you are talking about. Please send me existing data."}

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
                if check(splitted_array):
                    return splitted_array, output['channel']
                return None, output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1  # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if channel:
                print(channel, ": ", command)
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
