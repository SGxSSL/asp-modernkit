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
