import io
import os
from getpass import getpass

import garth
import gpxpy
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

    def get_activities(self, start: int, limit: int) -> list[dict]:
        return self.client.connectapi(
            "/activitylist-service/activities/search/activities",
            params={"start": start, "limit": limit},
        )

    def get_activity(self, activity_id: str, format: str) -> bytes:
        """
        Get more info about an `activity_id`. Format can be one of `csv, gpx, tcx`.
        """
        assert format in ["csv", "gpx", "tcx"]
        url = f"/download-service/export/{format}/activity/{activity_id}"
        return self.client.download(url)

    def get_hr(self, activity_id: str) -> list[int]:
        gpx = gpxpy.parse(self.get_activity(activity_id, format="gpx").decode())
        assert len(gpx.tracks) == 1
        assert len(gpx.tracks[0].segments) == 1
        return [
            int(pt.extensions[0].find(".//{*}hr").text) for pt in gpx.tracks[0].segments[0].points
        ]

    @staticmethod
    def csv_bytes_to_pandas(bytez: bytes) -> pd.DataFrame:
        return pd.read_csv(io.BytesIO(bytez))


def main():
    client = Client()

    res = pd.DataFrame(client.get_activites(start=0, limit=5))
    print(res)

    aid = res.iloc[0]["activityId"]
    dat = client.get_activity(aid)
    print(dat)


if __name__ == "__main__":
    main()
