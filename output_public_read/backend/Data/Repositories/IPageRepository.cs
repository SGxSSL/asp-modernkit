using PublicRead.Data.Entities;

namespace PublicRead.Data.Repositories.Interfaces;

public interface IPageRepository
{
    Task<PageEntity?> GetPageByFileNameAsync(string fileName);
    Task<List<PageEntity>> GetAllActivePagesAsync();
    Task<PageEntity?> GetPageByIdAsync(int pageId);
}
