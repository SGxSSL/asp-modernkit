<file path="backend/PublicRead.csproj">
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
    <Nullable>enable</Nullable>
    <ImplicitUsings>enable</ImplicitUsings>
    <DockerDefaultTargetOS>Linux</DockerDefaultTargetOS>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="10.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="10.0.0" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.Tools" Version="10.0.0">
      <PrivateAssets>all</PrivateAssets>
      <IncludeAssets>runtime; build; native; contentfiles; analyzers; buildtransitive</IncludeAssets>
    </PackageReference>
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.6.2" />
    <PackageReference Include="System.Text.Json" Version="10.0.0" />
  </ItemGroup>
</Project>
</file>

<file path="backend/appsettings.json">
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  },
  "AllowedHosts": "*",
  "ConnectionStrings": {
    "DefaultConnection": "Server=localhost;Database=PublicReadDb;Trusted_Connection=True;TrustServerCertificate=True;MultipleActiveResultSets=true"
  },
  "Cors": {
    "AllowedOrigins": "http://localhost:3000,http://localhost:5173"
  }
}
</file>

<file path="backend/Program.cs">
using Microsoft.EntityFrameworkCore;
using PublicRead.Data;
using PublicRead.Data.Repositories;
using PublicRead.Data.Repositories.Interfaces;
using Microsoft.OpenApi.Models;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers().AddJsonOptions(options =>
{
    options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
    options.JsonSerializerOptions.WriteIndented = true;
    options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
});

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "Public Read API", Version = "v1.0.0" });
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = SecuritySchemeType.Http,
        Scheme = "Bearer",
        BearerFormat = "JWT",
        In = ParameterLocation.Header
    });
});

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseSqlServer(builder.Configuration.GetConnectionString("DefaultConnection")));

builder.Services.AddScoped<IPageRepository, PageRepository>();
builder.Services.AddScoped<IProductRepository, ProductRepository>();
builder.Services.AddScoped<ITestimonialRepository, TestimonialRepository>();
builder.Services.AddScoped<IGlobalSettingRepository, GlobalSettingRepository>();
builder.Services.AddScoped<IModuleRepository, ModuleRepository>();

builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowFrontend", policy =>
    {
        policy.WithOrigins(builder.Configuration.GetSection("Cors:AllowedOrigins").Get<string[]>() ?? ["http://localhost:3000"])
              .AllowAnyMethod()
              .AllowAnyHeader();
    });
});

builder.Services.AddResponseCaching();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI(c => c.SwaggerEndpoint("/swagger/v1/swagger.json", "Public Read API v1.0.0"));
}

app.UseHttpsRedirection();
app.UseCors("AllowFrontend");
app.UseAuthorization();
app.MapControllers();
app.UseResponseCaching();

app.Run();
</file>

<file path="backend/Data/AppDbContext.cs">
using Microsoft.EntityFrameworkCore;
using PublicRead.Data.Entities;

namespace PublicRead.Data;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<PageEntity> Pages { get; set; }
    public DbSet<PageContentEntity> PageContents { get; set; }
    public DbSet<ProductEntity> Products { get; set; }
    public DbSet<TestimonialEntity> Testimonials { get; set; }
    public DbSet<GlobalSettingEntity> GlobalSettings { get; set; }
    public DbSet<ModuleEntity> Modules { get; set; }
    public DbSet<ModuleTypeEntity> ModuleTypes { get; set; }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<PageEntity>(entity =>
        {
            entity.HasKey(e => e.PageId);
            entity.Property(e => e.PageName).IsRequired().HasMaxLength(255);
            entity.Property(e => e.PageFileName).IsRequired().HasMaxLength(255);
            entity.Property(e => e.PageTitle).HasMaxLength(500);
            entity.Property(e => e.PageDescription).HasMaxLength(2000);
            entity.Property(e => e.PageKeywords).HasMaxLength(1000);
            entity.Property(e => e.Style).HasMaxLength(100);
            entity.Property(e => e.PageLinkHoverText).HasMaxLength(500);
            entity.HasOne(e => e.PageContent)
                .WithOne()
                .HasForeignKey<PageContentEntity>(pc => pc.PageId)
                .OnDelete(DeleteBehavior.Cascade);
            entity.Property(e => e.CreateDate).HasColumnType("datetime2");
            entity.Property(e => e.ModifiedDate).HasColumnType("datetime2");
        });

        modelBuilder.Entity<PageContentEntity>(entity =>
        {
            entity.HasKey(e => e.ContentId);
            entity.Property(e => e.PageContent).IsRequired();
            entity.Property(e => e.ModifiedDate).HasColumnType("datetime2");
        });

        modelBuilder.Entity<ProductEntity>(entity =>
        {
            entity.HasKey(e => e.Key);
            entity.Property(e => e.PID).HasMaxLength(100);
            entity.Property(e => e.Category).HasMaxLength(255);
            entity.Property(e => e.Brand).HasMaxLength(255);
            entity.Property(e => e.ProductLine).HasMaxLength(255);
            entity.Property(e => e.ProductName).HasMaxLength(500);
            entity.Property(e => e.Options).HasMaxLength(2000);
            entity.Property(e => e.ShortDescription).HasMaxLength(2000);
            entity.Property(e => e.LongDescription).HasMaxLength(MAX);
            entity.Property(e => e.Image1).HasMaxLength(500);
            entity.Property(e => e.Image2).HasMaxLength(500);
            entity.Property(e => e.Timestamp).HasColumnType("datetime2");
            entity.Property(e => e.RetailPrice).HasColumnType("decimal(18,2)");
            entity.Property(e => e.WholesalePrice).HasColumnType("decimal(18,2)");
        });

        modelBuilder.Entity<TestimonialEntity>(entity =>
        {
            entity.HasKey(e => e.ID);
            entity.Property(e => e.Name).HasMaxLength(255);
            entity.Property(e => e.Email).HasMaxLength(255);
            entity.Property(e => e.Location).HasMaxLength(255);
            entity.Property(e => e.Comments).HasMaxLength(MAX);
            entity.Property(e => e.TestimonialDate).HasColumnType("datetime2");
            entity.Property(e => e.Timestamp).HasColumnType("datetime2");
        });

        modelBuilder.Entity<GlobalSettingEntity>(entity =>
        {
            entity.HasKey(e => e.SettingId);
            entity.Property(e => e.SettingCategory).HasMaxLength(255);
            entity.Property(e => e.SettingName).HasMaxLength(255);
            entity.Property(e => e.SettingValue).HasMaxLength(MAX);
            entity.Property(e => e.ValueType).HasMaxLength(50);
            entity.Property(e => e.ValidationRule).HasMaxLength(500);
            entity.Property(e => e.SettingDescription).HasMaxLength(2000);
            entity.Property(e => e.CreationDate).HasColumnType("datetime2");
            entity.Property(e => e.ModifiedDate).HasColumnType("datetime2");
        });

        modelBuilder.Entity<ModuleEntity>(entity =>
        {
            entity.HasKey(e => e.ID);
            entity.Property(e => e.Name).HasMaxLength(255);
            entity.Property(e => e.Description).HasMaxLength(2000);
            entity.Property(e => e.StyleID).HasMaxLength(100);
            entity.Property(e => e.StyleClass).HasMaxLength(255);
            entity.Property(e => e.StyleInline).HasMaxLength(2000);
            entity.Property(e => e.PageIDs).HasMaxLength(2000);
            entity.Property(e => e.CustomSettings).HasMaxLength(MAX);
            entity.Property(e => e.Location).HasMaxLength(100);
            entity.Property(e => e.ModName).HasMaxLength(255);
            entity.Property(e => e.ModHandler).HasMaxLength(500);
            entity.Property(e => e.ModDescription).HasMaxLength(2000);
            entity.HasOne(e => e.ModuleType)
                .WithMany()
                .HasForeignKey(e => e.Type)
                .OnDelete(DeleteBehavior.Restrict);
        });

        modelBuilder.Entity<ModuleTypeEntity>(entity =>
        {
            entity.HasKey(e => e.ModID);
            entity.Property(e => e.ModName).HasMaxLength(255);
            entity.Property(e => e.ModHandler).HasMaxLength(500);
            entity.Property(e => e.ModDescription).HasMaxLength(2000);
        });
    }
}
</file>

