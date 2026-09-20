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
