import openai
import boto3

client = openai.OpenAI()

s3 = boto3.client("s3")


def process_document(document_text):

    embedding = client.embeddings.create(
        model="text-embedding-3-small",
        input=document_text,
    )

    # Store/process document embeddings for search
    document_search_index = embedding.data

return document_search_index