/**
 * Returns the next available ID for a given prefix and folder.
 * Usage in template: <% tp.user.next_id("DEC", "decisions") %>
 * Returns: "DEC-0002" (or whatever the next number is)
 */
function next_id(prefix, folder) {
  const files = app.vault.getMarkdownFiles().filter(f => f.path.startsWith(folder + "/"));
  let max = 0;
  const pattern = new RegExp("^" + prefix + "-(\\d+)");
  for (const file of files) {
    const match = file.basename.match(pattern);
    if (match) {
      const num = parseInt(match[1], 10);
      if (num > max) max = num;
    }
  }
  return prefix + "-" + String(max + 1).padStart(4, "0");
}
module.exports = next_id;
