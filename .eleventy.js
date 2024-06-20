const fs = require("fs");

// generate hash of a string
String.prototype.hashCode = function () {
  var hash = 0,
    i,
    chr;
  if (this.length === 0) return hash;
  for (i = 0; i < this.length; i++) {
    chr = this.charCodeAt(i);
    hash = (hash << 5) - hash + chr;
    hash |= 0; // Convert to 32bit integer
  }
  return hash;
};

module.exports = function (eleventyConfig) {
  // static files
  eleventyConfig.addPassthroughCopy({ public: "/" });
  eleventyConfig.addPassthroughCopy({ springy: "/" });
  eleventyConfig.addPassthroughCopy("polycule.json");

  eleventyConfig.addFilter("fullisodate", (dt) => {
    return dt.toISOString();
  });
  eleventyConfig.addFilter("now", () => {
    return new Date();
  });
  eleventyConfig.addFilter("polycule", () => {
    return fs.readFileSync("polycule.json").toString();
  });
  eleventyConfig.addFilter("id", (toid) => {
    return toid.hashCode();
  });
};
