import sys
import requests
from icalevents.icalevents import events
from datetime import datetime, timedelta

weekdays = ["Sonntag", "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag"]
months = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "Augsust", "September", "Oktober", "Novemer",
          "Dezember"]


class CalFetch:
    def __init__(self):
        self.current_time = None
        self.events_raw = []
        self.events = []

    def fetch(self, url_calendar, tag):
        self.current_time = datetime.now()
        untagged_events = events(url=url_calendar, end=self.current_time + timedelta(days=365))
        for event in untagged_events:
            event.tag = tag
            self.events_raw.append(event)

    def parse(self):
        # Sort list for chronological order
        self.events_raw.sort(key=lambda x: x.start.isoformat())

        date_today = self.current_time.date()
        date_tomorrow = date_today + timedelta(days=1)
        date_7_days = date_today + timedelta(days=7)

        self.events = []
        for event in self.events_raw:
            time_event_start = event.start
            time_event_end = event.end

            date_event = event.start.date()
            date_event_end = event.end.date()
            date_event_duration = time_event_end - time_event_start

            if date_today > date_event:
                description_day = str(date_event)
            elif date_today == date_event:
                description_day = "Heute"
            elif date_tomorrow == date_event:
                description_day = "Morgen"
            elif date_7_days > date_event:
                description_day = weekdays[int(time_event_start.strftime("%w"))]
            else:
                description_day = time_event_start.strftime("%d") + ". " + months[
                    int(time_event_start.strftime("%m")) - 1]

            if date_today == date_event_end:
                description_day_end = "Heute"
            elif date_tomorrow == date_event_end:
                description_day_end = "Morgen"
            elif date_7_days > date_event_end:
                description_day_end = weekdays[int(time_event_end.strftime("%w"))]
            else:
                description_day_end = time_event_end.strftime("%d") + ". " + months[
                    int(time_event_end.strftime("%m")) - 1]

            if date_event != date_event_end:
                # Check if event is a whole day-event
                if (date_event_duration == timedelta(days=1)) and (
                        time_event_start.strftime("%m/%d/%Y, %H:%M:%S") == date_event.strftime("%m/%d/%Y, %H:%M:%S")):
                        str_time = f"Ganzer Tag {description_day}"
                # Check if event is a multiple whole days-event
                elif (time_event_start.strftime("%m/%d/%Y, %H:%M:%S") == date_event.strftime(
                        "%m/%d/%Y, %H:%M:%S")) and (
                        time_event_end.strftime("%m/%d/%Y, %H:%M:%S") == date_event_end.strftime("%m/%d/%Y, %H:%M:%S")):
                    str_time = f'Ab {description_day} für {str(date_event_duration.days)} Tage'
                else:
                    str_time = f'{description_day} {time_event_start.strftime("%H:%M")} bis {description_day_end} {time_event_end.strftime("%H:%M")}'
            else:
                str_time = f'{description_day} {time_event_start.strftime("%H:%M")} - {time_event_end.strftime("%H:%M")}'

            self.events.append({'time': f'{str_time}', 'summary': event.summary, 'tag': event.tag})

    def send_to_miniserver(self):
        # Get a list of 5 upcoming events
        text_to_send = ""
        for i in range(5):
            if i < len(self.events):
                if i != 0:
                    text_to_send += "\n\n"
                text_to_send += f"{self.events[i]['time']} | {self.events[i]['summary']}"
            else:
                break
        if 0 < len(self.events):
            requests.get(f"http://USER:PASSWORD@IPADDRESS/dev/sps/io/Kalender {self.events[0]['tag']}/{text_to_send}")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Please specify a calendar url and a tag")
        exit(1)

    calendar_url = sys.argv[1]
    calendar_tag = sys.argv[2]

    cal_fetch = CalFetch()
    cal_fetch.fetch(calendar_url, calendar_tag)
    cal_fetch.parse()
    cal_fetch.send_to_miniserver()
