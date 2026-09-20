using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using PublicRead.Data.Repositories.Interfaces;
using PublicRead.Models.DTOs;

namespace PublicRead.Controllers;

[ApiController]
[Route("api/public/modules")]
public class ModulesController : ControllerBase
{
    private readonly IModuleRepository _moduleRepository;
    private readonly IMemoryCache _cache;

    public ModulesController(IModuleRepository moduleRepository, IMemoryCache cache)
    {
        _moduleRepository = moduleRepository;
        _cache = cache;
    }

    [HttpGet]
    [ResponseCache(Duration = 300)]
    public async Task<ActionResult<List<ModuleDto>>> GetAllActiveModules()
    {
        var cacheKey = "modules_all";
        if (!_cache.TryGetValue(cacheKey, out List<ModuleDto>? modules))
        {
            var entities = await _moduleRepository.GetAllActiveModulesAsync();
            modules = entities.Select(e => new ModuleDto
            {
                ID = e.ID,
                Active = e.Active,
                Name = e.Name,
                Description = e.Description,
                Type = e.Type,
                StyleID = e.StyleID,
                StyleClass = e.StyleClass,
                StyleInline = e.StyleInline,
                PageIDs = e.PageIDs,
                CustomSettings = e.CustomSettings,
                SortOrder = e.SortOrder,
                Location = e.Location,
                ModName = e.ModName,
                ModHandler = e.ModHandler,
                ModDescription = e.ModDescription,
                Disabled = e.Disabled
            }).ToList();

            _cache.Set(cacheKey, modules, TimeSpan.FromMinutes(5));
        }

        return Ok(modules);
    }
}
