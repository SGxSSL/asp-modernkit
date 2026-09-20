using Microsoft.EntityFrameworkCore;
using PublicRead.Data;
using PublicRead.Data.Entities;
using PublicRead.Data.Repositories.Interfaces;

namespace PublicRead.Data.Repositories;

public class GlobalSettingRepository : IGlobalSettingRepository
{
    private readonly AppDbContext _context;

    public GlobalSettingRepository(AppDbContext context)
    {
        _context = context;
    }

    public async Task<List<GlobalSettingEntity>> GetAllSettingsAsync()
    {
        return await _context.GlobalSettings
            .OrderBy(s => s.SettingCategory)
            .ThenBy(s => s.SortOrder)
            .ToListAsync();
    }
}
