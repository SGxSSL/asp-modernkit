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
