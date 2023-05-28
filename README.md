# chat-past

Let OpenAI leverage your private knowledge, which presented in your past notes like txt/md/html and Evernote.

我积累了很多笔记，Evernote里一部分，硬盘上文件也有一部分。当我想就某个主题写一篇文章时，我希望能从过往的笔记里找出最相关的一些内容，比如一些案例、一些以前的感想、一些摘录等。这是用传统的关键词搜索做不到的，是需要按语意搜索的。更进一步，当询问 OpenAI 某个 Topic 时，我希望 OpenAI 能用到那些相关的信息。

目前除了用过往笔记数据微调模型，主要就是利用Vector DB 和 OpenAI 的 Embedding 来实现上述目的了。LangChain 已经封装了上述操作。本项目添加了简单的命令行接口，使你可以指定你的笔记目录、向量化后的数据目录、取几条最相关文档等个性化信息。

基本上分为 3 步。

## Step 1：向量化你的数据
```
python3 indexing.py -h

usage: indexing.py [-h] [--source-folder SOURCE_FOLDER] [--db-folder DB_FOLDER] [--chunk-size CHUNK_SIZE]

Using OpenAI Embedding API to index your private data, and persist them to Chroma. It will load all supported files from your specified source folder. Currently it supports text file(*.txt), markdown file(*.md) and html file(*.htm*). The support for Evernote exported notes is coming.

options:
  -h, --help            show this help message and exit
  --source-folder SOURCE_FOLDER
                        The source folder in which your private data is located.
  --db-folder DB_FOLDER
                        The folder in which the indexed data will be persisted.
  --chunk-size CHUNK_SIZE
                        chunk size to split your documents. Default is 200.
```

这一步基本上只需要做一次，后续有新笔记的时候再跑一次即可（@TODO：检查md5，仅索引新文件）

## Step 2：找出最相关的 Top K 段文档
```
usage: query.py [-h] [--db-folder DB_FOLDER] [--top-k TOP_K] query

Retrieve top k relevant docs.

positional arguments:
  query                 The question you want to query.

options:
  -h, --help            show this help message and exit
  --db-folder DB_FOLDER
                        The folder of your indexed private data.
  --top-k TOP_K         Default value is 10.
```

## Step 3：将最相关文档加入 context，连同你的问题向 OpenAI 发出请求
```
usage: asking.py [-h] [--db-folder DB_FOLDER] [--top-k TOP_K] query

Ask your question to OpenAI, combined the top k relevant docs in context.

positional arguments:
  query                 The question you want to ask.

options:
  -h, --help            show this help message and exit
  --db-folder DB_FOLDER
                        The folder of your indexed private data.
  --top-k TOP_K         Default value is 10.
```

当然还有 Step 0.

## Step 0：将 OpenAI API Key 加入环境变量

> export OPENAI_API_KEY=your-key