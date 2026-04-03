/**
 * Returns a quick vault stats string for embedding in notes.
 * Usage: <% tp.user.vault_stats() %>
 * Returns: "5 knowledge | 3 decisions | 2 tasks open | 1 session"
 */
function vault_stats() {
  const files = app.vault.getMarkdownFiles();
  const knowledge = files.filter(f => f.path.startsWith("knowledge/")).length;
  const decisions = files.filter(f => f.path.startsWith("decisions/")).length;
  const tasks = files.filter(f => f.path.startsWith("tasks/")).length;
  const sessions = files.filter(f => f.path.startsWith("sessions/") && !f.path.includes("/daily/") && !f.path.includes("/weekly/")).length;
  return knowledge + " knowledge | " + decisions + " decisions | " + tasks + " tasks | " + sessions + " sessions";
}
module.exports = vault_stats;
