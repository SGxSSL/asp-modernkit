using PublicRead.Data.Entities;

namespace PublicRead.Data.Repositories.Interfaces;

public interface ITestimonialRepository
{
    Task<List<TestimonialEntity>> GetAllActiveTestimonialsAsync();
}
