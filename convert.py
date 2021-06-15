import csv
import datetime
import dateutil.parser
import ics
from pprint import pprint as print

def main():
    table = import_csv("revue_schedule.csv")
    table = strip_table(table)
    events = table_to_objects(table)
    events = filter_events(events)
    ics_events = make_events_list(events)
    make_calendar(ics_events)

def make_calendar(events):
    calendar = ics.icalendar.Calendar(
        events=events
    )
    with open("schedule.ics", "w") as f:
        f.writelines(calendar)

def dict_to_event(event:dict[str,str]):

    start_time, end_time = parse_datetime(event["date"], event["time"])
    print(f"{start_time}  {end_time}")
    event = ics.event.Event(
        name=event["title"],
        begin=start_time,
        end=end_time,
        location=event["location"]
    )

    return event

def make_events_list(event_list:list[dict[str,str]]):

    ics_event_list = []
    for event in event_list:
        ics_event_list.append(dict_to_event(event))

    return ics_event_list

# Get CSV into my program
def import_csv(filename:str):
    table = []
    
    with open(filename, newline='') as csvfile:
        spamreader = csv.reader(csvfile)
        for row in spamreader:
            # Convert into 2D Array
            table.append(row)
    
    return table

""" 
Stripping 2D array
Remove the 1st row and column which contain weeks and days
"""
def strip_table(table:list[list[str]]):
    stripped_table = []
    for row in table[1:]:
        stripped_table.append(row[1:])

    # Adjusting for if location doesn't exist in last row
    stripped_table.append(["" for _ in range(len(row))])

    return stripped_table

""" 
# Loop through to get specific blocks -> dicts

"""
def table_to_objects(table:list[list[str]]):
    # col 0..6
    # week = num_rows / 4
    events = [] 
    for row in range(0,len(table),4):
        for col in range(0,6):
            events.append(index_to_event_dict(row, col, table))
    return events

# Go fn index -> returns dict
def index_to_event_dict(row:int, col:int, table:list[list[str]]):
    return {
        "date": table[row][col],
        "title": table[row + 1][col],
        "time": table[row + 2][col],
        "location": table[row + 3][col],
    }

# Filter the events removing those time
def filter_events(events:list[dict[str,str]]):
    return [
        event 
        for event in events 
        if event["time"]
    ]

def parse_datetime(date:str, time:str):
    """
    6 - 9:30
    6 - 11
    11 - 6
    12 - 5
    5 - Late
    31-May
    6-Nov
    """
    # Given 6 - 9:30
    # return two string with AM or PM added
    start_time, end_time = parse_time(time)

    # Get both start and end datetime
    # By appending date to both strings
    # and converting with datetime
    start_datetime = dateutil.parser.parse(f"{start_time} {date}")
    end_datetime = dateutil.parser.parse(f"{end_time} {date}")

    # year = datetime.date.today().year
    # date = date.replace(year=year)
    
    return start_datetime, end_datetime

def parse_time(time:str):
    """
    6 - 9:30
    6 - 11
    11 - 6
    12 - 5
    5 - Late
    """
    
    start_time, end_time = time.strip().split(" - ")
    is_AM = determine_am(start_time, end_time)
    print(f"LATE {start_time} {end_time}")
    start_time = append_period(start_time, is_AM)
    if end_time in ["Late","12"]:
        end_time = "11:59PM"
    else:
        end_time = append_period(end_time)

    return start_time, end_time

# Assuming only numerical or colon hours
def determine_am(start_time:str, end_time:str):
    # Always assume if end_time is late, start_time is PM
    # i.e. no event will start 11am and go till Late
    if end_time == "Late":
        return False
    
    start_hour = int(start_time.split(":")[0])
    end_hour = int(end_time.split(":")[0])
    return (
        end_hour < start_hour
        and start_hour != 12
    )

# is_AM true -> Append AM
def append_period(time:str, is_AM:bool=False):
    if(is_AM):
        time += "AM"
    else:
        time += "PM"
    return time

# Go through dicts converting to ics
# Handle events with no time

if __name__ == "__main__":

    main()
