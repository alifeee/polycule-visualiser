module.exports = function (eleventyConfig) {
  // static files
  eleventyConfig.addPassthroughCopy({ public: "/" });
  eleventyConfig.addPassthroughCopy({ springy: "/" });
  eleventyConfig.addPassthroughCopy("polycule.json");
};
