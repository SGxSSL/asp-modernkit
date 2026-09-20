using Microsoft.EntityFrameworkCore;
using PublicRead.Data;
using PublicRead.Data.Entities;
using PublicRead.Data.Repositories.Interfaces;

namespace PublicRead.Data.Repositories;

public class TestimonialRepository : ITestimonialRepository
{
    private readonly AppDbContext _context;

    public TestimonialRepository(AppDbContext context)
    {
        _context = context;
    }

    public async Task<List<TestimonialEntity>> GetAllActiveTestimonialsAsync()
    {
        return await _context.Testimonials
            .Where(t => t.Active)
            .OrderBy(t => t.SortOrder)
            .ToListAsync();
    }
}
