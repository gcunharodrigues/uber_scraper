from datetime import datetime, timedelta

# Function to generate list of week ranges


def generate_week_ranges(start_date, num_weeks):
    week_ranges = []
    for i in range(num_weeks):
        start_of_week = start_date + timedelta(weeks=i)
        end_of_week = start_of_week + timedelta(days=7)
        week_range = f"{start_of_week.strftime('%b %d, %Y')} - {end_of_week.strftime('%b %d, %Y')}"
        week_ranges.append(week_range)
    return week_ranges


# # Specify the start date and number of weeks
# start_date = datetime(2023, 11, 6)  # Starting from 'Jul 22, 2024'
# num_weeks = 56                      # Number of weeks to generate

# # Generate and print the list of week ranges
# week_ranges = generate_week_ranges(start_date, num_weeks)
# for week in week_ranges:
#     print(week)
