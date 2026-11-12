// The two trusted chart shells share local IDs. Prefix references together so
// labels, descriptions and fragment links remain local in the combined story.
export function chartMarkup(markup, prefix) {
  return markup
    .replace(
      /\b(id|for|aria-labelledby|aria-describedby|aria-controls)="([^"]+)"/g,
      (_, attribute, ids) =>
        `${attribute}="${ids
          .split(/\s+/)
          .map((id) => prefix + id)
          .join(" ")}"`,
    )
    .replace(/href="#([^"]+)"/g, (_, id) => `href="#${prefix}${id}"`)
    .replace(/<main>/g, '<div class="chart-content">')
    .replace(/<\/main>/g, "</div>");
}
