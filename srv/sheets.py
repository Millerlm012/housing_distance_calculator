from google.oauth2 import service_account
from googleapiclient.discovery import build


class Client:
    def __init__(self):
        self.spreadsheet_id = "1g-9_xtC0OARsYJ7QhIiEOglvGtcJD3rFUyd5igFqc1I"
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.origin_range = "Homes!A2:U"
        self.destination_range = "Destination Addresses!B1:B"
        self.sheet_batch_update_payload = []
        self.init_service()

    def init_service(self):
        creds = service_account.Credentials.from_service_account_file(
            "./personal-services-339304-8242e8e3f1e7.json"
        )
        self.service = build("sheets", "v4", credentials=creds)
        self.sheet = self.service.spreadsheets()

    def get_addresses(self):
        result = (
            self.sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=self.origin_range)
            .execute()
        )
        values = result.get("values", [])

        addresses = []
        for i, row in enumerate(values):
            if (
                len(row) <= 11
            ):  # if less than 11 columns, it's missing the distance calculations
                row_to_update = i + 2
                self.sheet_batch_update_payload.append(
                    {"range": f"Homes!L{row_to_update}:U{row_to_update}"}
                )  # adding ranges to update for import_distances()
                addresses.append(row[2])

        return addresses

    def get_destination_addresses(self):
        result = (
            self.sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=self.destination_range)
            .execute()
        )
        values = result.get("values", [])

        addresses = []
        for row in values:
            addresses.append(row[0])

        return addresses

    def import_distances(self, values):
        for i, row in enumerate(values):
            mapped_values = []
            for val in row["elements"]:
                mapped_values.append(val["distance"]["text"])
                mapped_values.append(val["duration"]["text"])

            self.sheet_batch_update_payload[i]["values"] = [mapped_values]

        self.sheet.values().batchUpdate(
            spreadsheetId=self.spreadsheet_id,
            body={"valueInputOption": "RAW", "data": self.sheet_batch_update_payload},
        ).execute()
