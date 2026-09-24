from langgraph.store.memory import InMemoryStore
store =InMemoryStore()
store.put(
    ("users",),
    'user123',{"name": "张三", "language": "中文", "location": "北京"}
)
store.put(
    ("users",),##nameplace
    "user2",
    {"name": "李四", "language": "English", "location": "深圳"}
)
# 2. Get：按key精确读取
item =store.get(("users",),"user2")
if item:
    print(item.value)

# 3. Search：跨key搜索（支持内容过滤和向量相似度）
items = store.search(
    ("users",),
    filter={"language":"English"},
    query="语言偏好"      # 向量相似度搜索（需配置embedding）
)
print(items)

# 4. Delete：删除记忆
store.delete(("users",),"user2")

# 5. List：列出namespace下的所有key
items = store.search(("users",))
print(items)