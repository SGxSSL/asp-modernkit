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
