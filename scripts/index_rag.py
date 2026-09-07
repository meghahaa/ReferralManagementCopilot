"""RAG Indexing Script."""

from referral_copilot.rag.tool import ReferralPolicyRAGTool


def index_rag_documents():
    print("Indexing clinical policy documents for Agentic RAG...")
    tool = ReferralPolicyRAGTool()
    print(f"✓ Indexed {len(tool.documents)} document chunks from uploads directory.")
    test_res = tool.query_policy("Cardiology prior authorization")
    print(f"✓ RAG Query Test Passed. Highest relevance score: {test_res.relevance_score}")


if __name__ == "__main__":
    index_rag_documents()
