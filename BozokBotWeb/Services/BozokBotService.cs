using BozokBotWeb.Models;
using Newtonsoft.Json;
using System.Text;

namespace BozokBotWeb.Services
{
    public interface IBozokBotService
    {
        Task<ChatResponse> AskQuestionAsync(string question, int topK = 10);
        Task<bool> CheckHealthAsync();
    }

    public class BozokBotService : IBozokBotService
    {
        private readonly HttpClient _httpClient;
        private readonly ILogger<BozokBotService> _logger;
        private const string BASE_URL = "http://127.0.0.1:8000";

        public BozokBotService(HttpClient httpClient, ILogger<BozokBotService> logger)
        {
            _httpClient = httpClient;
            _httpClient.BaseAddress = new Uri(BASE_URL);
            _httpClient.Timeout = TimeSpan.FromSeconds(60); // RAG işlemi zaman alabilir
            _logger = logger;
        }

        public async Task<ChatResponse> AskQuestionAsync(string question, int topK = 10)
        {
            try
            {
                var request = new ChatRequest
                {
                    Question = question,
                    TopK = topK
                };

                var json = JsonConvert.SerializeObject(request);
                var content = new StringContent(json, Encoding.UTF8, "application/json");

                var response = await _httpClient.PostAsync("/ask", content);

                if (response.IsSuccessStatusCode)
                {
                    var responseJson = await response.Content.ReadAsStringAsync();
                    return JsonConvert.DeserializeObject<ChatResponse>(responseJson);
                }
                else
                {
                    _logger.LogError($"API Error: {response.StatusCode}");
                    return new ChatResponse
                    {
                        Success = false,
                        Error = $"API hatası: {response.StatusCode}",
                        Answer = "Üzgünüm, şu anda cevap veremiyorum. Lütfen daha sonra tekrar deneyin."
                    };
                }
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Error calling BozokBot API");
                return new ChatResponse
                {
                    Success = false,
                    Error = ex.Message,
                    Answer = "Bağlantı hatası. Backend çalışıyor mu kontrol edin."
                };
            }
        }

        public async Task<bool> CheckHealthAsync()
        {
            try
            {
                var response = await _httpClient.GetAsync("/health");
                return response.IsSuccessStatusCode;
            }
            catch
            {
                return false;
            }
        }
    }
}