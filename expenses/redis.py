import redis

r = redis.Redis.from_url("rediss://default:Adb1AAIjcDFhYTEwNTgxOWI3NzA0YmQ5OWNjYWI1MmFlNmM2NmJkNXAxMA@ethical-jackass-55029.upstash.io:6379")

r.set('foo', 'bar')
value = r.get('foo')