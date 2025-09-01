from google.cloud import firestore

from .common import BaseDatabase


class CloudFirestore(BaseDatabase):
    def _connect(self):
        # 환경변수 GOOGLE_APPLICATION_CREDENTIALS가 자동 적용됨
        client = firestore.Client(database="d2r-traderie")
        self.collection = client.collection("recent-trades")

    def _get_items_impl(self) -> list:
        docs = self.collection.select(["update_time"]).stream()

        items = []
        for doc in docs:
            doc_data = doc.to_dict()
            item = {
                "item_name": doc.id,
                "update_time": doc_data["update_time"],
            }

            items.append(item)

        return items

    def _put_item_impl(self, item_data: dict):
        item_data_without_name = {
            k: v for k, v in item_data.items() if k != "item_name"
        }

        doc_ref = self.collection.document(item_data["item_name"])
        doc_ref.set(item_data_without_name)