<file path="backend/Data/Entities/PageEntity.cs">
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PublicRead.Data.Entities;

[Table("tblPages")]
public class PageEntity
{
    [Key]
    [Column("PageID")]
    public int PageId { get; set; }

    [Column("Active")]
    public bool Active { get; set; }

    [Required]
    [MaxLength(255)]
    [Column("PageName")]
    public string PageName { get; set; } = string.Empty;

    [Required]
    [MaxLength(255)]
    [Column("PageFileName")]
    public string PageFileName { get; set; } = string.Empty;

    [MaxLength(500)]
    [Column("PageLinkHoverText")]
    public string? PageLinkHoverText { get; set; }

    [MaxLength(2000)]
    [Column("PageDescription")]
    public string? PageDescription { get; set; }

    [MaxLength(1000)]
    [Column("PageKeywords")]
    public string? PageKeywords { get; set; }

    [Column("MainMenu")]
    public bool MainMenu { get; set; }

    [MaxLength(500)]
    [Column("PageTitle")]
    public string? PageTitle { get; set; }

    [Column("MenuIndex")]
    public int MenuIndex { get; set; }

    [Column("ParentPage")]
    public int? ParentPageId { get; set; }

    [MaxLength(100)]
    [Column("Style")]
    public string? Style { get; set; }

    [Column("CreateDate")]
    public DateTime CreateDate { get; set; }

    [Column("ModifiedDate")]
    public DateTime? ModifiedDate { get; set; }

    [NotMapped]
    public string? Content { get; set; }
}

[Table("tblPageContent")]
public class PageContentEntity
{
    [Key]
    [Column("ContentID")]
    public int ContentId { get; set; }

    [Column("PageID")]
    public int PageId { get; set; }

    [Column("PageContent")]
    public string PageContent { get; set; } = string.Empty;

    [Column("ModifiedDate")]
    public DateTime ModifiedDate { get; set; }
}
</file>

<file path="backend/Data/Entities/ProductEntity.cs">
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PublicRead.Data.Entities;

[Table("tblProducts")]
public class ProductEntity
{
    [Key]
    public int Key { get; set; }

    [MaxLength(100)]
    public string PID { get; set; } = string.Empty;

    [MaxLength(255)]
    public string Category { get; set; } = string.Empty;

    [MaxLength(255)]
    public string Brand { get; set; } = string.Empty;

    [MaxLength(255)]
    public string ProductLine { get; set; } = string.Empty;

    [MaxLength(500)]
    public string ProductName { get; set; } = string.Empty;

    [MaxLength(2000)]
    public string? Options { get; set; }

    [MaxLength(2000)]
    public string? ShortDescription { get; set; }

    public string? LongDescription { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal RetailPrice { get; set; }

    [Column(TypeName = "decimal(18,2)")]
    public decimal WholesalePrice { get; set; }

    [MaxLength(500)]
    public string? Image1 { get; set; }

    [MaxLength(500)]
    public string? Image2 { get; set; }

    public bool Active { get; set; }

    public bool Recommended { get; set; }

    [Column(TypeName = "datetime2")]
    public DateTime Timestamp { get; set; }
}
</file>

<file path="backend/Data/Entities/TestimonialEntity.cs">
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PublicRead.Data.Entities;

[Table("tblTestimonials")]
public class TestimonialEntity
{
    [Key]
    public int ID { get; set; }

    public bool Active { get; set; }

    [MaxLength(255)]
    public string Name { get; set; } = string.Empty;

    [MaxLength(255)]
    public string? Email { get; set; }

    public bool ShowEmail { get; set; }

    public int SortOrder { get; set; }

    public string? Comments { get; set; }

    [MaxLength(255)]
    public string? Location { get; set; }

    [Column(TypeName = "datetime2")]
    public DateTime TestimonialDate { get; set; }

    [Column(TypeName = "datetime2")]
    public DateTime Timestamp { get; set; }
}
</file>

<file path="backend/Data/Entities/GlobalSettingEntity.cs">
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PublicRead.Data.Entities;

[Table("tblGlobalSettings")]
public class GlobalSettingEntity
{
    [Key]
    public int SettingId { get; set; }

    [MaxLength(255)]
    public string? SettingCategory { get; set; }

    [MaxLength(255)]
    public string? SettingName { get; set; }

    public string? SettingValue { get; set; }

    [MaxLength(50)]
    public string? ValueType { get; set; }

    [MaxLength(500)]
    public string? ValidationRule { get; set; }

    [MaxLength(2000)]
    public string? SettingDescription { get; set; }

    public int SortOrder { get; set; }

    [Column(TypeName = "datetime2")]
    public DateTime CreationDate { get; set; }

    [Column(TypeName = "datetime2")]
    public DateTime? ModifiedDate { get; set; }
}
</file>

<file path="backend/Data/Entities/ModuleEntity.cs">
using System.ComponentModel.DataAnnotations;
using System.ComponentModel.DataAnnotations.Schema;

namespace PublicRead.Data.Entities;

[Table("tblModules")]
public class ModuleEntity
{
    [Key]
    public int ID { get; set; }

    public bool Active { get; set; }

