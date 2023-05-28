from typing import Any, Union, List, NamedTuple, Optional, cast
from langchain.schema import Document
from langchain.document_loaders.unstructured import UnstructuredFileLoader
from langchain.document_loaders import TextLoader
import concurrent.futures
import chardet

def print_documents(documents:List[Document]):
    for doc in documents:
        print(doc.metadata["source"])
        print(doc.page_content)
    print(f"documents count: {len(documents)}")

class AnyEncodingTextLoader(TextLoader):
    def __init__(
        self,
        file_path: str
    ):
        super().__init__(file_path,None,True)

class FileEncoding(NamedTuple):
    encoding: Optional[str]
    confidence: float
    language: Optional[str]

def detect_file_encodings(file_path: str, timeout: int = 5) -> List[FileEncoding]:

    def read_and_detect(file_path: str) -> List[dict]:
        with open(file_path, "rb") as f:
            rawdata = f.read()
        return cast(List[dict], chardet.detect_all(rawdata))

    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(read_and_detect, file_path)
        try:
            encodings = future.result(timeout=timeout)
        except concurrent.futures.TimeoutError:
            raise TimeoutError(
                f"Timeout reached while detecting encoding for {file_path}"
            )

    if all(encoding["encoding"] is None for encoding in encodings):
        raise RuntimeError(f"Could not detect encoding for {file_path}")
    return [FileEncoding(**enc) for enc in encodings if enc["encoding"] is not None]


class AnyEncodingHtmlLoader(UnstructuredFileLoader):
    def __init__(
        self,
        file_path: Union[str, List[str]],
        mode: str = "single",
        **unstructured_kwargs: Any,
    ):
        super().__init__(file_path, mode=mode, **unstructured_kwargs)
        detected_encodings = detect_file_encodings(self.file_path)
        detected_encodings.append(FileEncoding(encoding="gb2312",confidence=0.1,language=""))
        detected_encodings.append(FileEncoding(encoding="gbk",confidence=0.1,language=""))
        detected_encodings.append(FileEncoding(encoding="gb18030",confidence=0.1,language=""))
        detected_encodings.append(FileEncoding(encoding="iso-8859-1",confidence=0.1,language=""))
        for encoding in detected_encodings:
            try:
                with open(self.file_path, encoding=encoding.encoding) as f:
                    f.read()
                    self.unstructured_kwargs["encoding"] = encoding.encoding
                break
            except Exception:
                print(file_path)
                print(encoding.encoding)
                continue 

