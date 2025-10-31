from google.cloud import pubsub_v1, firestore
import feedparser, json, os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def publish_entry(db, publisher, topic_path, entry):
    """Publish a single feed entry to Pub/Sub and Firestore."""
    try:
        doc = {
            "title": entry.get("title", "Untitled"),
            "link": entry.get("link", ""),
            "summary": entry.get("summary", ""),
            "source": "arxiv",
            "created_at": firestore.SERVER_TIMESTAMP
        }
        
        # Add to Firestore
        ref = db.collection("documents").add(doc)[1]
        logger.info(f"Document created: {ref.id}")
        
        # Publish to Pub/Sub
        payload = {"doc_id": ref.id, "link": doc["link"]}
        future = publisher.publish(topic_path, json.dumps(payload).encode("utf-8"))
        future.result()  # Wait for publish to complete
        
        logger.info(f"Published: {doc['title'][:50]}...")
        return True
    except Exception as e:
        logger.error(f"Error publishing entry: {str(e)}", exc_info=True)
        return False

def main():
    """Main crawler function."""
    try:
        logger.info("Crawler started")
        
        # Initialize clients
        project_id = os.environ.get("GCP_PROJECT", "echo-476821")
        topic_name = "echo-ingest"
        
        logger.info(f"GCP Project: {project_id}")
        logger.info(f"Topic: {topic_name}")
        
        publisher = pubsub_v1.PublisherClient()
        topic_path = publisher.topic_path(project_id, topic_name)
        db = firestore.Client()
        
        logger.info("Fetching ArXiv RSS feed...")
        feed = feedparser.parse("https://export.arxiv.org/rss/cs")
        
        if not feed.entries:
            logger.warning("No entries found in feed")
            return
        
        logger.info(f"Found {len(feed.entries)} entries, processing first 10")
        
        success_count = 0
        for i, entry in enumerate(feed.entries[:10], 1):
            logger.info(f"Processing entry {i}/10")
            if publish_entry(db, publisher, topic_path, entry):
                success_count += 1
        
        logger.info(f"Crawler finished. Successfully processed {success_count}/10 entries")
        
    except Exception as e:
        logger.error(f"Crawler failed: {str(e)}", exc_info=True)
        raise

if __name__ == "__main__":
    main()
