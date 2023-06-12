#!/bin/python

import datetime
import os

def generate_commit_message(input_string):
    now = datetime.datetime.now()
    current_date = now.strftime("%a %d %b %Y %H:%M:%S")

    full_year = now.strftime("%d %b %Y")
    full_time = now.strftime("%a %H:%M:%S")
    year = now.year
    month_no = now.month
    month_name = now.strftime("%B")
    day_no = now.day
    day_name = now.strftime("%A")
    minute = now.minute
    hour = now.hour
    my_username = os.getenv("INPUT_USERNAME")

    placeholders = {
        "date": current_date,
        "year": year,
        "month_name": month_name,
        "month_no": month_no,
        "day_name": day_name,
        "day_no": day_no,
        "minute": minute,
        "hour": hour,
        "username": my_username,
        "full_year": full_year,
        "full_time": full_time,
    }

    u_message = input_string
    for placeholder, value in placeholders.items():
        u_message = u_message.replace(f"``{placeholder}``", str(value))

    return u_message
