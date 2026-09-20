using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Caching.Memory;
using PublicRead.Data.Repositories.Interfaces;
using PublicRead.Models.DTOs;

namespace PublicRead.Controllers;

[ApiController]
[Route("api/public/testimonials")]
public class TestimonialsController : ControllerBase
{
    private readonly ITestimonialRepository _testimonialRepository;
    private readonly IMemoryCache _cache;

    public TestimonialsController(ITestimonialRepository testimonialRepository, IMemoryCache cache)
    {
        _testimonialRepository = testimonialRepository;
        _cache = cache;
    }

    [HttpGet]
    [ResponseCache(Duration = 300)]
    public async Task<ActionResult<List<TestimonialDto>>> GetAllActiveTestimonials()
    {
        var cacheKey = "testimonials_all";
        if (!_cache.TryGetValue(cacheKey, out List<TestimonialDto>? testimonials))
        {
            var entities = await _testimonialRepository.GetAllActiveTestimonialsAsync();
            testimonials = entities.Select(e => new TestimonialDto
            {
                ID = e.ID,
                Active = e.Active,
                Name = e.Name,
                Email = e.Email,
                ShowEmail = e.ShowEmail,
                SortOrder = e.SortOrder,
                Comments = e.Comments,
                Location = e.Location,
                TestimonialDate = e.TestimonialDate,
                Timestamp = e.Timestamp
            }).ToList();

            _cache.Set(cacheKey, testimonials, TimeSpan.FromMinutes(5));
        }

        return Ok(testimonials);
    }
}
