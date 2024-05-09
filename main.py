import json
from time import sleep
import schedule
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
import json

from switchbot import Switchbot

with open('config.json', 'r') as config_file:
    config = json.load(config_file)

bucket = config['influxdb']['bucket']
org = config['influxdb']['org']
token = config['influxdb']['token']
url = config['influxdb']['url']

client = InfluxDBClient(
    url=url,
    token=token,
    org=org
)

write_api = client.write_api(write_options=SYNCHRONOUS)


def save_device_status(status: dict):
    """SwitchbotデバイスのステータスをInfluxDBに保存する"""

    device_type = status.get("deviceType")

    if device_type == "Meter":
        p = (
            Point("Meter")
            .tag("device_id", status["deviceId"])
            .field("humidity", float(status["humidity"]))
            .field("temperature", float(status["temperature"]))
        )

        write_api.write(bucket=bucket, record=p)
        print(f"Saved:{status}")


def task():
    """定期実行するタスク"""
    bot = Switchbot()
    print("a")

    with open("device_list.json", "r") as f:
        device_list = json.load(f)

    for d in device_list:
        device_type = d.get("deviceType")
        if device_type == "Meter":
            print("meter")
            try:
                status = bot.get_device_status(d.get("deviceId"))
            except Exception as e:
                print(f"Request error: {e}")
                continue
            print(status)

            try:
                save_device_status(status)
            except Exception as e:
                print(f"Save error: {e}")
            print("exit")


if __name__ == "__main__":
    schedule.every(5).minutes.do(task)

    while True:
        schedule.run_pending()
        sleep(1)
