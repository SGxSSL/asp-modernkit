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
