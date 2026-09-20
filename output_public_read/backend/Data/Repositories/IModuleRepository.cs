using PublicRead.Data.Entities;

namespace PublicRead.Data.Repositories.Interfaces;

public interface IModuleRepository
{
    Task<List<ModuleEntity>> GetAllActiveModulesAsync();
}
