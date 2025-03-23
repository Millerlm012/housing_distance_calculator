import math
import requests


def format_addresses(addresses):
    url_friendly_addresses = ""
    for address in addresses:
        url_friendly_addresses += address.replace("#", "")

        if address != addresses[-1]:
            url_friendly_addresses += "|"

    return url_friendly_addresses


def distance_matrix(addresses, destination_addresses, key):
    """
    You can only pass a max of 25 origins or 25 destinations to the Distance Matrix API.
    We will batch the addresses and raise an error if destinations exceeds limit.
    """

    BATCH_LIMIT = 25
    if len(destination_addresses) > BATCH_LIMIT:
        raise ValueError(
            f"Max of 25 destinaton addresses (currently). Received: {len(destination_addresses)}."
        )

    all_rows = []
    batches = math.floor(len(addresses) / BATCH_LIMIT)
    for i in range(batches + 1):
        origin_batch = addresses[BATCH_LIMIT * i : BATCH_LIMIT * (i + 1)]

        origins = format_addresses(origin_batch)
        destinations = format_addresses(destination_addresses)

        url = f"https://maps.googleapis.com/maps/api/distancematrix/json?destinations={destinations}&origins={origins}&units=imperial&key={key}"
        rsp = requests.get(url)
        data = rsp.json()

        if rsp.status_code != 200 or data["status"] != "OK":
            raise ValueError(
                f"Distance Matrix API request failed. \nStatus Code: {rsp.status_code}\nResponse Status: {data['status']}\nError: {rsp.text}"
            )

        all_rows += data["rows"]

    return all_rows
