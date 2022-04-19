from datetime import datetime
import requests
from time import sleep
from twilio.rest import Client

ppl = {
    'Matthew': ['+14049529090', 'Computer Science'],
    'Ayusha': ['+16784283991', 'Biomedical Engineering'],
    'MatthewTest': ['+14049529090', 'Biomedical Engineering'],
}

courses = [
    {
        'name': 'CS 2050 B',
        'CRN': '83730',
        'numbers': ['Matthew']
    },
    {
        'name': 'CS 2340 B',
        'CRN': '81106',
        'numbers': ['Matthew']
    },
    {
        'name': 'MATH 3012 L',
        'CRN': '92973',
        'numbers': ['Matthew']
    },
    {
        'name': 'BME 4853 A01',
        'CRN': '89604',
        'numbers': ['MatthewTest', 'Ayusha']
    },
    {
        'name': 'CS 1331',
        'CRN': '88376',
        'numbers': ['MatthewTest', 'Ayusha']
    },
    {
        'name': 'MATH 3406 G',
        'CRN': '86134',
        'numbers': ['Matthew']
    }
]

url = 'https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched?term_in=202208&crn_in={0}'

def send_message(number, message):
    account_sid = "AC5a1c9806af603885451a3e3e38f79a9f"
    auth_token = "6c0fe1d119f627a495b1320ac02028b1"
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        to=number,
        from_="+18336113049",
        body=message)
    print(message.sid)

prev_remaining = [[1, 1, []] for _ in courses]
iter = 0
while True:
    if iter % 30 == 0:
        print(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    iter += 1
    try:
        sleep(20)
        for (i, course) in enumerate(courses):
            req = requests.get(url.format(course['CRN']))
            if req.status_code == 200:
                lines = req.text.split('\n')
                result = {'Majors': []}
                seats_start = lines.index('<th CLASS="ddlabel" scope="row" ><SPAN class="fieldlabeltext">Seats</SPAN></th>')
                waitlist_start = lines.index('<th CLASS="ddlabel" scope="row" ><SPAN class="fieldlabeltext">Waitlist Seats</SPAN></th>')
                if 'Must be enrolled in one of the following Majors:&nbsp; &nbsp; &nbsp; ' in lines:
                    major_restrict_start = lines.index('Must be enrolled in one of the following Majors:&nbsp; &nbsp; &nbsp; ')
                    major_restrict_end = lines.index('Must be enrolled in one of the following Campuses:&nbsp; &nbsp; &nbsp; ')
                    result['Majors'] = [lines[i].split('; ')[-1] for i in range(major_restrict_start + 2, major_restrict_end, 2)]
                result['capacity'] = int(lines[seats_start + 1].split('<td CLASS="dddefault">')[1].split('</td>')[0])
                result['actual'] = int(lines[seats_start + 2].split('<td CLASS="dddefault">')[1].split('</td>')[0])
                result['remaining'] = result['capacity'] - result['actual']
                result['WL capacity'] = int(lines[waitlist_start + 1].split('<td CLASS="dddefault">')[1].split('</td>')[0])
                result['WL actual'] = int(lines[waitlist_start + 2].split('<td CLASS="dddefault">')[1].split('</td>')[0])
                result['WL remaining'] = result['WL capacity'] - result['WL actual']
                for number in course['numbers']:
                    major = ppl[number][1]
                    can_enroll = major in result['Majors'] or result['Majors'] == []
                    if result['remaining'] > 0 and prev_remaining[i][0] == 0 and can_enroll:
                        send_message(ppl[number][0], 'Seats have opened up for {0}! Seats remaining: {1}'.format(course['name'], str(result['remaining'])))
                    if result['WL remaining'] > 0 and prev_remaining[i][1] == 0 and can_enroll:
                        send_message(ppl[number][0], 'Waitlist seats have opened up for {0}! Seats remaining: {1}'.format(course['name'], str(result['WL remaining'])))
                    if can_enroll and not (major in prev_remaining[i][2] or prev_remaining[i][2] == []):
                        send_message(ppl[number][0], 'Major restrictions have been lifted for {0}!'.format(course['name']))
                prev_remaining[i][0] = result['remaining']
                prev_remaining[i][1] = result['WL remaining']
                prev_remaining[i][2] = result['Majors']
            else:
                print('Error: ' + str(req.status_code))
    except Exception as e:
        print(e)