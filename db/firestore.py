from google.cloud import firestore

from .common import BaseDatabase


class CloudFirestore(BaseDatabase):
    def _connect(self):
        # 환경변수 GOOGLE_APPLICATION_CREDENTIALS가 자동 적용됨
        client = firestore.Client(database="d2r-traderie")
        self.collection = client.collection("recent-trades")

    def _get_items_impl(self) -> list:
        docs = self.collection.select(["item_name", "update_time"]).stream()

        items = []
        for doc in docs:
            doc_data = doc.to_dict()
            if doc_data:
                items.append(
                    {
                        "item_name": doc_data.get("item_name", ""),
                        "update_time": doc_data.get("update_time", ""),
                    }
                )

        return items

    def _put_item_impl(self, item_data: dict):
        doc_ref = self.collection.document(item_data["item_name"])
        doc_ref.set(item_data)
