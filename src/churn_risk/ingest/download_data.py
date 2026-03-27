from pathlib import Path

import requests

from churn_risk.config import settings


def download_file(url: str, output_path: str) -> None:
    destination = Path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)

    response = requests.get(url, timeout=60)
    response.raise_for_status()

    destination.write_bytes(response.content)
    print(f"Downloaded dataset to {destination}")


if __name__ == "__main__":
    download_file(
        url=settings.raw_data_url,
        output_path=settings.raw_data_path,
    )
