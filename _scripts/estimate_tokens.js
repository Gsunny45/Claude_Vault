/**
 * Estimates token count for a string.
 * Usage in template: <% tp.user.estimate_tokens(tp.file.content) %>
 * Returns: number
 */
function estimate_tokens(text) {
  if (!text) return 0;
  return Math.ceil(text.length / 4);
}
module.exports = estimate_tokens;
