This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import requests

baseURL = 'http://www.thebluealliance.com/api/v3/'
header = {'X-TBA-Auth-Key':'rlFzEcoS3n28Du8MdTr6VLNOfZ25HpYoOgZQITWpLGjsqKW00YvJiIFdUNdc6O6H'} 
s = requests.Session() 

# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the FRC Team tool. " \
                    "Please ask for information about a team by saying, " \
                    "Give me information about team 253"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please ask for information about a team by saying, " \
                    "Give me information about team 253"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()
    
def getTBA(url): #uses TBA API to get data in python native type
    return s.get(baseURL + url, headers=header).json()

def getTeamInfo(num, info_key): #generic method to pull team-specific information
    return getTBA("team/frc" + str(num))[info_key]

def getTeamName(num): #returns the name from the teamnumber
    return getTeamInfo(num, 'nickname')
    
def getLocation(num): #returns the location of a team as a string, ignoring data that is null
    address = getTeamInfo(num, 'address')
    city = getTeamInfo(num, 'city')
    state_prov = getTeamInfo(num, 'state_prov')
    country = getTeamInfo(num, 'country')
    postal_code = getTeamInfo(num, 'postal_code')


    location = [address, city, state_prov, country, postal_code]

    #Creates a list of each element of location if they are not null
    finalLocationList = []
    for loc in location:
        if loc != None:
            finalLocationList.append(loc)
    
    #Creates a string from list, with proper commas
    finalLocationString = ''
    for loc in finalLocationList: 
        finalLocationString += loc
        if finalLocationList.index(loc) != len(finalLocationList)-1:
            finalLocationString += ", "
    
    return finalLocationString
    
def getMotto(num): #Returns team motto
    return getTeamInfo(num, 'motto')
    
def text2int(textnum, numwords={}):
    if not numwords:
      units = [
        "zero", "one", "two", "three", "four", "five", "six", "seven", "eight",
        "nine", "ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen",
        "sixteen", "seventeen", "eighteen", "nineteen",
      ]

      tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"]

      scales = ["hundred", "thousand", "million", "billion", "trillion"]

      numwords["and"] = (1, 0)
      for idx, word in enumerate(units):    numwords[word] = (1, idx)
      for idx, word in enumerate(tens):     numwords[word] = (1, idx * 10)
      for idx, word in enumerate(scales):   numwords[word] = (10 ** (idx * 3 or 2), 0)

    current = result = 0
    for word in textnum.split():
        if word not in numwords:
          raise Exception("Illegal word: " + word)

        scale, increment = numwords[word]
        current = current * scale + increment
        if scale > 100:
            result += current
            current = 0

    return result + current


def teamInfo(intent, session):
    card_title = intent['name']
    teamNum = intent['slots']['teamNum']['value']
    
    try:
        teamNum = text2int(teamNum, len(teamNum));
    except TypeError:
        pass
    session_attributes = {}
    should_end_session = False
    
    speech_output = "Team "+ teamNum + " is named " + getTeamInfo(teamNum, 'nickname') +". " + "They are located in " + getLocation(teamNum) + " and their motto is " + getMotto(teamNum)
    reprompt_text = "Sorry, I didn't get that. Give me a team number again."
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    
def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Dispatch to your skill's intent handlers
    if intent_name == "GetTeam":
        return teamInfo(intent, session)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    '''if (event['session']['application']['applicationId'] !=
             "amzn1.echo-sdk-ams.app.[unique-value-here]"):
         raise ValueError("Invalid Application ID")'''

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    '''elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])'''