

import faiss
import pickle
import numpy as np
import ollama
import os

#  Get embedding from Ollama
def get_local_embedding(text):
    try:
        response = ollama.embeddings(model='all-minilm', prompt=text)
        return response['embedding']
    except Exception as e:
        print(" Embedding Error:", e)
        return None

#  Create and save FAISS index
def setup_rag_index():
    documents = [
    "All devices purchased from our company come with a standard one-year manufacturer warranty that covers hardware defects and malfunctions. Customers must present a valid purchase receipt to claim warranty services. Software issues are not covered unless bundled with device support contracts.",

    "Refunds are processed only within 7 days from the date of delivery and are applicable only if the product is returned in its original packaging and condition. Shipping charges are non-refundable. Refunds may take 5–7 working days to reflect in your bank account.",

    "Our customer support team is available 24/7 via our online portal and support helpline. Support covers device troubleshooting, warranty claims, and general inquiries. Priority support is provided to premium customers. Weekend response times may vary slightly due to high volumes.",

    "Physical or accidental damage such as water exposure, cracked screens, or burns is not covered under the standard warranty. For such cases, customers may opt for a paid repair service or extended accidental damage protection plan if purchased.",

    "If your device has a manufacturing defect, you are eligible for a replacement within the first 30 days from the delivery date. After 30 days, warranty repair will be offered instead of replacement. The replacement process may take up to 7 working days depending on stock availability.",

    "Warranty becomes void if the product is tampered with, rooted, jailbroken, or opened by unauthorized service centers. Please ensure that warranty repairs are only conducted through official service channels provided by us.",

    "Extended warranty plans are available at the time of purchase or within 30 days post-purchase. These plans extend coverage for an additional 1 or 2 years and include all standard warranty benefits, excluding accidental damage unless specifically covered.",

    "You can track your warranty status by logging into your account on our website and entering your device serial number. Any discrepancies should be reported to support within 48 hours of detection.",

    "Refunds for software products are not allowed once the license key has been issued or the software has been activated. Please read the product description carefully before purchasing.",

    "Live chat support is available Monday to Friday from 9 AM to 6 PM. Outside these hours, you can raise a ticket through our support portal and expect a response within 12 hours. Critical support (Level 1 issues) is monitored continuously."
]


    embeddings = []
    valid_docs = []

    for doc in documents:
        emb = get_local_embedding(doc)
        if emb:
            embeddings.append(emb)
            valid_docs.append(doc)

    if not embeddings:
        raise ValueError(" No embeddings were generated.")

    embeddings = np.array(embeddings).astype("float32")
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    with open("rag_faiss_ollama.pkl", "wb") as f:
        pickle.dump((index, valid_docs), f)

    print(" FAISS index created and saved as 'rag_faiss_ollama.pkl'.")

#  Query FAISS and get best matching doc
def query_rag(query):
    try:
        with open("rag_faiss_ollama.pkl", "rb") as f:
            index, docs = pickle.load(f)

        query_emb = get_local_embedding(query)
        if query_emb is None:
            return " Failed to generate embedding for your query."

        query_emb = np.array(query_emb).reshape(1, -1)
        D, I = index.search(query_emb, k=1)
        matched_doc = docs[I[0][0]]

        return f" Relevant Info:\n\n{matched_doc}"
    except Exception as e:
        return f" RAG Error: {e}"
