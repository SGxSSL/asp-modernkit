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
