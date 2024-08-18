import streamlit as st
import requests
from pendulum import now
import pandas as pd

latitude = 50.1088
longitude = 14.5573
altitude = 270
met_no_api_endpoint = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={latitude}&lon={longitude}&altitude={altitude}"
headers = {'User-Agent': 'blabla'}

response = requests.get(met_no_api_endpoint, headers=headers)
data = response.json()
time_series = data["properties"]["timeseries"]


df = pd.json_normalize(time_series)
df.time = pd.to_datetime(df.time, utc=True)
df = df.set_index('time')

# df.info()
# df.loc[df.index < now("UTC").add(hours=12), ['data.instant.details.air_temperature', 'data.next_1_hours.details.precipitation_amount']].to_markdown('data.md')

st.title("Weather Forecast")

# Display weather information
st.header("Current Conditions")
st.write("Temperature:", df['data.instant.details.air_temperature'][0], "°C")
st.write("Air Pressure:", df['data.instant.details.air_pressure_at_sea_level'][0], "hPa")
st.write("Humidity:", df['data.instant.details.relative_humidity'][0], "%")
st.write("Precipitation in next 1 hour:", df['data.next_1_hours.details.precipitation_amount'][0], "mm")
st.write("Precipitation in next 6 hour:", df['data.next_6_hours.details.precipitation_amount'][0], "mm")
st.write("Wind Speed:", df['data.instant.details.wind_speed'][0], "m/s")
st.write("Wind Direction:", df['data.instant.details.wind_from_direction'][0], "degrees")

# Display weather forecast
st.header("Data")
df[['data.instant.details.air_temperature', 'data.next_1_hours.details.precipitation_amount']]

st.header("Plot")
st.line_chart(df.loc[df.index < now("UTC").add(hours=12), ['data.instant.details.air_temperature', 'data.next_1_hours.details.precipitation_amount']])