    [MaxLength(255)]
    public string Name { get; set; } = string.Empty;

    public string? Description { get; set; }

    public int Type { get; set; }

    [MaxLength(100)]
    public string? StyleID { get; set; }

    [MaxLength(255)]
    public string? StyleClass { get; set; }

    public string? StyleInline { get; set; }

    [MaxLength(2000)]
    public string? PageIDs { get; set; }

    public string? CustomSettings { get; set; }

    public int SortOrder { get; set; }

    [MaxLength(100)]
    public string? Location { get; set; }

    [MaxLength(255)]
    public string? ModName { get; set; }

    [MaxLength(500)]
    public string? ModHandler { get; set; }

    [MaxLength(2000)]
    public string? ModDescription { get; set; }

    public bool Disabled { get; set; }

    [ForeignKey("Type")]
    public ModuleTypeEntity? ModuleType { get; set; }
}

[Table("tblModuleTypes")]
public class ModuleTypeEntity
{
    [Key]
    public int ModID { get; set; }

    public bool Disabled { get; set; }

    [MaxLength(255)]
    public string? ModName { get; set; }

    [MaxLength(500)]
    public string? ModHandler { get; set; }

    [MaxLength(2000)]
    public string? ModDescription { get; set; }
}
</file>

<file path="backend/Data/Repositories/IPageRepository.cs">
using PublicRead.Data.Entities;

namespace PublicRead.Data.Repositories.Interfaces;

public interface IPageRepository
{
    Task<PageEntity?> GetPageByFileNameAsync(string fileName);
    Task<List<PageEntity>> GetAllActivePagesAsync();
    Task<PageEntity?> GetPageByIdAsync(int pageId);
}
</file>

<file path="backend/Data/Repositories/PageRepository.cs">
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
</file>

<file path="backend/Data/Repositories/IProductRepository.cs">
using PublicRead.Data.Entities;

namespace PublicRead.Data.Repositories.Interfaces;

public interface IProductRepository
{
    Task<List<ProductEntity>> GetAllActiveProductsAsync();
    Task<ProductEntity?> GetProductByIdAsync(int id);
}
</file>

<file path="backend/Data/Repositories/ProductRepository.cs">
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
</file>

<file path="backend/Data/Repositories/ITestimonialRepository.cs">
using PublicRead.Data.Entities;

namespace PublicRead.Data.Repositories.Interfaces;

public interface ITestimonialRepository
{
    Task<List<TestimonialEntity>> GetAllActiveTestimonialsAsync();
}
</file>

<file path="backend/Data/Repositories/TestimonialRepository.cs">
using Microsoft.EntityFrameworkCore;
using PublicRead.Data;
using PublicRead.Data.Entities;
using PublicRead.Data.Repositories.Interfaces;

namespace PublicRead.Data.Repositories;

public class TestimonialRepository : ITestimonialRepository
{
    private readonly AppDbContext _context;

    public TestimonialRepository(AppDbContext context)
    {
        _context = context;
    }

    public async Task<List<TestimonialEntity>> GetAllActiveTestimonialsAsync()
    {
        return await _context.Testimonials
            .Where(t => t.Active)
            .OrderBy(t => t.SortOrder)
            .ToListAsync();
    }
}
</file>

<file path="backend/Data/Repositories/IGlobalSettingRepository.cs">
using PublicRead.Data.Entities;

namespace PublicRead.Data.Repositories.Interfaces;

public interface IGlobalSettingRepository
{
    Task<List<GlobalSettingEntity>> GetAllSettingsAsync();
}
</file>

<file path="backend/Data/Repositories/GlobalSettingRepository.cs">
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
</file>

<file path="backend/Data/Repositories/IModuleRepository.cs">
using PublicRead.Data.Entities;

namespace PublicRead.Data.Repositories.Interfaces;

public interface IModuleRepository
{
    Task<List<ModuleEntity>> GetAllActiveModulesAsync();
}
</file>

<file path="backend/Data/Repositories/ModuleRepository.cs">
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
</file>

<file path="backend/Models/DTOs/PageDto.cs">
namespace PublicRead.Models.DTOs;

public class PageDto
{
    public int PageId { get; set; }
    public bool Active { get; set; }
    public string PageName { get; set; } = string.Empty;
    public string PageFileName { get; set; } = string.Empty;
    public string? PageLinkHoverText { get; set; }
    public string? PageDescription { get; set; }
    public string? PageKeywords { get; set; }
    public bool MainMenu { get; set; }
    public string? PageTitle { get; set; }
    public int MenuIndex { get; set; }
    public int? ParentPageId { get; set; }
    public string? Style { get; set; }
    public DateTime CreateDate { get; set; }
    public string? Content { get; set; }
    public DateTime? ModifiedDate { get; set; }
}
</file>

<file path="backend/Models/DTOs/ProductDto.cs">
namespace PublicRead.Models.DTOs;

public class ProductDto
{
    public int Key { get; set; }
    public string PID { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public string Brand { get; set; } = string.Empty;
    public string ProductLine { get; set; } = string.Empty;
    public string ProductName { get; set; } = string.Empty;
    public string? Options { get; set; }
    public string? ShortDescription { get; set; }
    public string? LongDescription { get; set; }
    public decimal RetailPrice { get; set; }
    public decimal WholesalePrice { get; set; }
    public string? Image1 { get; set; }
    public string? Image2 { get; set; }
    public bool Active { get; set; }
    public bool Recommended { get; set; }
    public DateTime Timestamp { get; set; }
}
</file>

<file path="backend/Models/DTOs/TestimonialDto.cs">
namespace PublicRead.Models.DTOs;

public class TestimonialDto
{
    public int ID { get; set; }
    public bool Active { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Email { get; set; }
    public bool ShowEmail { get; set; }
    public int SortOrder { get; set; }
    public string? Comments { get; set; }
    public string? Location { get; set; }
    public DateTime TestimonialDate { get; set; }
    public DateTime Timestamp { get; set; }
}
</file>

<file path="backend/Models/DTOs/GlobalSettingDto.cs">
namespace PublicRead.Models.DTOs;

public class GlobalSettingDto
{
    public int SettingId { get; set; }
    public string? SettingCategory { get; set; }
    public string? SettingName { get; set; }
    public string? SettingValue { get; set; }
    public string? ValueType { get; set; }
    public string? ValidationRule { get; set; }
    public string? SettingDescription { get; set; }
    public int SortOrder { get; set; }
    public DateTime CreationDate { get; set; }
    public DateTime? ModifiedDate { get; set; }
}
</file>

<file path="backend/Models/DTOs/ModuleDto.cs">
namespace PublicRead.Models.DTOs;

public class ModuleDto
{
    public int ID { get; set; }
    public bool Active { get; set; }
    public string Name { get; set; } = string.Empty;
    public string? Description { get; set; }
    public int Type { get; set; }
    public string? StyleID { get; set; }
    public string? StyleClass { get; set; }
    public string? StyleInline { get; set; }
    public string? PageIDs { get; set; }
    public string? CustomSettings { get; set; }
    public int SortOrder { get; set; }
    public string? Location { get; set; }
    public string? ModName { get; set; }
    public string? ModHandler { get; set; }
    public string? ModDescription { get; set; }
    public bool Disabled { get; set; }
}
</file>

<file path="backend/Controllers/PagesController.cs">
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
</file>

<file path="backend/Controllers/ProductsController.cs">
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
</file>

<file path="backend/Controllers/TestimonialsController.cs">
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using PublicRead.Data.Repositories.Interfaces;
using PublicRead.Models.DTOs;

namespace PublicRead.Controllers;

[ApiController]
[Route("api/public/testimonials")]
public class TestimonialsController : ControllerBase
{
    private readonly ITestimonialRepository _testimonialRepository;
    private readonly IMemoryCache _cache;

