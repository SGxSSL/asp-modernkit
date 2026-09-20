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
