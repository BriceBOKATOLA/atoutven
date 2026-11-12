"use client";

import { useEffect, useState } from "react";
import { Flower } from "./Brand";

const chapters = [
  { id: "reseau", label: "Le réseau" },
  { id: "emploi", label: "L’emploi" },
  { id: "territoires", label: "Les pôles" },
  { id: "methode", label: "La méthode" },
];

export function StoryNavigation() {
  const [activeChapter, setActiveChapter] = useState("");
  useEffect(() => {
    const sections = chapters.map(({ id }) => document.getElementById(id));
    const updateChapter = () => {
      const readingLine = window.innerHeight * 0.35;
      let current = "";
      for (const section of sections) {
        if (section && section.getBoundingClientRect().top <= readingLine)
          current = section.id;
      }
      setActiveChapter(current);
    };
    updateChapter();
    window.addEventListener("scroll", updateChapter, { passive: true });
    window.addEventListener("resize", updateChapter);
    return () => {
      window.removeEventListener("scroll", updateChapter);
      window.removeEventListener("resize", updateChapter);
    };
  }, []);

  return (
    <nav className="story-navigation" aria-label="Chapitres du récit">
      <a
        href="#accueil"
        className="nav-brand"
        aria-label="EcloWork, début du récit"
      >
        ew
        <Flower />
      </a>
      <div className="chapter-links">
        {chapters.map(({ id, label }) => (
          <a
            key={id}
            href={`#${id}`}
            aria-current={activeChapter === id ? "location" : undefined}
          >
            {label}
          </a>
        ))}
      </div>
      <span className="nav-location">Île-de-France</span>
    </nav>
  );
}