    public TestimonialsController(ITestimonialRepository testimonialRepository, IMemoryCache cache)
    {
        _testimonialRepository = testimonialRepository;
        _cache = cache;
    }

    [HttpGet]
    [ResponseCache(Duration = 300)]
    public async Task<ActionResult<List<TestimonialDto>>> GetAllActiveTestimonials()
    {
        var cacheKey = "testimonials_all";
        if (!_cache.TryGetValue(cacheKey, out List<TestimonialDto>? testimonials))
        {
            var entities = await _testimonialRepository.GetAllActiveTestimonialsAsync();
            testimonials = entities.Select(e => new TestimonialDto
            {
                ID = e.ID,
                Active = e.Active,
                Name = e.Name,
                Email = e.Email,
                ShowEmail = e.ShowEmail,
                SortOrder = e.SortOrder,
                Comments = e.Comments,
                Location = e.Location,
                TestimonialDate = e.TestimonialDate,
                Timestamp = e.Timestamp
            }).ToList();

            _cache.Set(cacheKey, testimonials, TimeSpan.FromMinutes(5));
        }

        return Ok(testimonials);
    }
}
</file>

<file path="backend/Controllers/SettingsController.cs">
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using PublicRead.Data.Repositories.Interfaces;
using PublicRead.Models.DTOs;

namespace PublicRead.Controllers;

[ApiController]
[Route("api/public/settings")]
public class SettingsController : ControllerBase
{
    private readonly IGlobalSettingRepository _settingRepository;
    private readonly IMemoryCache _cache;

    public SettingsController(IGlobalSettingRepository settingRepository, IMemoryCache cache)
    {
        _settingRepository = settingRepository;
        _cache = cache;
    }

    [HttpGet]
    [ResponseCache(Duration = 300)]
    public async Task<ActionResult<Dictionary<string, string>>> GetAllSettings()
    {
        var cacheKey = "settings_all";
        if (!_cache.TryGetValue(cacheKey, out Dictionary<string, string>? settings))
        {
            var entities = await _settingRepository.GetAllSettingsAsync();
            settings = entities.ToDictionary(
                e => e.SettingName ?? e.SettingId.ToString(),
                e => e.SettingValue ?? string.Empty
            );

            _cache.Set(cacheKey, settings, TimeSpan.FromMinutes(5));
        }

        return Ok(settings);
    }
}
</file>

<file path="backend/Controllers/ModulesController.cs">
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using PublicRead.Data.Repositories.Interfaces;
using PublicRead.Models.DTOs;

namespace PublicRead.Controllers;

[ApiController]
[Route("api/public/modules")]
public class ModulesController : ControllerBase
{
    private readonly IModuleRepository _moduleRepository;
    private readonly IMemoryCache _cache;

    public ModulesController(IModuleRepository moduleRepository, IMemoryCache cache)
    {
        _moduleRepository = moduleRepository;
        _cache = cache;
    }

    [HttpGet]
    [ResponseCache(Duration = 300)]
    public async Task<ActionResult<List<ModuleDto>>> GetAllActiveModules()
    {
        var cacheKey = "modules_all";
        if (!_cache.TryGetValue(cacheKey, out List<ModuleDto>? modules))
        {
            var entities = await _moduleRepository.GetAllActiveModulesAsync();
            modules = entities.Select(e => new ModuleDto
            {
                ID = e.ID,
                Active = e.Active,
                Name = e.Name,
                Description = e.Description,
                Type = e.Type,
                StyleID = e.StyleID,
                StyleClass = e.StyleClass,
                StyleInline = e.StyleInline,
                PageIDs = e.PageIDs,
                CustomSettings = e.CustomSettings,
                SortOrder = e.SortOrder,
                Location = e.Location,
                ModName = e.ModName,
                ModHandler = e.ModHandler,
                ModDescription = e.ModDescription,
                Disabled = e.Disabled
            }).ToList();

            _cache.Set(cacheKey, modules, TimeSpan.FromMinutes(5));
        }

        return Ok(modules);
    }
}
</file>

<file path="frontend/package.json">
{
  "name": "public-read-frontend",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext ts,tsx"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.26.0",
    "axios": "^1.7.2",
    "dompurify": "^3.1.6"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@types/dompurify": "^3.0.5",
    "@vitejs/plugin-react": "^4.3.1",
    "typescript": "^5.5.3",
    "vite": "^5.4.0",
    "eslint": "^9.9.0",
    "@typescript-eslint/eslint-plugin": "^8.2.0",
    "@typescript-eslint/parser": "^8.2.0"
  }
}
</file>

<file path="frontend/tsconfig.json">
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "isolatedModules": true,
    "moduleDetection": "force",
    "noEmit": true,
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "erasableSyntaxOnly": true,
    "noFallthroughCasesInSwitch": true,
    "noUncheckedSideEffectImports": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "resolveJsonModule": true,
    "paths": {
      "@/*": ["./src/*"]
    },
    "baseUrl": "."
  },
  "include": ["src"]
}
</file>

<file path="frontend/vite.config.ts">
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
      },
    },
  },
});
</file>

<file path="frontend/index.html">
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <meta name="description" content="Public Read CMS" />
    <title>Public Read CMS</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>
</file>

<file path="frontend/src/main.tsx">
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import './styles/global.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <App />
    </BrowserRouter>
  </React.StrictMode>
);
</file>

<file path="frontend/src/services/api.ts">
import axios from 'axios';

const apiClient = axios.create({
  baseURL: '/api/public',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    Accept: 'application/json',
  },
});

