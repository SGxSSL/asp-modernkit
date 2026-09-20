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
