#!/bin/python

import datetime
import os

# Include variables in the readme so that every commit can be "unique"
# They can be expanded as your wish

# Start the variable script
input_string = os.getenv("INPUT_COMMIT_MESSAGE")
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

# Define a dictionary with placeholders and their corresponding values
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

# Iterate over the placeholders and replace them in the input string
u_message = input_string
for placeholder, value in placeholders.items():
    u_message = u_message.replace(f"``{placeholder}``", str(value))
    

print(u_message)

# End the variable script