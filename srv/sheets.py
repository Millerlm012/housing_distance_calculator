from google.oauth2 import service_account
from googleapiclient.discovery import build


class Client:
    def __init__(self):
        self.spreadsheet_id = "1g-9_xtC0OARsYJ7QhIiEOglvGtcJD3rFUyd5igFqc1I"
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.address_range = "Homes!C2:C"
        self.destination_range = "Destination Addresses!B1:B"
        self.address_distance_range = "Distances!A2:A"
        self.distance_row_index = 0
        self.init_service()

    def init_service(self):
        creds = service_account.Credentials.from_service_account_file(
            "./personal-services-339304-8242e8e3f1e7.json"
        )
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet = self.service.spreadsheets()

    def get_addresses_to_calculate_distance(self):
        result = (
            self.sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=self.address_range)
            .execute()
        )
        origin_addresses = [
            address for row in result.get("values", []) for address in row
        ]

        result = (
            self.sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=self.address_distance_range)
            .execute()
        )
        calculated_addresses = [
            address for row in result.get("values", []) for address in row
        ]

        self.distance_row_index = (
            len(calculated_addresses) + 1
        )  # adding 2 to offset the header row

        addresses_to_calculate_for = []
        for address in origin_addresses:
            if address not in calculated_addresses:
                addresses_to_calculate_for.append(address)

        return addresses_to_calculate_for

    def get_destination_addresses(self):
        result = (
            self.sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=self.destination_range)
            .execute()
        )
        values = result.get("values", [])

        addresses = []
        for row in values:
            address_col = row[0]
            addresses.append(address_col)

        return addresses

    def import_distances(self, addresses, values):
        sheet_batch_update_payload = []
        for i, row in enumerate(values):
            mapped_values = [addresses[i]]
            for val in row["elements"]:
                mapped_values.append(val["distance"]["text"])
                mapped_values.append(val["duration"]["text"])

            sheet_batch_update_payload.append(
                {
                    # distance_row_index is the index of where it's at before update
                    # i is where we're at in our iteration of new rows
                    # we add 1 to get to the index for our new row
                    "range": f"Distances!A{self.distance_row_index + i + 1}:K{self.distance_row_index + i + 1}",
                    "values": [mapped_values],
                }
            )

        self.sheet.values().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={"valueInputOption": "RAW", "data": sheet_batch_update_payload},
        ).execute()
