from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from app.config.settings import get_settings


def test_chat_model():
    settings = get_settings()
    llm = ChatOpenAI(
        model=settings.azure_openai_chat_model,
        api_key=settings.azure_openai_chat_api_key,
        base_url=settings.azure_openai_base_url,
        temperature=1,
    )

    response = llm.invoke("Hello, introduce yourself briefly.")

    assert response.content


def test_embedding_model():
    settings = get_settings()
    embedding = OpenAIEmbeddings(
        model=settings.azure_openai_embedding_model,
        api_key=settings.azure_openai_embedding_api_key,
        base_url=settings.azure_openai_base_url,
    )

    vector = embedding.embed_query("Azure OpenAI is a cloud service for AI models.")

    assert len(vector) > 0
