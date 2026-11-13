import { NetworkMap } from "../../components/NetworkMap";
import Image from "next/image";
import { Wordmark } from "../../components/Brand";
import { StoryNavigation } from "../../components/StoryNavigation";
import EmploymentExplorer from "../(chart-2)/charts/chart-2/Explorer";
import TerritoriesExplorer from "../(chart-3)/charts/chart-3/explorer";

export default function Home() {
  return (
    <>
      <a href="#recit" className="skip-link">
        Aller au contenu
      </a>
      <header className="hero" id="accueil">
        <div className="hero-top">
          <a href="#accueil" className="team">
            rhizome
          </a>
          <span>Hackaviz 2026 — Défi 2</span>
        </div>
        <div className="hero-title">
          <h1>
            <Wordmark />
            <span className="sr-only">
              {" "}
              — Mobilités et emploi en Île-de-France
            </span>
          </h1>
          <p className="tagline">Mobilités et emploi en Île-de-France</p>
        </div>
        <div className="hero-bottom">
          <p>
            Quel a été l’impact du développement du réseau de transport sur
            l’emploi ces dix dernières années ?
          </p>
          <a href="#recit" className="discover">
            Explorer les cartes <span aria-hidden="true">↓</span>
          </a>
        </div>
      </header>
      <StoryNavigation />
      <main id="recit" tabIndex={-1}>
        <section
          className="chapter network section-wrap"
          id="reseau"
          aria-labelledby="network-title"
        >
          <div className="chapter-intro">
            <div>
              <h2 id="network-title">
                Le réseau
                <br />
                ferré.
              </h2>
            </div>
            <p>Découvrez les lignes et gares ouvertes entre 2015 et 2025.</p>
          </div>
          <NetworkMap />
          <p className="reading-note">
            La présence d’une gare dans une commune ne mesure ni le temps de
            trajet ni l’accès effectif à un emploi.
          </p>
        </section>
        <section
          className="chapter employment section-wrap"
          id="emploi"
          aria-labelledby="employment-title"
        >
          <div className="chapter-intro">
            <div>
              <h2 id="employment-title">
                L’emploi
                <br />
                sur le territoire.
              </h2>
            </div>
            <p>
              Comparez l’évolution des demandeurs d’emploi par commune et les
              indicateurs des zones d’emploi.
            </p>
          </div>
          <EmploymentExplorer />
        </section>
        <section
          className="chapter territories section-wrap"
          id="territoires"
          aria-labelledby="territories-title"
        >
          <div className="chapter-intro">
            <div>
              <h2 id="territories-title">
                Les pôles
                <br />
                d’emploi.
              </h2>
            </div>
            <p>
              Explorez les pôles d’emploi et les indicateurs des départements
              franciliens.
            </p>
          </div>
          <TerritoriesExplorer />
        </section>
        <section
          className="method section-wrap"
          id="methode"
          aria-labelledby="method-title"
        >
          <div>
            <h2 id="method-title">
              Méthode
              <br />
              et limites.
            </h2>
          </div>
          <div className="method-details">
            <p>
              Ces cartes décrivent des évolutions. Elles ne mesurent ni les
              déplacements individuels ni l’effet d’une nouvelle ligne sur
              l’emploi.
            </p>
            <p>
              La carte du réseau retient les ouvertures de 2015 à 2025. Le total
              en kilomètres additionne les tronçons datés de cette période, hors
              TER, sur les lignes ayant une gare récente. Le T14 reprend une
              ligne ancienne renommée en 2025. Il figure dans le réseau
              existant. Une gare présente sur plusieurs lignes est comptée pour
              chaque ligne. Les tronçons du prolongement du métro 11 sont
              présents dans la source mais sans date : ils sont exclus de cette
              carte et du total. Ses gares de 2024 figurent sur la carte.
            </p>
            <p className="method-source">
              Projet de l’équipe Rhizome — Hackaviz 2026
            </p>
          </div>
        </section>
      </main>
      <footer className="footer section-wrap">
        <Wordmark />
        <div className="footer-credits">
          <span>Un projet de l’équipe Rhizome</span>
          <span>Hackaviz 2026 — Île-de-France</span>
          <div className="footer-logos">
            <a href="https://www.iledefrance-mobilites.fr/">
              <Image
                src="/images/ile-de-france-mobilites-transparent.png"
                alt="Île-de-France Mobilités"
                width={2560}
                height={597}
                unoptimized
              />
            </a>
            <a href="https://datactivist.coop/fr/">
              <Image
                src="/images/datactivist-transparent.png"
                alt="Datactivist"
                width={1053}
                height={136}
                unoptimized
              />
            </a>
          </div>
        </div>
      </footer>
    </>
  );
}
