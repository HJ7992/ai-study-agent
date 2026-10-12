from langchain_community.document_loaders import PyMuPDFLoader

file_path = "data/sample_document.pdf"
loader = PyMuPDFLoader(file_path)
data = loader.load()
print(type(data))
print(data)
print(data[0])