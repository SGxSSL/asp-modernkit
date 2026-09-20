using PublicRead.Data.Entities;

namespace PublicRead.Data.Repositories.Interfaces;

public interface IProductRepository
{
    Task<List<ProductEntity>> GetAllActiveProductsAsync();
    Task<ProductEntity?> GetProductByIdAsync(int id);
}
