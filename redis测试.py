import redis


conn = redis.Redis(host="52.15.206.110", port=6379, password='123ec2')
# conn = redis.Redis(host="47.93.4.198", port=6379, password='123123')
conn.set("k1", "v1")
val = conn.get("k1")
print(val)