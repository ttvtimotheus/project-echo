from google.cloud import pubsub_v1, firestore
import feedparser, json, os

project_id = os.environ.get("GCP_PROJECT", "echo-476821")
topic_name = "echo-ingest"

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path(project_id, topic_name)
db = firestore.Client()

def publish_entry(entry):
    doc = {
        "title": entry.get("title"),
        "link": entry.get("link"),
        "summary": entry.get("summary"),
        "source": "arxiv",
    }
    ref = db.collection("documents").add(doc)[1]
    payload = {"doc_id": ref.id, "link": doc["link"]}
    publisher.publish(topic_path, json.dumps(payload).encode("utf-8"))
    print(f"Published: {doc['title']}")

def main():
    print("Crawler started...")
    feed = feedparser.parse("https://export.arxiv.org/rss/cs")
    for entry in feed.entries[:10]:
        publish_entry(entry)
    print("Crawler finished.")

if __name__ == "__main__":
    main()
