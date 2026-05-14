import asyncio
import json
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

CONN_STR = "Endpoint=sb://itri613.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=nvcKq+P4E0ygthPvOIuLILiY1OI/g/ta3+AEhKz8IqU="
HUB = "clickstream-hub"

async def send_poison():
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CONN_STR,
        eventhub_name=HUB
    )
    async with producer:
        batch = await producer.create_batch()
        
        # Poison message 1: missing event_id (NULL)
        poison1 = {
            "event_id": None,
            "event_type": "clickstream",
            "user_id": "C9999",
            "price": 500,
            "action": "view",
            "event_time": "2026-05-01T12:00:00"
        }
        
        # Poison message 2: negative price
        poison2 = {
            "event_id": "poison_002",
            "event_type": "clickstream", 
            "user_id": "C9998",
            "price": -999,
            "action": "purchase",
            "event_time": "2026-05-01T12:00:01"
        }
        
        # Poison message 3: price way too high
        poison3 = {
            "event_id": "poison_003",
            "event_type": "clickstream",
            "user_id": "C9997", 
            "price": 999999,
            "action": "purchase",
            "event_time": "2026-05-01T12:00:02"
        }
        
        batch.add(EventData(json.dumps(poison1)))
        batch.add(EventData(json.dumps(poison2)))
        batch.add(EventData(json.dumps(poison3)))
        
        await producer.send_batch(batch)
        print("3 poison messages sent to Event Hubs")

asyncio.run(send_poison())