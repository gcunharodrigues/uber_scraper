# Import the datetime and timedelta objects from the datetime module.
from datetime import datetime, timedelta


def generate_week_ranges(start_date, end_date):
    week_ranges = []  # Initialize an empty list to store the week ranges.
    # Ensure start_date is a datetime object
    if not isinstance(start_date, datetime):
        # Convert start_date to datetime object if it's a string.
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    # Ensure end_date is a datetime object
    if not isinstance(end_date, datetime):
        # Convert end_date to datetime object if it's a string.
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Calculate the number of weeks
    # Calculate the difference between end_date and start_date.
    delta = end_date - start_date
    num_days = delta.days  # Get the number of days in the delta.
    # Calculate the number of weeks, adding 1 to account for partial weeks.
    num_weeks = (num_days // 7) + 1

    # Find the first Monday
    # Calculate the start date of the first week (Monday).
    start_of_first_week = start_date - timedelta(days=start_date.weekday())

    for i in range(num_weeks):  # Iterate through the number of weeks.
        # Calculate the start date of the current week.
        start_of_week = start_of_first_week + timedelta(weeks=i)
        # Calculate the end date of the current week.
        end_of_week = start_of_week + timedelta(days=7)
        # Format the week range as a string.
        week_range = f"{start_of_week.strftime('%b %d, %Y')} - {end_of_week.strftime('%b %d, %Y')}"
        # Add the formatted week range to the list.
        week_ranges.append(week_range)
    return week_ranges  # Return the list of week ranges.
