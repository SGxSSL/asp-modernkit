using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using PublicRead.Data.Repositories.Interfaces;
using PublicRead.Models.DTOs;

namespace PublicRead.Controllers;

[ApiController]
[Route("api/public/pages")]
public class PagesController : ControllerBase
{
    private readonly IPageRepository _pageRepository;
    private readonly IMemoryCache _cache;

    public PagesController(IPageRepository pageRepository, IMemoryCache cache)
    {
        _pageRepository = pageRepository;
        _cache = cache;
    }

    [HttpGet("{fileName}")]
    [ResponseCache(Duration = 300)]
    public async Task<ActionResult<PageDto>> GetPageByFileName(string fileName)
    {
        var cacheKey = $"page_{fileName}";
        if (!_cache.TryGetValue(cacheKey, out PageDto? page))
        {
            var entity = await _pageRepository.GetPageByFileNameAsync(fileName);
            if (entity == null)
                return NotFound(new { message = $"Page '{fileName}' not found." });

            page = new PageDto
            {
                PageId = entity.PageId,
                Active = entity.Active,
                PageName = entity.PageName,
                PageFileName = entity.PageFileName,
                PageLinkHoverText = entity.PageLinkHoverText,
                PageDescription = entity.PageDescription,
                PageKeywords = entity.PageKeywords,
                MainMenu = entity.MainMenu,
                PageTitle = entity.PageTitle,
                MenuIndex = entity.MenuIndex,
                ParentPageId = entity.ParentPageId,
                Style = entity.Style,
                CreateDate = entity.CreateDate,
                Content = entity.Content,
                ModifiedDate = entity.ModifiedDate
            };

            _cache.Set(cacheKey, page, TimeSpan.FromMinutes(5));
        }

        return Ok(page);
    }

    [HttpGet]
    [ResponseCache(Duration = 300)]
    public async Task<ActionResult<List<PageDto>>> GetAllActivePages()
    {
        var cacheKey = "pages_all";
        if (!_cache.TryGetValue(cacheKey, out List<PageDto>? pages))
        {
            var entities = await _pageRepository.GetAllActivePagesAsync();
            pages = entities.Select(e => new PageDto
            {
                PageId = e.PageId,
                Active = e.Active,
                PageName = e.PageName,
                PageFileName = e.PageFileName,
                PageLinkHoverText = e.PageLinkHoverText,
                PageDescription = e.PageDescription,
                PageKeywords = e.PageKeywords,
                MainMenu = e.MainMenu,
                PageTitle = e.PageTitle,
                MenuIndex = e.MenuIndex,
                ParentPageId = e.ParentPageId,
                Style = e.Style,
                CreateDate = e.CreateDate,
                Content = e.Content,
                ModifiedDate = e.ModifiedDate
            }).ToList();

            _cache.Set(cacheKey, pages, TimeSpan.FromMinutes(5));
        }

        return Ok(pages);
    }
}
