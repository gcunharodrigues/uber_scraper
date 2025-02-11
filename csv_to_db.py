import csv
from db_manager import insert_batch_data

with open('output1.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    rides = list(reader)

for ride in rides:
    if len(ride) < 12:
        ride.append('0.00')

insert_batch_data('ride_data.db', rides)
