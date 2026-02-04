import argparse
import json
from datetime import datetime

import requests


def track_account(
    api_url, account_number, balance, equity, profit, loss, currency="USD"
):
    """
    Sends account performance data to the GenX Trading Platform API.
    """
    url = f"{api_url}/api/v1/performance/update"
    payload = {
        "account_number": account_number,
        "balance": balance,
        "equity": equity,
        "total_profit": profit,
        "total_loss": loss,
        "currency": currency,
        "timestamp": datetime.now().isoformat(),
    }

    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"Successfully tracked account {account_number}")
        print(json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error tracking account: {e}")
        if hasattr(e, "response") and e.response is not None:
            print(e.response.text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Track MT5 account performance")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--account", required=True, help="Account number")
    parser.add_argument("--balance", type=float, required=True, help="Current balance")
    parser.add_argument("--equity", type=float, required=True, help="Current equity")
    parser.add_argument("--profit", type=float, required=True, help="Total profit")
    parser.add_argument("--loss", type=float, required=True, help="Total loss")

    args = parser.parse_args()

    track_account(
        args.url, args.account, args.balance, args.equity, args.profit, args.loss
    )
