using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using PublicRead.Data.Repositories.Interfaces;
using PublicRead.Models.DTOs;

namespace PublicRead.Controllers;

[ApiController]
[Route("api/public/products")]
public class ProductsController : ControllerBase
{
    private readonly IProductRepository _productRepository;
    private readonly IMemoryCache _cache;

    public ProductsController(IProductRepository productRepository, IMemoryCache cache)
    {
        _productRepository = productRepository;
        _cache = cache;
    }

    [HttpGet]
    [ResponseCache(Duration = 300)]
    public async Task<ActionResult<List<ProductDto>>> GetAllActiveProducts()
    {
        var cacheKey = "products_all";
        if (!_cache.TryGetValue(cacheKey, out List<ProductDto>? products))
        {
            var entities = await _productRepository.GetAllActiveProductsAsync();
            products = entities.Select(e => new ProductDto
            {
                Key = e.Key,
                PID = e.PID,
                Category = e.Category,
                Brand = e.Brand,
                ProductLine = e.ProductLine,
                ProductName = e.ProductName,
                Options = e.Options,
                ShortDescription = e.ShortDescription,
                LongDescription = e.LongDescription,
                RetailPrice = e.RetailPrice,
                WholesalePrice = e.WholesalePrice,
                Image1 = e.Image1,
                Image2 = e.Image2,
                Active = e.Active,
                Recommended = e.Recommended,
                Timestamp = e.Timestamp
            }).ToList();

            _cache.Set(cacheKey, products, TimeSpan.FromMinutes(5));
        }

        return Ok(products);
    }

    [HttpGet("{id}")]
    [ResponseCache(Duration = 300)]
    public async Task<ActionResult<ProductDto>> GetProductById(int id)
    {
        var cacheKey = $"product_{id}";
        if (!_cache.TryGetValue(cacheKey, out ProductDto? product))
        {
            var entity = await _productRepository.GetProductByIdAsync(id);
            if (entity == null)
                return NotFound(new { message = $"Product with ID {id} not found." });

            product = new ProductDto
            {
                Key = entity.Key,
                PID = entity.PID,
                Category = entity.Category,
                Brand = entity.Brand,
                ProductLine = entity.ProductLine,
                ProductName = entity.ProductName,
                Options = entity.Options,
                ShortDescription = entity.ShortDescription,
                LongDescription = entity.LongDescription,
                RetailPrice = entity.RetailPrice,
                WholesalePrice = entity.WholesalePrice,
                Image1 = entity.Image1,
                Image2 = entity.Image2,
                Active = entity.Active,
                Recommended = entity.Recommended,
                Timestamp = entity.Timestamp
            };

            _cache.Set(cacheKey, product, TimeSpan.FromMinutes(5));
        }

        return Ok(product);
    }
}
