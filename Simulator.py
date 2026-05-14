import asyncio
import json
import random
import uuid
import datetime
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData

# Connection strings
CLICKSTREAM_CONN_STR = "Endpoint=sb://itri613.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=nvcKq+P4E0ygthPvOIuLILiY1OI/g/ta3+AEhKz8IqU="
CUSTOMER_REF_CONN_STR = "Endpoint=sb://itri613.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=nvcKq+P4E0ygthPvOIuLILiY1OI/g/ta3+AEhKz8IqU="
SYSTEMLOG_CONN_STR = "Endpoint=sb://itri613.servicebus.windows.net/;SharedAccessKeyName=SystemLog;SharedAccessKey=iAfgqOCFoeoxWv8qIv6qfejShZWdkzKsW+AEhAwLLWc=;EntityPath=systemlog-hub"

# Hub names
CLICKSTREAM_HUB = "clickstream-hub"
CUSTOMER_REF_HUB = "customer-ref-hub"
SYSTEMLOG_HUB = "systemlog-hub"

# Products catalog
PRODUCTS = [
    {"product_id": "P1001", "category": "electronics", "price": 5000, "name": "Laptop"},
    {"product_id": "P1002", "category": "electronics", "price": 1500, "name": "Headphones"},
    {"product_id": "P1003", "category": "clothing", "price": 800, "name": "Jacket"},
    {"product_id": "P1004", "category": "clothing", "price": 300, "name": "Jeans"},
    {"product_id": "P1005", "category": "home", "price": 1200, "name": "Coffee Machine"},
    {"product_id": "P1006", "category": "home", "price": 450, "name": "Lamp"},
    {"product_id": "P1007", "category": "beauty", "price": 250, "name": "Perfume"},
    {"product_id": "P1008", "category": "beauty", "price": 150, "name": "Skincare Set"},
]

CUSTOMER_SEGMENTS = ["new", "regular", "high_value", "at_risk"]
CUSTOMER_IDS = [f"C{str(i).zfill(4)}" for i in range(1, 101)]
active_sessions = {}

def get_timestamp():
    base_time = datetime.datetime.now()
    if random.random() < 0.1:
        delay_seconds = random.randint(2, 30)
        return (base_time - datetime.timedelta(seconds=delay_seconds)).isoformat()
    return base_time.isoformat()

def generate_clickstream_event():
    user_id = random.choice(CUSTOMER_IDS)
    product = random.choice(PRODUCTS)
    
    if user_id not in active_sessions:
        active_sessions[user_id] = {
            "session_start": datetime.datetime.now(),
            "last_product": None
        }
    
    actions = ["view", "view", "view", "add_to_cart", "view", "remove_from_cart", "purchase"]
    action = random.choice(actions)
    
    # 10% chance to generate a poison message
    if random.random() < 0.1:
        poison_type = random.choice(["null_event_id", "negative_price", "excessive_price"])
        
        if poison_type == "null_event_id":
            return {
                "event_id": None,
                "event_type": "clickstream",
                "user_id": user_id,
                "product_id": product["product_id"],
                "product_name": product["name"],
                "category": product["category"],
                "price": product["price"],
                "action": action,
                "session_id": f"sess_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H')}",
                "event_time": get_timestamp()
            }
        elif poison_type == "negative_price":
            return {
                "event_id": f"poison_{uuid.uuid4().hex[:8]}",
                "event_type": "clickstream",
                "user_id": user_id,
                "product_id": product["product_id"],
                "product_name": product["name"],
                "category": product["category"],
                "price": random.randint(-1000, -1),
                "action": action,
                "session_id": f"sess_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H')}",
                "event_time": get_timestamp()
            }
        else:  # excessive_price
            return {
                "event_id": f"poison_{uuid.uuid4().hex[:8]}",
                "event_type": "clickstream",
                "user_id": user_id,
                "product_id": product["product_id"],
                "product_name": product["name"],
                "category": product["category"],
                "price": random.randint(100001, 500000),
                "action": action,
                "session_id": f"sess_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H')}",
                "event_time": get_timestamp()
            }
    
    # Normal event
    return {
        "event_id": f"click_{uuid.uuid4().hex[:8]}",
        "event_type": "clickstream",
        "user_id": user_id,
        "product_id": product["product_id"],
        "product_name": product["name"],
        "category": product["category"],
        "price": product["price"],
        "action": action,
        "session_id": f"sess_{user_id}_{datetime.datetime.now().strftime('%Y%m%d%H')}",
        "event_time": get_timestamp()
    }

