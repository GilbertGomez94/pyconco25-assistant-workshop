from langchain_core.tools import tool
from langchain_community.retrievers import ArxivRetriever

_arxiv = ArxivRetriever(load_max_docs=3, get_full_documents=False)


@tool("AcademicSearchTool", description="Busca artículos académicos en arXiv.")
def academic_search_tool(query: str) -> str:
    docs = _arxiv.invoke(query)
    if not docs:
        return "No se encontraron artículos."
    return "\n\n".join(
        f"Título: {d.metadata.get('Title')}\nResumen: {d.page_content[:300]}…\nLink: {d.metadata.get('Entry ID')}"
        for d in docs
    )
