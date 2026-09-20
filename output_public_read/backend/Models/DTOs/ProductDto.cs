namespace PublicRead.Models.DTOs;

public class ProductDto
{
    public int Key { get; set; }
    public string PID { get; set; } = string.Empty;
    public string Category { get; set; } = string.Empty;
    public string Brand { get; set; } = string.Empty;
    public string ProductLine { get; set; } = string.Empty;
    public string ProductName { get; set; } = string.Empty;
    public string? Options { get; set; }
    public string? ShortDescription { get; set; }
    public string? LongDescription { get; set; }
    public decimal RetailPrice { get; set; }
    public decimal WholesalePrice { get; set; }
    public string? Image1 { get; set; }
    public string? Image2 { get; set; }
    public bool Active { get; set; }
    public bool Recommended { get; set; }
    public DateTime Timestamp { get; set; }
}