def generate_customer_profile():
    user_id = random.choice(CUSTOMER_IDS)
    segment = random.choice(CUSTOMER_SEGMENTS)
    
    if segment == "high_value":
        avg_order = random.randint(3000, 10000)
        lifetime_value = random.randint(20000, 100000)
    elif segment == "regular":
        avg_order = random.randint(500, 3000)
        lifetime_value = random.randint(5000, 20000)
    elif segment == "new":
        avg_order = random.randint(100, 1000)
        lifetime_value = random.randint(0, 5000)
    else:  # at_risk
        avg_order = random.randint(100, 500)
        lifetime_value = random.randint(1000, 10000)
    
    return {
        "event_id": f"profile_{uuid.uuid4().hex[:8]}",
        "event_type": "customer_profile",
        "user_id": user_id,
        "segment": segment,
        "avg_order_value": avg_order,
        "lifetime_value": lifetime_value,
        "preferred_category": random.choice(["electronics", "clothing", "home", "beauty"]),
        "is_active": segment != "at_risk",
        "event_time": get_timestamp()
    }

def generate_system_log():
    """Generate system/error log events - third heterogeneous source"""
    log_levels = ["INFO", "INFO", "INFO", "WARNING", "ERROR"]
    services = ["checkout-service", "inventory-service", 
                "payment-service", "recommendation-engine"]
    
    errors = [
        "Payment gateway timeout after 30s",
        "Inventory check failed for product",
        "Recommendation model latency spike detected",
        "Database connection pool exhausted",
        "Cache miss rate exceeded threshold"
    ]
    
    level = random.choice(log_levels)
    service = random.choice(services)
    
    return {
        "event_id": f"log_{uuid.uuid4().hex[:8]}",
        "event_type": "system_log",
        "log_level": level,
        "service": service,
        "message": random.choice(errors) if level == "ERROR" 
                   else f"{service} processed request successfully",
        "response_time_ms": random.randint(10, 5000),
        "error_code": f"ERR_{random.randint(1000,9999)}" 
                      if level == "ERROR" else None,
        "event_time": get_timestamp()
    }

async def send_clickstream_events():
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CLICKSTREAM_CONN_STR,
        eventhub_name=CLICKSTREAM_HUB
    )
    
    async with producer:
        normal_count = 0
        poison_count = 0
        
        while True:
            try:
                batch = await producer.create_batch()
                batch_size = random.randint(5, 15)
                
                for _ in range(batch_size):
                    event = generate_clickstream_event()
                    batch.add(EventData(json.dumps(event)))
                    
                    if event.get('event_id') is None or event.get('price', 0) < 0 or event.get('price', 0) > 100000:
                        poison_count += 1
                        print(f" POISON MESSAGE SENT: {event.get('event_id', 'NULL_ID')} - Price: {event.get('price', 'N/A')}")
                    else:
                        normal_count += 1
                
                await producer.send_batch(batch)
                print(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] Sent {batch_size} events (Normal: {normal_count}, Poison: {poison_count})")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"Clickstream Error: {e}")
                await asyncio.sleep(1)

async def send_reference_events():
    producer = EventHubProducerClient.from_connection_string(
        conn_str=CUSTOMER_REF_CONN_STR,
        eventhub_name=CUSTOMER_REF_HUB
    )
    
    async with producer:
        while True:
            try:
                profile = generate_customer_profile()
                await producer.send_event(EventData(json.dumps(profile)))
                print(f"  [REF] Profile: {profile['user_id']} - {profile['segment']} (LTV: R{profile['lifetime_value']})")
                await asyncio.sleep(30)
            except Exception as e:
                print(f"REF Error: {e}")
                await asyncio.sleep(30)

async def send_system_logs():
    """Send system log events every 15 seconds"""
    producer = EventHubProducerClient.from_connection_string(
        conn_str=SYSTEMLOG_CONN_STR,
        eventhub_name=SYSTEMLOG_HUB
    )
    
    async with producer:
        while True:
            try:
                log = generate_system_log()
                await producer.send_event(EventData(json.dumps(log)))
                print(f"  [LOG] {log['log_level']} — "
                      f"{log['service']}: {log['message'][:50]}")
                await asyncio.sleep(15)
            except Exception as e:
                print(f"  Log error: {e}")
                await asyncio.sleep(15)

async def main():
    print("=" * 55)
    print("  E-COMMERCE STREAMING SIMULATOR")
    print("  Clickstream → every 1 second")
    print("  Customer profiles → every 30 seconds")
    print("  System logs → every 15 seconds")
    print("  Press Ctrl+C to stop")
    print("=" * 55)
    
    await asyncio.gather(
        send_clickstream_events(),
        send_reference_events(),
        send_system_logs(),
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n Simulator stopped.")