apiClient.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response?.status === 404) {
      console.error('Resource not found:', error.config.url);
    } else if (error.response?.status >= 500) {
      console.error('Server error:', error.response.status);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
</file>

<file path="frontend/src/services/pageService.ts">
import apiClient from './api';
import { PageDto } from '../types';

export const pageService = {
  getPageByFileName: (fileName: string): Promise<PageDto> =>
    apiClient.get(`/pages/${fileName}`).then((res) => res.data),

  getAllActivePages: (): Promise<PageDto[]> =>
    apiClient.get('/pages').then((res) => res.data),
};
</file>

<file path="frontend/src/services/productService.ts">
import apiClient from './api';
import { ProductDto } from '../types';

export const productService = {
  getAllActiveProducts: (): Promise<ProductDto[]> =>
    apiClient.get('/products').then((res) => res.data),

  getProductById: (id: number): Promise<ProductDto> =>
    apiClient.get(`/products/${id}`).then((res) => res.data),
};
</file>

<file path="frontend/src/services/testimonialService.ts">
import apiClient from './api';
import { TestimonialDto } from '../types';

export const testimonialService = {
  getAllActiveTestimonials: (): Promise<TestimonialDto[]> =>
    apiClient.get('/testimonials').then((res) => res.data),
};
</file>

<file path="frontend/src/services/settingsService.ts">
import apiClient from './api';

export const settingsService = {
  getAllSettings: (): Promise<Record<string, string>> =>
    apiClient.get('/settings').then((res) => res.data),
};
</file>

<file path="frontend/src/services/moduleService.ts">
import apiClient from './api';
import { ModuleDto } from '../types';

export const moduleService = {
  getAllActiveModules: (): Promise<ModuleDto[]> =>
    apiClient.get('/modules').then((res) => res.data),
};
</file>

<file path="frontend/src/types/index.ts">
export interface PageDto {
  pageId: number;
  active: boolean;
  pageName: string;
  pageFileName: string;
  pageLinkHoverText: string | null;
  pageDescription: string | null;
  pageKeywords: string | null;
  mainMenu: boolean;
  pageTitle: string | null;
  menuIndex: number;
  parentPageId: number | null;
  style: string | null;
  createDate: string;
  content: string | null;
  modifiedDate: string | null;
}

export interface ProductDto {
  key: number;
  pid: string;
  category: string;
  brand: string;
  productLine: string;
  productName: string;
  options: string | null;
  shortDescription: string | null;
  longDescription: string | null;
  retailPrice: number;
  wholesalePrice: number;
  image1: string | null;
  image2: string | null;
  active: boolean;
  recommended: boolean;
  timestamp: string;
}

export interface TestimonialDto {
  id: number;
  active: boolean;
  name: string;
  email: string | null;
  showEmail: boolean;
  sortOrder: number;
  comments: string | null;
  location: string | null;
  testimonialDate: string;
  timestamp: string;
}

export interface GlobalSettingDto {
  settingId: number;
  settingCategory: string | null;
  settingName: string | null;
  settingValue: string | null;
  valueType: string | null;
  validationRule: string | null;
  settingDescription: string | null;
  sortOrder: number;
  creationDate: string;
  modifiedDate: string | null;
}

export interface ModuleDto {
  id: number;
  active: boolean;
  name: string;
  description: string | null;
  type: number;
  styleId: string | null;
  styleClass: string | null;
  styleInline: string | null;
  pageIds: string | null;
  customSettings: string | null;
  sortOrder: number;
  location: string | null;
  modName: string | null;
  modHandler: string | null;
  modDescription: string | null;
  disabled: boolean;
}
</file>

<file path="frontend/src/utils/sanitizer.ts">
import DOMPurify from 'dompurify';

export function sanitizeHtml(dirty: string): string {
  return DOMPurify.sanitize(dirty, {
    ALLOWED_TAGS: [
      'p', 'br', 'strong', 'em', 'b', 'i', 'u', 'span', 'div',
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'ul', 'ol', 'li', 'a', 'img', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
      'blockquote', 'code', 'pre', 'hr', 'br',
      'figure', 'figcaption', 'video', 'audio', 'source',
      'iframe', 'object', 'param', 'embed',
      'form', 'input', 'label', 'select', 'option', 'textarea', 'button',
      'section', 'article', 'header', 'footer', 'nav', 'aside', 'main',
      'details', 'summary', 'mark', 'small', 'sub', 'sup', 'del', 'ins',
    ],
    ALLOWED_ATTR: [
      'class', 'id', 'style', 'href', 'src', 'alt', 'title', 'width', 'height',
      'name', 'type', 'value', 'placeholder', 'checked', 'disabled', 'selected',
      'target', 'rel', 'colspan', 'rowspan', 'datetime', 'cite',
    ],
    ALLOW_DATA_ATTR: false,
    FORBID_TAGS: ['script', 'style', 'form', 'input', 'iframe', 'object', 'embed'],
    FORBID_ATTR: ['onclick', 'onerror', 'onload', 'onmouseover', 'onfocus', 'onblur'],
  });
}

export function sanitizeUrl(url: string): string {
  try {
    const parsed = new URL(url, window.location.origin);
    if (parsed.protocol === 'http:' || parsed.protocol === 'https:' || parsed.protocol === '') {
      return url;
    }
    return '';
  } catch {
    return '';
  }
}
</file>

<file path="frontend/src/utils/helpers.ts">
export function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
}

export function formatRelativeDate(dateString: string): string {
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffSecs = Math.floor(diffMs / 1000);
  const diffMins = Math.floor(diffSecs / 60);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffDays > 365) return `${Math.floor(diffDays / 365)} year(s) ago`;
  if (diffDays > 30) return `${Math.floor(diffDays / 30)} month(s) ago`;
  if (diffDays > 0) return `${diffDays} day(s) ago`;
  if (diffHours > 0) return `${diffHours} hour(s) ago`;
  if (diffMins > 0) return `${diffMins} minute(s) ago`;
  return 'Just now';
}

export function truncate(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength).trim() + '...';
}

export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

export function slugify(str: string): string {
  return str
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/(^-|-$)/g, '');
}
</file>

<file path="frontend/src/hooks/useApi.ts">
import { useState, useEffect, useCallback } from 'react';

interface UseApiResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

export function useApi<T>(
  fetchFn: () => Promise<T>,
  deps: unknown[] = []
): UseApiResult<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred');
    } finally {
      setLoading(false);
    }
  }, deps);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
}
</file>

<file path="frontend/src/contexts/AppContext.tsx">
import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { settingsService } from '../services/settingsService';

interface AppContextType {
  settings: Record<string, string>;
  loading: boolean;
  error: string | null;
}

const AppContext = createContext<AppContextType>({
  settings: {},
  loading: true,
  error: null,
});

export const useAppContext = () => useContext(AppContext);

interface AppProviderProps {
  children: ReactNode;
}

