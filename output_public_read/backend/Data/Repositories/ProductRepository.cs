using Microsoft.EntityFrameworkCore;
using PublicRead.Data;
using PublicRead.Data.Entities;
using PublicRead.Data.Repositories.Interfaces;

namespace PublicRead.Data.Repositories;

public class ProductRepository : IProductRepository
{
    private readonly AppDbContext _context;

    public ProductRepository(AppDbContext context)
    {
        _context = context;
    }

    public async Task<List<ProductEntity>> GetAllActiveProductsAsync()
    {
        return await _context.Products
            .Where(p => p.Active)
            .OrderBy(p => p.ProductName)
            .ToListAsync();
    }

    public async Task<ProductEntity?> GetProductByIdAsync(int id)
    {
        return await _context.Products
            .FirstOrDefaultAsync(p => p.Key == id && p.Active);
    }
}
