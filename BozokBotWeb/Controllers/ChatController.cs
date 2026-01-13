using BozokBotWeb.Models;
using BozokBotWeb.Services;
using Microsoft.AspNetCore.Mvc;

namespace BozokBotWeb.Controllers
{
    public class ChatController : Controller
    {
        private readonly IBozokBotService _botService;
        private readonly ILogger<ChatController> _logger;

        public ChatController(IBozokBotService botService, ILogger<ChatController> logger)
        {
            _botService = botService;
            _logger = logger;
        }

        // GET: /Chat
        public IActionResult Index()
        {
            return View(new ChatViewModel());
        }

        // POST: /Chat/Ask
        [HttpPost]
        public async Task<IActionResult> Ask(string question)
        {
            if (string.IsNullOrWhiteSpace(question))
            {
                return View("Index", new ChatViewModel
                {
                    HasError = true,
                    ErrorMessage = "Lütfen bir soru girin."
                });
            }

            var response = await _botService.AskQuestionAsync(question);

            var viewModel = new ChatViewModel
            {
                Question = question,
                Answer = response.Answer,
                Sources = response.Sources,
                HasError = !response.Success,
                ErrorMessage = response.Error
            };

            return View("Index", viewModel);
        }

        // API endpoint for AJAX calls
        [HttpPost]
        public async Task<IActionResult> AskApi([FromBody] ChatRequest request)
        {
            if (string.IsNullOrWhiteSpace(request.Question))
            {
                return BadRequest(new { error = "Soru boş olamaz" });
            }

            var response = await _botService.AskQuestionAsync(request.Question, request.TopK);
            return Json(response);
        }

        // Health check
        public async Task<IActionResult> Health()
        {
            var isHealthy = await _botService.CheckHealthAsync();
            return Json(new { healthy = isHealthy });
        }
    }
}