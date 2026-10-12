from langchain_text_splitters import RecursiveCharacterTextSplitter
text = "今天天气很好。我们去吃饭！你觉得怎么样？走吧。明天还要上班。记得早起！"

##1. 普通切分
spliter = RecursiveCharacterTextSplitter(
    chunk_size=10,
    chunk_overlap=2,
    is_separator_regex=False,
    separators=['\n\n','\n','。','，','！','？']
)
chunks1 = spliter.split_text(text)
print(f"普通切分结果{chunks1}")
for i,chunk in enumerate(chunks1,1):
    print(f"第{i}块：{chunk}")
##2。 正则切分
spliter = RecursiveCharacterTextSplitter(
    chunk_size=10,
    chunk_overlap=2,
    is_separator_regex=True,
    separators=['\n\n','\n','(?<=。)','(?<=，)','(?<=！)','(?<=？)']
)
chunks1 = spliter.split_text(text)
print(chunks1)
print(f"正则切分结果{chunks1}")
for i,chunk in enumerate(chunks1,1):
    print(f"第{i}块：{chunk}")



