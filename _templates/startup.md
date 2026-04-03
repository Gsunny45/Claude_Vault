<%*
// Startup template — runs on vault open
// Appends a session marker to today's inbox file

const today = tp.date.now("YYYY-MM-DD");
const time = tp.date.now("HH:mm:ss");
const inboxPath = "inbox/" + today + ".md";

let inboxFile = app.vault.getAbstractFileByPath(inboxPath);
if (!inboxFile) {
  await app.vault.create(inboxPath, "# Inbox — " + today + "\n");
  inboxFile = app.vault.getAbstractFileByPath(inboxPath);
}

if (inboxFile) {
  await app.vault.append(inboxFile, "\n---\n**" + time + "** — Vault opened. Session started.\n");
}

// Don't create a new note — this is a silent startup action
// The file this template was "applied to" should be removed
const currentFile = tp.config.target_file;
if (currentFile && currentFile.path.includes("Untitled")) {
  await app.vault.delete(currentFile);
}
%>
