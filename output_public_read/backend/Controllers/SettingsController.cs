using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using PublicRead.Data.Repositories.Interfaces;
using PublicRead.Models.DTOs;

namespace PublicRead.Controllers;

[ApiController]
[Route("api/public/settings")]
public class SettingsController : ControllerBase
{
    private readonly IGlobalSettingRepository _settingRepository;
    private readonly IMemoryCache _cache;

    public SettingsController(IGlobalSettingRepository settingRepository, IMemoryCache cache)
    {
        _settingRepository = settingRepository;
        _cache = cache;
    }

    [HttpGet]
    [ResponseCache(Duration = 300)]
    public async Task<ActionResult<Dictionary<string, string>>> GetAllSettings()
    {
        var cacheKey = "settings_all";
        if (!_cache.TryGetValue(cacheKey, out Dictionary<string, string>? settings))
        {
            var entities = await _settingRepository.GetAllSettingsAsync();
            settings = entities.ToDictionary(
                e => e.SettingName ?? e.SettingId.ToString(),
                e => e.SettingValue ?? string.Empty
            );

            _cache.Set(cacheKey, settings, TimeSpan.FromMinutes(5));
        }

        return Ok(settings);
    }
}
