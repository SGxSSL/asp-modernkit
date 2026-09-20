using PublicRead.Data.Entities;

namespace PublicRead.Data.Repositories.Interfaces;

public interface IGlobalSettingRepository
{
    Task<List<GlobalSettingEntity>> GetAllSettingsAsync();
}