export const AppProvider: React.FC<AppProviderProps> = ({ children }) => {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    settingsService
      .getAllSettings()
      .then((data) => {
        setSettings(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, []);

  return (
    <AppContext.Provider value={{ settings, loading, error }}>
      {children}
    </AppContext.Provider>
  );
};
</file>

<file path="frontend/src/components/Navigation.tsx">
import React from 'react';
import { NavLink } from 'react-router-dom';
import { pageService } from '../services/pageService';
import { useAppContext } from '../contexts/AppContext';

const Navigation: React.FC = () => {
  const { settings } = useAppContext();
  const [pages, setPages] = React.useState<Array<{ pageFileName: string; pageName: string; pageLinkHoverText: string; mainMenu: boolean }>>([]);
  const [loading, setLoading] = React.useState(true);

  React.useEffect(() => {
    pageService
      .getAllActivePages()
      .then((data) => {
        const menuPages = data.filter((p) => p.mainMenu).sort((a, b) => a.menuIndex - b.menuIndex);
        setPages(menuPages);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return <nav className="navigation"><span>Loading navigation...</span></nav>;
  }

  return (
    <nav className="navigation" aria-label="Main navigation">
      <ul className="nav-menu">
        {pages.map((page) => (
          <li key={page.pageFileName}>
            <NavLink
              to={`/${page.pageFileName === 'default' ? '' : page.pageFileName}`}
              title={page.pageLinkHoverText || page.pageName}
              className={({ isActive }) => (isActive ? 'nav-link active' : 'nav-link')}
            >
              {page.pageName}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Navigation;
</file>

<file path="frontend/src/components/Header.tsx">
import React from 'react';
import { useAppContext } from '../contexts/AppContext';
import Navigation from './Navigation';

const Header: React.FC = () => {
  const { settings } = useAppContext();
  const siteTitle = settings['Site Title'] || 'Public Read CMS';
  const logo = settings['Site Logo'] || '';

  return (
    <header className="site-header">
      <div className="header-inner">
        {logo && (
          <img src={logo} alt={`${siteTitle} logo`} className="site-logo" />
        )}
        <h1 className="site-title">{siteTitle}</h1>
        <Navigation />
      </div>
    </header>
  );
};

export default Header;
</file>

<file path="frontend/src/components/Footer.tsx">
import React from 'react';
import { useAppContext } from '../contexts/AppContext';

const Footer: React.FC = () => {
  const { settings } = useAppContext();
  const companyName = settings['Company Name'] || 'CMS';
  const year = new Date().getFullYear();

  return (
    <footer className="site-footer">
      <div className="footer-inner">
        <p className="copyright">
          &copy; {year} {companyName}. All rights reserved.
        </p>
        <p className="footer-powered">
          Powered by Public Read CMS
        </p>
      </div>
    </footer>
  );
};

export default Footer;
</file>

<file path="frontend/src/components/PageRenderer.tsx">
import React from 'react';
import { PageDto } from '../types';
import { sanitizeHtml } from '../utils/sanitizer';

interface PageRendererProps {
  page: PageDto;
}

const PageRenderer: React.FC<PageRendererProps> = ({ page }) => {
  return (
    <article className="page-content" itemScope itemType="https://schema.org/WebPage">
      <h1 itemProp="headline">{page.pageTitle || page.pageName}</h1>
      {page.pageDescription && (
        <meta itemProp="description" content={page.pageDescription} />
      )}
      <div
        className="page-body"
        dangerouslySetInnerHTML={{ __html: sanitizeHtml(page.content || '') }}
        itemProp="text"
      />
    </article>
  );
};

export default PageRenderer;
</file>

<file path="frontend/src/components/ProductList.tsx">
import React from 'react';
import { Link } from 'react-router-dom';
import { ProductDto } from '../types';
import { formatRelativeDate } from '../utils/helpers';

interface ProductListProps {
  products: ProductDto[];
}

const ProductList: React.FC<ProductListProps> = ({ products }) => {
  return (
    <section className="product-list" aria-label="Products">
      <h2>Products</h2>
      <div className="products-grid">
        {products.map((product) => (
          <article key={product.key} className="product-card">
            <Link to={`/products/${product.key}`}>
              {product.image1 && (
                <img src={product.image1} alt={product.productName} className="product-image" />
              )}
              <h3>{product.productName}</h3>
              <p className="product-brand">{product.brand}</p>
              <p className="product-category">{product.category}</p>
              <p className="product-price">${product.retailPrice.toFixed(2)}</p>
              {product.recommended && <span className="badge recommended">Recommended</span>}
              <p className="product-date">{formatRelativeDate(product.timestamp)}</p>
            </Link>
          </article>
        ))}
      </div>
    </section>
  );
};

export default ProductList;
</file>

<file path="frontend/src/components/ProductDetail.tsx">
import React from 'react';
import { ProductDto } from '../types';
import { formatDate } from '../utils/helpers';

interface ProductDetailProps {
  product: ProductDto;
}

const ProductDetail: React.FC<ProductDetailProps> = ({ product }) => {
  return (
    <article className="product-detail" itemScope itemType="https://schema.org/Product">
      <h1 itemProp="name">{product.productName}</h1>
      {product.image1 && (
        <img src={product.image1} alt={product.productName} className="product-detail-image" />
      )}
      <div className="product-info">
        <p className="product-brand" itemProp="brand">{product.brand}</p>
        <p className="product-category">Category: {product.category}</p>
        <p className="product-line">{product.productLine}</p>
        <p className="product-price" itemProp="offers" itemScope itemType="https://schema.org/Offer">
          <span itemProp="price">${product.retailPrice.toFixed(2)}</span>
          <meta itemProp="priceCurrency" content="USD" />
        </p>
        {product.shortDescription && (
          <p className="product-short-description">{product.shortDescription}</p>
        )}
        {product.longDescription && (
          <div
            className="product-long-description"
            dangerouslySetInnerHTML={{ __html: product.longDescription }}
          />
        )}
        {product.options && (
          <p className="product-options">Options: {product.options}</p>
        )}
        <p className="product-date">Published: {formatDate(product.timestamp)}</p>
      </div>
    </article>
  );
};

export default ProductDetail;
</file>

<file path="frontend/src/components/TestimonialList.tsx">
import React from 'react';
import { TestimonialDto } from '../types';
import { formatDate } from '../utils/helpers';

interface TestimonialListProps {
  testimonials: TestimonialDto[];
}

const TestimonialList: React.FC<TestimonialListProps> = ({ testimonials }) => {
  return (
    <section className="testimonial-list" aria-label="Testimonials">
      <h2>Testimonials</h2>
      <div className="testimonials-grid">
        {testimonials.map((testimonial) => (
          <blockquote key={testimonial.id} className="testimonial-card">
            <p className="testimonial-comments">{testimonial.comments}</p>
            <footer className="testimonial-author">
              <cite>{testimonial.name}</cite>
              {testimonial.location && (
                <span className="testimonial-location">{testimonial.location}</span>
              )}
              {testimonial.showEmail && testimonial.email && (
                <a href={`mailto:${testimonial.email}`} className="testimonial-email">
                  {testimonial.email}
                </a>
              )}
              <time dateTime={testimonial.testimonialDate}>
                {formatDate(testimonial.testimonialDate)}
              </time>
            </footer>
          </blockquote>
        ))}
      </div>
    </section>
  );
};

export default TestimonialList;
</file>

<file path="frontend/src/components/ModuleRenderer.tsx">
import React from 'react';
import { ModuleDto } from '../types';

interface ModuleRendererProps {
  modules: ModuleDto[];
  location: string;
}

const ModuleRenderer: React.FC<ModuleRendererProps> = ({ modules, location }) => {
  const locationModules = modules
    .filter((m) => m.location === location && m.active && !m.disabled)
    .sort((a, b) => a.sortOrder - b.sortOrder);

  if (locationModules.length === 0) return null;

  return (
    <div className="module-container" data-location={location}>
      {locationModules.map((module) => (
        <div
          key={module.id}
          className={`module module-${module.id}`}
          style={{
            id: module.styleId || undefined,
            className: module.styleClass || undefined,
            style: module.styleInline ? { cssText: module.styleInline } : undefined,
          }}
        >
          <div className="module-wrapper">
            <h3>{module.name}</h3>
            {module.description && <p>{module.description}</p>}
          </div>
        </div>
      ))}
    </div>
  );
};

export default ModuleRenderer;
</file>

<file path="frontend/src/pages/HomePage.tsx">
import React from 'react';
import { pageService } from '../services/pageService';
import { useApi } from '../hooks/useApi';
import PageRenderer from '../components/PageRenderer';
import ModuleRenderer from '../components/ModuleRenderer';
import { moduleService } from '../services/moduleService';

const HomePage: React.FC = () => {
  const { data: page, loading, error } = useApi(
    () => pageService.getPageByFileName('default'),
    []
  );
  const { data: modules } = useApi(
    () => moduleService.getAllActiveModules(),
    []
  );

  if (loading) return <div className="loading">Loading homepage...</div>;
  if (error) return <div className="error">Error loading homepage: {error}</div>;
  if (!page) return <div className="not-found">Homepage not found.</div>;

  return (
    <main className="home-page">
      <ModuleRenderer modules={modules || []} location="header" />
      <PageRenderer page={page} />
      <ModuleRenderer modules={modules || []} location="main" />
      <ModuleRenderer modules={modules || []} location="footer" />
    </main>
  );
};

export default HomePage;
</file>

<file path="frontend/src/pages/AboutPage.tsx">
import React from 'react';
import { pageService } from '../services/pageService';
import { useApi } from '../hooks/useApi';
import PageRenderer from '../components/PageRenderer';

const AboutPage: React.FC = () => {
  const { data: page, loading, error } = useApi(
    () => pageService.getPageByFileName('about'),
    []
  );

  if (loading) return <div className="loading">Loading about page...</div>;
  if (error) return <div className="error">Error loading page: {error}</div>;
  if (!page) return <div className="not-found">About page not found.</div>;

  return (
    <main className="about-page">
      <PageRenderer page={page} />
    </main>
  );
};

export default AboutPage;
</file>

<file path="frontend/src/pages/ContactPage.tsx">
import React from 'react';
import { pageService } from '../services/pageService';
import { useApi } from '../hooks/useApi';
import PageRenderer from '../components/PageRenderer';

const ContactPage: React.FC = () => {
  const { data: page, loading, error } = useApi(
    () => pageService.getPageByFileName('contact'),
    []
  );

  if (loading) return <div className="loading">Loading contact page...</div>;
  if (error) return <div className="error">Error loading page: {error}</div>;
  if (!page) return <div className="not-found">Contact page not found.</div>;

  return (
    <main className="contact-page">
      <PageRenderer page={page} />
    </main>
  );
};

export default ContactPage;
</file>

<file path="frontend/src/pages/ProductsPage.tsx">
import React from 'react';
import { productService } from '../services/productService';
import { useApi } from '../hooks/useApi';
import ProductList from '../components/ProductList';

const ProductsPage: React.FC = () => {
  const { data: products, loading, error } = useApi(
    () => productService.getAllActiveProducts(),
    []
  );

  if (loading) return <div className="loading">Loading products...</div>;
  if (error) return <div className="error">Error loading products: {error}</div>;
  if (!products) return <div className="no-products">No products available.</div>;

  return (
    <main className="products-page">
      <h1>Products</h1>
      <ProductList products={products} />
    </main>
  );
};

export default ProductsPage;
</file>

<file path="frontend/src/pages/ProductDetailPage.tsx">
import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { productService } from '../services/productService';
import { useApi } from '../hooks/useApi';
import ProductDetail from '../components/ProductDetail';

const ProductDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const productId = parseInt(id || '0', 10);
  const { data: product, loading, error } = useApi(
    () => productService.getProductById(productId),
    [productId]
  );

  if (loading) return <div className="loading">Loading product details...</div>;
  if (error) return <div className="error">Error loading product: {error}</div>;
  if (!product) return <div className="not-found">Product not found.</div>;

  return (
    <main className="product-detail-page">
      <Link to="/products" className="back-link">&larr; Back to Products</Link>
      <ProductDetail product={product} />
    </main>
  );
};

export default ProductDetailPage;
</file>

<file path="frontend/src/pages/TestimonialsPage.tsx">
import React from 'react';
import { testimonialService } from '../services/testimonialService';
import { useApi } from '../hooks/useApi';
import TestimonialList from '../components/TestimonialList';

const TestimonialsPage: React.FC = () => {
  const { data: testimonials, loading, error } = useApi(
    () => testimonialService.getAllActiveTestimonials(),
    []
  );

  if (loading) return <div className="loading">Loading testimonials...</div>;
  if (error) return <div className="error">Error loading testimonials: {error}</div>;
  if (!testimonials) return <div className="no-testimonials">No testimonials available.</div>;

  return (
    <main className="testimonials-page">
      <h1>Testimonials</h1>
      <TestimonialList testimonials={testimonials} />
    </main>
  );
};

export default TestimonialsPage;
</file>

<file path="frontend/src/pages/NotFound.tsx">
import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <main className="not-found-page">
      <h1>404</h1>
      <h2>Page Not Found</h2>
      <p>The page you are looking for does not exist or has been moved.</p>
      <Link to="/" className="home-link">Return to Homepage</Link>
    </main>
  );
};

export default NotFound;
</file>

<file path="frontend/src/App.tsx">
import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import { AppProvider } from './contexts/AppContext';
import Header from './components/Header';
import Footer from './components/Footer';

const HomePage = lazy(() => import('./pages/HomePage'));
const AboutPage = lazy(() => import('./pages/AboutPage'));
const ContactPage = lazy(() => import('./pages/ContactPage'));
const ProductsPage = lazy(() => import('./pages/ProductsPage'));
const ProductDetailPage = lazy(() => import('./pages/ProductDetailPage'));
const TestimonialsPage = lazy(() => import('./pages/TestimonialsPage'));
const NotFound = lazy(() => import('./pages/NotFound'));

const LoadingFallback: React.FC = () => (
  <div className="loading-container">
    <div className="loading-spinner" />
    <p>Loading...</p>
  </div>
);

const App: React.FC = () => {
  return (
    <AppProvider>
      <div className="app">
        <Header />
        <Suspense fallback={<LoadingFallback />}>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/contact" element={<ContactPage />} />
            <Route path="/products" element={<ProductsPage />} />
            <Route path="/products/:id" element={<ProductDetailPage />} />
            <Route path="/testimonials" element={<TestimonialsPage />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
        <Footer />
      </div>
    </AppProvider>
  );
};

export default App;
</file>

<file path="frontend/src/styles/global.css">
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  --color-primary: #2c3e50;
  --color-secondary: #3498db;
  --color-accent: #e74c3c;
  --color-background: #ffffff;
  --color-text: #333333;
  --color-text-light: #666666;
  --color-border: #e0e0e0;
  --font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  --max-width: 1200px;
  --spacing-unit: 8px;
}

body {
  font-family: var(--font-family);
  color: var(--color-text);
  background-color: var(--color-background);
  line-height: 1.6;
  font-size: 16px;
}

.app {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

main {
  flex: 1;
  max-width: var(--max-width);
  margin: 0 auto;
  padding: calc(var(--spacing-unit) * 3);
  width: 100%;
}

/* Header */
.site-header {
  background-color: var(--color-primary);
  color: white;
  padding: calc(var(--spacing-unit) * 2) 0;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.header-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 calc(var(--spacing-unit) * 3);
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
}

.site-logo {
  height: 50px;
  width: auto;
}

.site-title {
  font-size: 1.5rem;
  margin-left: calc(var(--spacing-unit) * 2);
}

/* Navigation */
.navigation {
  flex: 1;
  text-align: right;
}

.nav-menu {
  list-style: none;
  display: flex;
  gap: calc(var(--spacing-unit) * 2);
  justify-content: flex-end;
}

.nav-link {
  color: white;
  text-decoration: none;
  padding: calc(var(--spacing-unit)) calc(var(--spacing-unit) * 1.5);
  border-radius: 4px;
  transition: background-color 0.2s;
}

.nav-link:hover,
.nav-link.active {
  background-color: rgba(255, 255, 255, 0.2);
}

/* Footer */
.site-footer {
  background-color: var(--color-primary);
  color: white;
  padding: calc(var(--spacing-unit) * 2) 0;
  margin-top: auto;
}

.footer-inner {
  max-width: var(--max-width);
  margin: 0 auto;
  padding: 0 calc(var(--spacing-unit) * 3);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Page Content */
.page-content {
  max-width: 100%;
}

.page-content h1 {
  font-size: 2rem;
  margin-bottom: calc(var(--spacing-unit) * 2);
  color: var(--color-primary);
}

.page-body {
  line-height: 1.8;
}

.page-body img {
  max-width: 100%;
  height: auto;
}

/* Products */
.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: calc(var(--spacing-unit) * 3);
  margin-top: calc(var(--spacing-unit) * 2);
}

.product-card {
  border: 1px solid var(--color-border);
  border-radius: 8px;
  overflow: hidden;
  transition: box-shadow 0.2s;
}

.product-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.product-card img {
  width: 100%;
  height: 200px;
  object-fit: cover;
}

.product-card h3 {
  padding: calc(var(--spacing-unit) * 1.5);
  font-size: 1.2rem;
}

.product-price {
  font-size: 1.25rem;
  font-weight: bold;
  color: var(--color-secondary);
  padding: 0 calc(var(--spacing-unit) * 1.5) calc(var(--spacing-unit) * 1.5);
}

.product-detail-image {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
}

/* Testimonials */
.testimonials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: calc(var(--spacing-unit) * 3);
  margin-top: calc(var(--spacing-unit) * 2);
}

.testimonial-card {
  background-color: #f9f9f9;
  border-left: 4px solid var(--color-secondary);
  padding: calc(var(--spacing-unit) * 2);
  border-radius: 4px;
}

.testimonial-comments {
  font-style: italic;
  margin-bottom: calc(var(--spacing-unit) * 1.5);
}

.testimonial-author {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 0.9rem;
  color: var(--color-text-light);
}

/* Loading & Error States */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 50vh;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-secondary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading,
.error,
.not-found {
  text-align: center;
  padding: calc(var(--spacing-unit) * 4);
}

.error {
  color: var(--color-accent);
}

.not-found-page {
  text-align: center;
  padding: calc(var(--spacing-unit) * 6);
}

.not-found-page h1 {
  font-size: 4rem;
  color: var(--color-secondary);
}

.back-link {
  display: inline-block;
  margin-bottom: calc(var(--spacing-unit) * 2);
  color: var(--color-secondary);
  text-decoration: none;
}

.back-link:hover {
  text-decoration: underline;
}

/* Responsive */
@media (max-width: 768px) {
  .header-inner {
    flex-direction: column;
    text-align: center;
  }

  .navigation {
    text-align: center;
    margin-top: calc(var(--spacing-unit) * 1.5);
  }

  .nav-menu {
    justify-content: center;
    flex-wrap: wrap;
  }

  .footer-inner {
    flex-direction: column;
    gap: calc(var(--spacing-unit));
    text-align: center;
  }
}
</file>

<file path="frontend/src/styles/variables.css">
:root {
  --color-primary: #2c3e50;
  --color-secondary: #3498db;
  --color-accent: #e74c3c;
  --color-background: #ffffff;
  --color-text: #333333;
  --color-text-light: #666666;
  --color-border: #e0e0e0;
  --font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  --max-width: 1200px;
  --spacing-unit: 8px;
  --border-radius: 8px;
  --box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  --transition-speed: 0.2s;
}
</file>

<file path="frontend/public/robots.txt">
User-agent: *
Allow: /
Sitemap: /sitemap.xml
</file>

<file path="frontend/public/favicon.ico">
<!-- Favicon placeholder -->
</file>