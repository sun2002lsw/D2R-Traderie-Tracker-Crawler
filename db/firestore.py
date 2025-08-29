from google.cloud import firestore

from .common import TABLE_NAME, BaseDatabase


class CloudFirestore(BaseDatabase):
    def _connect(self):
        # 환경변수 GOOGLE_APPLICATION_CREDENTIALS가 자동 적용됨
        db = firestore.Client()
        self.table = db.collection(TABLE_NAME)

    def _get_items_impl(self) -> list:
        docs = self.table.select(["item_name", "update_time"]).stream()

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
        doc_ref = self.table.document(item_data["item_name"])
        doc_ref.set(item_data)
