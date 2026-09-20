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
