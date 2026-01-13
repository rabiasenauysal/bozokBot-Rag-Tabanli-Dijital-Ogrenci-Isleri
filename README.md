# 🎓 BozokBot - RAG Tabanlı Öğrenci İşleri Asistanı

Bozok Üniversitesi öğrencileri için lisans yönergeleri, yaz okulu, tek ders sınavı ve diğer akademik konularda soru-cevap yapabilen yapay zeka destekli chatbot.

## 🏗️ Mimari

- **Backend:** Python + FastAPI + ChromaDB + Gemini AI
- **Frontend:** ASP.NET Core MVC (C#)
- **RAG (Retrieval-Augmented Generation):** Belge tabanlı doğru yanıt üretimi

## 📋 Gereksinimler

### Backend (Python)
- Python 3.10+
- Virtual Environment
- Google Gemini API Key

### Frontend (C#)
- .NET 7.0 veya .NET 8.0
- Visual Studio 2022 veya VS Code

## 🚀 Kurulum

### 1️⃣ Repository'yi Klonla

```bash
git clone https://github.com/KULLANICI_ADIN/bozokbot-project.git
cd bozokbot-project
```

### 2️⃣ Backend Kurulumu

```bash
cd backend

# Virtual environment oluştur
python -m venv venv

# Aktive et (Windows)
venv\Scripts\activate

# Paketleri yükle
pip install -r requirements.txt

# .env dosyası oluştur
copy .env.example .env

# .env dosyasını düzenle ve API key ekle
notepad .env
```

### 3️⃣ PDF'leri Ekle

`backend/pdfs/` klasörüne yönerge PDF'lerini koy.

### 4️⃣ Backend'i Başlat

```bash
python main.py
```

Backend `http://127.0.0.1:8000` adresinde çalışacak.

### 5️⃣ Frontend Kurulumu

```bash
cd ../BozokBotWeb
```

Visual Studio'da `BozokBotWeb.sln` dosyasını aç veya:

```bash
dotnet restore
dotnet run
```

Frontend `https://localhost:7085` (veya 5283) adresinde açılacak.

## 🎯 Kullanım

1. Backend'i başlat (Python)
2. Frontend'i başlat (C# MVC)
3. Tarayıcıda `https://localhost:7085/Chat` aç
4. Sorunuzu yazın!

## 📚 Örnek Sorular

- "Yaz okulunda en fazla kaç AKTS alabilirim?"
- "Tek ders sınavına kimler girebilir?"
- "GANO'su 2.80 olan öğrenci üst yarıyıldan ders alabilir mi?"

## 🔧 Yapılandırma

### Backend (.env)

```bash
GOOGLE_API_KEY=your_actual_api_key
CHROMA_DB_PATH=./chroma_db
COLLECTION_NAME=Yonergeler
EMBEDDING_MODEL=distiluse-base-multilingual-cased-v1
GEMINI_MODEL=gemini-2.5-flash
```

### Frontend (appsettings.json)

```json
{
  "BozokBotApi": {
    "BaseUrl": "http://127.0.0.1:8000"
  }
}
```

## 📄 Lisans

MIT License

## 👥 Katkıda Bulunma

Pull request'ler kabul edilir!

## 📧 İletişim

Sorularınız için issue açabilirsiniz.