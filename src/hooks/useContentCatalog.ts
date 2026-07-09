import { useEffect, useState } from "react";
import { chaptersData as bundledChapters } from "../data/words";
import { BUNDLED_SEASONS } from "../data/seasons";
import type { Chapter, WordTerm } from "../data/words";
import type { Season } from "../types";
import { loadContent, pickWordOfTheWeek, getSabbathWeekKey } from "../lib/contentLoader";

export function useContentCatalog() {
  const [chaptersData, setChaptersData] = useState<Chapter[]>(bundledChapters);
  const [seasons, setSeasons] = useState<Season[]>(BUNDLED_SEASONS);
  const [wordOfTheWeek, setWordOfTheWeek] = useState<WordTerm | null>(() =>
    pickWordOfTheWeek(bundledChapters, getSabbathWeekKey())
  );
  const [featuredAnnouncement, setFeaturedAnnouncement] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    loadContent().then((loaded) => {
      if (cancelled) return;
      setChaptersData(loaded.chapters);
      setSeasons(loaded.seasons);
      setWordOfTheWeek(loaded.wordOfTheWeek);
      setFeaturedAnnouncement(loaded.featured?.announcement ?? null);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return { chaptersData, seasons, wordOfTheWeek, featuredAnnouncement };
}
