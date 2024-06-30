import os

from dotenv import load_dotenv, find_dotenv
import openai
from llama_index.core import (
    Document,
    load_index_from_storage,
    Settings,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
)
from llama_index.core.node_parser import (
    get_leaf_nodes,
    HierarchicalNodeParser,
    SentenceWindowNodeParser,
)
from llama_index.core.indices.postprocessor import (
    MetadataReplacementPostProcessor,
    SentenceTransformerRerank,
)
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import AutoMergingRetriever
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding


# Function to build or load the sentence window index.
def build_sentence_window_index(
    file_path,
    api_key,
    model="gpt-4o",
    embedding_model="text-embedding-3-large",
    index_dir="./sentence_index",
):
    # Load and parse the document
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    document_text = "\n\n".join([doc.text for doc in documents])
    document = Document(text=document_text)

    # Segment the document using a Sentence Window Parser
    node_parser = SentenceWindowNodeParser.from_defaults(
        window_size=4,
        window_metadata_key="window",
        original_text_metadata_key="original_sentence",
    )

    # Set up OpenAI integration and embeddings
    openai.api_key = api_key
    llm = OpenAI(model=model, temperature=0.1, api_key=api_key)
    embedding = OpenAIEmbedding(model=embedding_model)

    # Create the index
    Settings.llm = llm
    Settings.embeddings = embedding
    Settings.node_parser = node_parser

    if not os.path.exists(index_dir):
        sentence_index = VectorStoreIndex.from_documents(
            [document], service_context=Settings
        )
        sentence_index.storage_context.persist(persist_dir=index_dir)
    else:
        sentence_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=index_dir),
            service_context=Settings,
        )

    return sentence_index


def build_automerging_index(
    file_path,
    api_key,
    model="gpt-4o",
    embedding_model="text-embedding-3-large",
    index_dir="./merging_index",
    chunk_sizes=None,
):
    chunk_sizes = chunk_sizes or [2048, 512, 128]

    # Load and parse the document
    documents = SimpleDirectoryReader(input_files=[file_path]).load_data()
    document_text = "\n\n".join([doc.text for doc in documents])
    document = Document(text=document_text)

    # Segment the document using a Hierarchical Node Parser
    node_parser = HierarchicalNodeParser.from_defaults(chunk_sizes=chunk_sizes)
    nodes = node_parser.get_nodes_from_documents([document])
    leaf_nodes = get_leaf_nodes(nodes)

    # Set up OpenAI integration and embeddings
    openai.api_key = api_key
    llm = OpenAI(model=model, temperature=0.1, api_key=api_key)
    embedding = OpenAIEmbedding(model=embedding_model)

    # Create the index
    Settings.llm = llm
    Settings.embeddings = embedding

    storage_context = StorageContext.from_defaults()
    storage_context.docstore.add_documents(nodes)

    if not os.path.exists(index_dir):
        automerging_index = VectorStoreIndex(
            leaf_nodes, storage_context=storage_context, service_context=Settings
        )
        automerging_index.storage_context.persist(persist_dir=index_dir)
    else:
        automerging_index = load_index_from_storage(
            StorageContext.from_defaults(persist_dir=index_dir),
            service_context=Settings,
        )
    return automerging_index


# Function to get the automerging query engine.
def get_automerging_query_engine(automerge_index, similarity_top_k=12, rerank_top_n=6):
    base_retriever = automerge_index.as_retriever(similarity_top_k=similarity_top_k)
    retriever = AutoMergingRetriever(
        base_retriever, automerge_index.storage_context, verbose=True
    )
    rerank = SentenceTransformerRerank(
        top_n=rerank_top_n, model="BAAI/bge-reranker-base"
    )
    auto_merging_engine = RetrieverQueryEngine.from_args(
        retriever, node_postprocessors=[rerank]
    )
    return auto_merging_engine


# Function to get the sentence window query engine
def get_sentence_window_query_engine(sentence_index):
    # Set up post-processing
    postproc = MetadataReplacementPostProcessor(target_metadata_key="window")

    # Set up the query engine
    sentence_window_engine = sentence_index.as_query_engine(
        similarity_top_k=10, node_postprocessors=[postproc]
    )

    return sentence_window_engine


def get_openai_api_key():
    _ = load_dotenv(find_dotenv())

    return os.getenv("OPENAI_API_KEY")
