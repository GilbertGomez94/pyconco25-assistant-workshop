from pathlib import Path
import arxiv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage



def literature_search(query: str, max_results: int = 5, llm_model: str = "gpt-4o-mini") -> str:
    results = arxiv.Search(
        query=query,
        max_results=max_results,
        sort_by=arxiv.SortCriterion.SubmittedDate,
    ).results()

    papers = list(results)

    Path("papers").mkdir(exist_ok=True)
    for p in papers:
        p.download_pdf(dirpath="papers")

    abstracts = "\n\n".join(f"### {p.title}\n{p.summary}" for p in papers)
    print(abstracts)
    llm = ChatOpenAI(model=llm_model, temperature=0.25).with_config(run_name="research")
    summary = llm.invoke(
        [SystemMessage(content="Resume en español:\n" + abstracts)]
    )
    return summary.content
