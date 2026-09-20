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
