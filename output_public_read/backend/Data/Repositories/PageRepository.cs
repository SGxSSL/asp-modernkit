using Microsoft.EntityFrameworkCore;
using PublicRead.Data;
using PublicRead.Data.Entities;
using PublicRead.Data.Repositories.Interfaces;

namespace PublicRead.Data.Repositories;

public class PageRepository : IPageRepository
{
    private readonly AppDbContext _context;

    public PageRepository(AppDbContext context)
    {
        _context = context;
    }

    public async Task<PageEntity?> GetPageByFileNameAsync(string fileName)
    {
        return await _context.Pages
            .Include(p => p.PageContent)
            .FirstOrDefaultAsync(p => p.PageFileName == fileName && p.Active);
    }

    public async Task<List<PageEntity>> GetAllActivePagesAsync()
    {
        return await _context.Pages
            .Where(p => p.Active)
            .OrderBy(p => p.MenuIndex)
            .ToListAsync();
    }

    public async Task<PageEntity?> GetPageByIdAsync(int pageId)
    {
        return await _context.Pages
            .Include(p => p.PageContent)
            .FirstOrDefaultAsync(p => p.PageId == pageId);
    }
}
