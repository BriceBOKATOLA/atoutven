// Upper bounds are exclusive. Classify raw values before display rounding.
const classes = [
  { upper: -5, color: "#2C7FB8" },
  { upper: 0, color: "#A6CEE3" },
  { upper: 5, color: "#FBE6CC" },
  { upper: 15, color: "#F5AE6B" },
  { upper: Infinity, color: "#D9531E" },
];

export const missingEvolution = {
  color: "#F1EFEA",
  label: "Donnée indisponible",
};

const percent = (value) => `${String(value).replace("-", "−")} %`;

export const evolutionClasses = classes.map((entry, index) => ({
  ...entry,
  label:
    index === 0
      ? `Moins de ${percent(entry.upper)}`
      : entry.upper === Infinity
        ? `${percent(classes[index - 1].upper)} ou plus`
        : `${percent(classes[index - 1].upper)} à moins de ${percent(entry.upper)}`,
}));

// Highcharts scans classes from last to first. Shared endpoints therefore
// belong to the higher class, preserving our exclusive upper bounds.
export const evolutionDataClasses = evolutionClasses.map((entry, index) => ({
  ...(index > 0 ? { from: evolutionClasses[index - 1].upper } : {}),
  ...(Number.isFinite(entry.upper) ? { to: entry.upper } : {}),
  color: entry.color,
  name: entry.label,
}));
