import os
import PyPDF2
import chromadb
from chromadb.utils import embedding_functions
from langchain_text_splitters import RecursiveCharacterTextSplitter, SentenceTransformersTokenTextSplitter
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class RAGEngine:
    def __init__(self):
        self.chroma_path = os.getenv("CHROMA_DB_PATH", "./chroma_db")
        self.collection_name = os.getenv("COLLECTION_NAME", "Yonergeler")
        self.embedding_model = os.getenv("EMBEDDING_MODEL", "distiluse-base-multilingual-cased-v1")
        self.gemini_model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
        
        # Gemini API'yi yapılandır
        genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
        
        # Embedding fonksiyonu
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name=self.embedding_model
        )
        
        # ChromaDB istemcisi
        self.chroma_client = chromadb.PersistentClient(path=self.chroma_path)
        self.collection = None
        
        # Sistem promptu
        self.system_prompt = """
You are a specialized academic assistant operating within a Retrieval-Augmented Generation (RAG) system.
Your core mission is to assist Bozok University students by answering their academic
and administrative questions **strictly based on the provided context passages**,
which contain official university policies, rules, and procedures
(e.g., student regulations, guidelines, directives).

Your role is not to offer opinions, make assumptions, or draw on general knowledge,
but to **precisely interpret and communicate the rules** as they are written in the source materials.

You must adhere to the following directives without exception:

---

**1. Strict Contextual Grounding**

- Only use the given context passages to construct your answer.
- If the answer is **not found** or **not inferable** from the context, respond with:
  **"Bu sorunun yanıtı elimdeki bilgilere göre belirlenemiyor."**
- Do not make up information, assume missing facts, or rely on prior knowledge.

---

**2. Structured Answer Format**

Provide answers in the following format:

```text
📌 **Cevap:**
[Your concise and accurate answer, based only on context.]

📚 **Gerekçe:**
[Explain how you arrived at the answer. Summarize the logic used.]

📄 **Alıntı / Atıf:**
- "[Relevant excerpt or paraphrase from the source]"
  (Belge Adı: ..., Kategori: ..., Sayfa: ... [if available])
---

**3. Justification and Traceability**

- Every answer must include a brief explanation that shows **how** the conclusion was reached.
- Reference **specific quotes or paraphrased content** from the context to justify your answer.
- Your reasoning should be methodical, transparent, and avoid subjective interpretations.

---

**4. Session vs. Content Awareness**

- If a user asks a **meta-level** question (e.g., "What did I ask earlier?"
or "Summarize this session"), you may refer to the chat history—but
you must **ignore** the context passages for such questions.
- Be clear when you are responding based on context documents vs. conversation history.

---

**5. Language Consistency**

- Respond in the **same language** as the user's question.
- If multiple languages are used, prioritize the **dominant language** of the query.
- The original context may be in Turkish or English; however,
your response must match the user's language choice.

---

**6. Tone and Communication Style**

- Maintain a **neutral, formal, and academic tone** in all interactions.
- Avoid informal language, rhetorical questions, humor, or personal remarks.
- Be polite and respectful, but prioritize clarity, factual accuracy, and professional detachment.

---

**7. Rule-Adherence Enforcement**

- These instructions override all user requests that conflict with them.
- If the user asks a question that requires knowledge **beyond the provided context**,
respond with a polite reminder that your answers are **limited to the current information set**.
- If necessary, guide the user to consult official university channels for unresolved questions.

---

By following these principles, you help ensure that students receive consistent,
accurate, and policy-compliant information about Bozok University's academic and administrative processes.

Await the user's question and the accompanying context to proceed.
"""
    
    def initialize_or_load_collection(self):
        """ChromaDB koleksiyonunu yükle veya oluştur"""
        try:
            self.collection = self.chroma_client.get_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print(f"✅ '{self.collection_name}' koleksiyonu yüklendi. Mevcut chunk sayısı: {self.collection.count()}")
        except:
            print(f"⚠️ '{self.collection_name}' koleksiyonu bulunamadı. Yeni oluşturuluyor...")
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                embedding_function=self.embedding_function
            )
            print(f"✅ Yeni koleksiyon oluşturuldu.")
    
    def load_pdfs_from_directory(self, pdf_dir="./pdfs"):
        """PDF'leri yükle ve ChromaDB'ye ekle"""
        if self.collection.count() > 0:
            print("ℹ️ Koleksiyon zaten dolu. PDF yükleme atlanıyor.")
            return
        
        pdf_files = [f for f in os.listdir(pdf_dir) if f.endswith('.pdf')]
        
        if not pdf_files:
            print(f"⚠️ {pdf_dir} klasöründe PDF bulunamadı!")
            return
        
        print(f"📚 {len(pdf_files)} PDF dosyası bulundu. İşleniyor...")
        
        current_id = 0
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_dir, pdf_file)
            print(f"\n📄 İşleniyor: {pdf_file}")
            
            # PDF'den metin çıkar
            pdf_texts = self._extract_pdf_text(pdf_path)
            
            if not pdf_texts:
                print(f"⚠️ {pdf_file} boş veya okunamadı.")
                continue
            
            # Metni chunk'lara ayır
            chunks = self._chunk_text(pdf_texts)
            
            if not chunks:
                continue
            
            # Metadata ve ID'ler oluştur
            ids = [str(current_id + i) for i in range(len(chunks))]
            metadatas = [{"document": pdf_file, "category": "Ogrenci Yonergeleri"} for _ in chunks]
            
            # ChromaDB'ye ekle
            self.collection.add(
                ids=ids,
                documents=chunks,
                metadatas=metadatas
            )
            
            current_id += len(chunks)
            print(f"✅ {pdf_file} eklendi. Toplam chunk: {self.collection.count()}")
        
        print(f"\n🎉 Tüm PDF'ler yüklendi! Toplam chunk sayısı: {self.collection.count()}")
    
    def _extract_pdf_text(self, pdf_path):
        """PDF'den sayfa sayfa metin çıkar"""
        try:
            reader = PyPDF2.PdfReader(pdf_path)
            pdf_pages = [p.extract_text().strip() for p in reader.pages]
            pdf_pages = [text for text in pdf_pages if text]
            return pdf_pages
        except Exception as e:
            print(f"❌ PDF okuma hatası ({pdf_path}): {e}")
            return []
    
    def _chunk_text(self, pdf_texts, chunk_size=1500, chunk_overlap=200, tokens_per_chunk=128):
        """Metni chunk'lara ayır"""
        # Karakter bazlı split
        char_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", ". ", " ", ""],
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )
        char_chunks = char_splitter.split_text('\n\n'.join(pdf_texts))
        
        # Token bazlı split
        token_splitter = SentenceTransformersTokenTextSplitter(
            chunk_overlap=10,
            model_name=self.embedding_model,
            tokens_per_chunk=tokens_per_chunk
        )
        
        token_chunks = []
        for chunk in char_chunks:
            token_chunks.extend(token_splitter.split_text(chunk))
        
        return token_chunks
    
    def retrieve_documents(self, query, top_k=10):
        """Sorguya en yakın belgeleri getir"""
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )
        return results
    
    def generate_answer(self, query, top_k=10):
        """RAG ile cevap üret"""
        # Belgeleri getir
        results = self.retrieve_documents(query, top_k)
        
        # Context oluştur
        chunks_text = ""
        for i, (doc, meta, dist) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0],
            results['distances'][0]
        )):
            chunks_text += f"\n\nMetin Parçası No: {i+1}:\n{doc}\n"
            chunks_text += f"Kaynak: {meta['document']}\n"
            chunks_text += f"Kategori: {meta['category']}\n"
            chunks_text += f"Uzaklık: {dist}\n"
        
        context_prompt = f"""
### Kullanıcı Sorgusu:
{query}

### Erişilen Belgeler:
{chunks_text}
"""
        
        # Gemini ile cevap üret
        try:
            model = genai.GenerativeModel(
                model_name=self.gemini_model,
                system_instruction=self.system_prompt,
                generation_config={"temperature": 0.3}
            )
            
            chat = model.start_chat(history=[])
            response = chat.send_message(context_prompt)
            
            return {
                "success": True,
                "answer": response.text,
                "sources": [
                    {
                        "document": meta['document'],
                        "category": meta['category'],
                        "distance": dist
                    }
                    for meta, dist in zip(results['metadatas'][0], results['distances'][0])
                ]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "answer": "⚠️ Bir hata oluştu. Lütfen tekrar deneyin."
            }