using Newtonsoft.Json;

namespace BozokBotWeb.Models
{
    public class ChatRequest
    {
        [JsonProperty("question")]  // Python API'de "question" bekliyor
        public string Question { get; set; }

        [JsonProperty("top_k")]     // Python API'de "top_k" bekliyor (snake_case)
        public int TopK { get; set; } = 10;
    }

    public class ChatResponse
    {
        [JsonProperty("success")]
        public bool Success { get; set; }

        [JsonProperty("answer")]
        public string Answer { get; set; }

        [JsonProperty("sources")]
        public List<SourceInfo> Sources { get; set; } = new List<SourceInfo>();

        [JsonProperty("error")]
        public string Error { get; set; }
    }

    public class SourceInfo
    {
        [JsonProperty("document")]
        public string Document { get; set; }

        [JsonProperty("category")]
        public string Category { get; set; }

        [JsonProperty("distance")]
        public double Distance { get; set; }
    }

    public class ChatViewModel
    {
        public string Question { get; set; }
        public string Answer { get; set; }
        public List<SourceInfo> Sources { get; set; } = new List<SourceInfo>();
        public bool HasError { get; set; }
        public string ErrorMessage { get; set; }
    }
}