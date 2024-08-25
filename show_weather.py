import requests
from pendulum import now
import pandas as pd
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from symbol_code import symbol_code_id


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


# Prepare data
df_ = df.loc[df.index < now("UTC").add(hours=12), ['data.instant.details.air_temperature', 'data.next_1_hours.details.precipitation_amount']]


# render picture
def font(font_ttf = 'LiberationSans-Regular.ttf', font_size=32):
    return ImageFont.truetype(font_ttf, font_size)

def header(draw, cursor=(16, 0), text=''):
    cursor = cursor[0], cursor[1]+28
    draw.text(cursor, text, font = font(font_size=44), fill = 0)
    return cursor[0], cursor[1]+44+16

def header2(draw, cursor=(16, 0), text=''):
    cursor = cursor[0], cursor[1]+20
    draw.text(cursor, text, font = font(font_size=36), fill = 0)
    return cursor[0], cursor[1]+36+12

def text(draw, cursor=(16, 0), text=''):
    cursor = cursor[0], cursor[1]+4
    draw.text(cursor, text, font = font(font_size=28), fill = 0)
    return cursor[0], cursor[1]+28+4

def day(draw, cursor=(16, 0), text=''):
    cursor = cursor[0], cursor[1]+4
    draw.text(cursor, text, font = font(font_size=28), fill = 0)
    return cursor[0]+64, cursor[1]

def weather_symbol(image, cursor=(16, 0), symbol_code=''):
    icon = Image.open(Path() / 'yrno' / 'symbols' / 'lightmode' / 'png' / '100' / f'{symbol_code_id[symbol_code]}.png')
    icon = icon.resize((36, 36))
    image.paste(icon, cursor, icon)
    return cursor[0]+36, cursor[1]

image_blc = Image.new('1', (800, 480), 255)  # 255: clear the frame
image_red = Image.new('1', (800, 480), 255)  # 255: clear the frame
draw_blc = ImageDraw.Draw(image_blc)
draw_image_red = ImageDraw.Draw(image_red)

# first culumn
cursor = header(draw_blc, cursor=(16, 0), text="Počasí yr.no")
cursor = text(draw_blc, cursor=cursor, text=f'{now("Europe/Prague").strftime(r"%c")[:-8]}',)
cursor = header2(draw_blc, cursor=cursor, text='Aktuální podmínky',)
symbol_code = df['data.next_1_hours.summary.symbol_code'].iloc[0]
cursor = weather_symbol(image_blc, cursor=cursor, symbol_code=df['data.next_1_hours.summary.symbol_code'].iloc[0])
cursor = text(draw_blc, cursor=cursor, text=f"{df['data.instant.details.air_temperature'].iloc[0]} °C {df['data.next_1_hours.details.precipitation_amount'].iloc[0]} mm/h",)
cursor = 16, cursor[1]
cursor = header2(draw_blc, cursor=cursor, text='Předpověď',)

symbol_code = df['data.next_12_hours.summary.symbol_code'].iloc[0]
cursor = day(draw_blc, cursor=cursor, text=now("Europe/Prague").strftime("%a"))
cursor = weather_symbol(image_blc, cursor=cursor, symbol_code=df['data.next_12_hours.summary.symbol_code'].iloc[0])
cursor = text(draw_blc, cursor=cursor, text=f"{df['data.instant.details.air_temperature'].iloc[0]} °C {df['data.next_6_hours.details.precipitation_amount'].iloc[0]} mm/h",)
cursor = 16, cursor[1]

tomorow = now("UTC").set(hour=10, minute=0, second=0, microsecond=0).add(days=1)
df = df.loc[df.index == tomorow]
cursor = day(draw_blc, cursor=cursor, text=tomorow.strftime("%a"))
cursor = weather_symbol(image_blc, cursor=cursor, symbol_code=df['data.next_12_hours.summary.symbol_code'].iloc[0])
cursor = text(draw_blc, cursor=cursor, text=f"{df['data.instant.details.air_temperature'].iloc[0]} °C {df['data.next_6_hours.details.precipitation_amount'].iloc[0]} mm/h",)
cursor = 16, cursor[1]

# second column placeholder
cursor = header(draw_blc, cursor=(416, 0), text="Golemio")
cursor = header2(draw_blc, cursor=cursor, text='Autobusy',)
cursor = text(draw_blc, cursor=cursor, text='201 16:51',)
cursor = header2(draw_blc, cursor=cursor, text='Vlaky',)
cursor = text(draw_blc, cursor=cursor, text='SP8501 16:21',)


# draw_image_blc.text((16, 32), f"Temperature: {df['data.instant.details.air_temperature'][0]} °C", font = font16, fill = 0)
# draw_image_blc.text((16, 32+16), f"Air Pressure: {df['data.instant.details.air_pressure_at_sea_level'][0]} hPa", font = font16, fill = 0)
# draw_image_blc.text((16, 32+32), f"Humidity: {df['data.instant.details.relative_humidity'][0]} %", font = font16, fill = 0)
# draw_image_blc.text((16, 32+48), f"Precipitation in next 1 hour: {df['data.next_1_hours.details.precipitation_amount'][0]} mm", font = font16, fill = 0)
# draw_image_blc.text((16, 32+64), f"Precipitation in next 6 hour: {df['data.next_6_hours.details.precipitation_amount'][0]} mm", font = font16, fill = 0)
# draw_image_blc.text((16, 32+80), f"Wind Speed: {df['data.instant.details.wind_speed'][0]} m/s", font = font16, fill = 0)
# draw_image_blc.text((16, 32+96), f"Wind Direction: {df['data.instant.details.wind_from_direction'][0]} Degrees", font = font16, fill = 0)

image_blc.save('image.png', 'PNG')