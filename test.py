from pymilvus import connections, Collection

connections.connect(host="localhost", port="19530")
col = Collection("knowledge_base")
col.load()
print(f"文档总数: {col.num_entities}")

# 打印前两条文档的前200个字符
results = col.query(expr="id >= 0", output_fields=["text"], limit=10)
for r in results:
    print(r["text"][:500] )