from fastapi import APIRouter,HTTPException
from app.services.retrieval.retriever import retriever
from app.schemas.query import  QueryRequest, QueryResponse,Source
from app.services.llm.llm_servicelocal import generate_response
from app.services.retrieval.prompt_builder import build_prompt,build_general_prompt
router = APIRouter(tags=["Query"])

@router.post( "/query",response_model=QueryResponse)
   
def query_endpoint(request: QueryRequest):
    user_query = request.q.strip()
    document_id = request.document_id

    if not user_query:
        raise HTTPException(
            status_code=400,
            detail="Query string 'q' cannot be empty."
 )
    
    try:
       #Document RAG Mode (PDF context attached)
        if document_id:

            # Retrieve & Rerank
            reranked_results = retriever(
                question=user_query,
                document_id=document_id,
            )

            # No relevant context found
            if not reranked_results:
                return QueryResponse(
                    question=user_query,
                    answer="I couldn't find this information in the uploaded research paper.",
                    sources=[],
                )

            # Step 2: Build ChatML prompt
            messages = build_prompt(
                query=user_query,
                reranked_docs=reranked_results,
            )

            # Step 3: Run LLM Inference
            answer = generate_response(messages)

            # Step 4: Extract unique source citations
            seen = set()
            sources = []

            for doc in reranked_results:
                key = (doc.get("source"), doc.get("page"))

                if key not in seen:
                    seen.add(key)
                    sources.append(
                        Source(
                            document_id=doc.get("source", document_id),
                            page=doc.get("page", 1),
                        )
                    )

            return QueryResponse(
                question=user_query,
                answer=answer,
                sources=sources,
            )
#---------if no pdf is give and direct query is asked so no rag direct llm call--------#
        else:
            # Step 1: Build ChatML prompt without context wrapper
            messages = build_general_prompt(query=user_query)

            # Step 2: Run LLM Inference
            answer = generate_response(messages)

            # Step 3: Return response with empty sources list
            return QueryResponse(
                question=user_query,
                answer=answer,
                sources=[]
            )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query execution failed: {str(e)}"
        )

