import io
import os
from getpass import getpass

import garth
import pandas as pd
from loguru import logger

SESS_DIR = os.path.expanduser("~/.cache/garmin")


class Client:
    def __init__(self):
        self.client = garth.Client(domain="garmin.com")

        if os.path.exists(SESS_DIR):
            logger.info(f"Loading session from {SESS_DIR}")
            self.client.load(SESS_DIR)
        else:
            logger.info(f"Saving session to {SESS_DIR}")
            username = input("> Username: ")
            password = getpass("> Password: ")
            self.client.login(username, password, prompt_mfa=None)
            self.client.dump(SESS_DIR)

    def get_activites(self, start: int, limit: int) -> list[dict]:
        return self.client.connectapi(
            "/activitylist-service/activities/search/activities",
            params={"start": start, "limit": limit},
        )

    def get_activity(self, activity_id: str, format: str = "csv") -> pd.DataFrame:
        assert format in ["csv", "gpx"]
        url = f"/download-service/export/{format}/activity/{activity_id}"
        raw = self.client.download(url)
        return pd.read_csv(io.BytesIO(raw))


def main():
    client = Client()

    res = pd.DataFrame(client.get_activites(start=0, limit=5))
    print(res)

    aid = res.iloc[0]["activityId"]
    dat = client.get_activity(aid)
    print(dat)


if __name__ == "__main__":
    main()
