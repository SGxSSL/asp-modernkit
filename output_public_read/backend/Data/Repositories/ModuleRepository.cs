using Microsoft.EntityFrameworkCore;
using PublicRead.Data;
using PublicRead.Data.Entities;
using PublicRead.Data.Repositories.Interfaces;

namespace PublicRead.Data.Repositories;

public class ModuleRepository : IModuleRepository
{
    private readonly AppDbContext _context;

    public ModuleRepository(AppDbContext context)
    {
        _context = context;
    }

    public async Task<List<ModuleEntity>> GetAllActiveModulesAsync()
    {
        return await _context.Modules
            .Where(m => m.Active && !m.Disabled)
            .Include(m => m.ModuleType)
            .OrderBy(m => m.Location)
            .ThenBy(m => m.SortOrder)
            .ToListAsync();
    }
}
