import os
from sheets import Client
from distance import distance_matrix
from dotenv import load_dotenv

load_dotenv()
DISTANCE_MATRIX_KEY = os.getenv("DISTANCE_MATRIX_KEY")


def main():
    client = Client()

    addresses = client.get_addresses_to_calculate_distance()
    if len(addresses) == 0:
        print("No new addresses to calculate distances for.")
        exit(0)

    destination_addresses = client.get_destination_addresses()

    results = distance_matrix(addresses, destination_addresses, DISTANCE_MATRIX_KEY)
    client.import_distances(addresses, results)


if __name__ == "__main__":
    main()
