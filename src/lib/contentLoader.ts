import { applyExpertClue } from "../data/expertClues";
import { BUNDLED_SEASONS } from "../data/seasons";
import { chaptersData, type Chapter, type WordTerm } from "../data/words";
import type { FeaturedContent, Season } from "../types";
import { getIsoWeekKey } from "../utils/streaks";
import { isSupabaseConfigured, supabase } from "./supabase";

export interface LoadedContent {
  chapters: Chapter[];
  seasons: Season[];
  wordOfTheWeek: WordTerm | null;
  featured: FeaturedContent | null;
  source: "supabase" | "bundled";
}

/** Deterministic index from a string seed (Sabbath-week key). */
function seededIndex(seed: string, modulo: number): number {
  if (modulo <= 0) return 0;
  let h = 0;
  for (let i = 0; i < seed.length; i++) {
    h = (Math.imul(31, h) + seed.charCodeAt(i)) | 0;
  }
  return Math.abs(h) % modulo;
}

/** Sabbath-aligned week key: reuse ISO week label for WOTW seeding. */
export function getSabbathWeekKey(date = new Date()): string {
  return getIsoWeekKey(date);
}

function flattenWords(chapters: Chapter[]): WordTerm[] {
  return chapters.reduce<WordTerm[]>((acc, ch) => [...acc, ...ch.words], []);
}

export function pickWordOfTheWeek(
  chapters: Chapter[],
  weekKey: string,
  overrideWordId?: string | null
): WordTerm | null {
  const all = flattenWords(chapters);
  if (all.length === 0) return null;
  if (overrideWordId) {
    const found = all.find((w) => w.id === overrideWordId);
    if (found) return found;
  }
  return all[seededIndex(weekKey, all.length)] ?? null;
}

function bundledContent(weekKey: string): LoadedContent {
  return {
    chapters: chaptersData,
    seasons: BUNDLED_SEASONS,
    wordOfTheWeek: pickWordOfTheWeek(chaptersData, weekKey),
    featured: null,
    source: "bundled",
  };
}

/**
 * Load chapters/words/seasons/featured from Supabase.
 * On any failure or empty catalog, fall back to bundled 80/20 content.
 */
export async function loadContent(date = new Date()): Promise<LoadedContent> {
  const weekKey = getSabbathWeekKey(date);

  if (!supabase || !isSupabaseConfigured) {
    return bundledContent(weekKey);
  }

  try {
    const [chaptersRes, wordsRes, seasonsRes, scRes, featuredRes] = await Promise.all([
      supabase.from("chapters").select("id, title, description, sort_order, season_id").order("sort_order"),
      supabase
        .from("words")
        .select("id, chapter_id, word, clue, expert_clue, verse, scripture, summary, sort_order")
        .order("sort_order"),
      supabase.from("seasons").select("id, title, description, starts_on, ends_on"),
      supabase.from("season_chapters").select("season_id, chapter_id"),
      supabase.from("content_featured").select("week_key, word_id, announcement").eq("week_key", weekKey).maybeSingle(),
    ]);

    if (chaptersRes.error || wordsRes.error || !chaptersRes.data?.length || !wordsRes.data?.length) {
      return bundledContent(weekKey);
    }

    const wordsByChapter = new Map<string, WordTerm[]>();
    for (const row of wordsRes.data) {
      const term = applyExpertClue({
        id: row.id as string,
        word: row.word as string,
        clue: row.clue as string,
        expertClue: (row.expert_clue as string | null) ?? undefined,
        verse: (row.verse as string) ?? "",
        scripture: (row.scripture as string) ?? "",
        summary: (row.summary as string) ?? "",
      });
      const list = wordsByChapter.get(row.chapter_id as string) ?? [];
      list.push(term);
      wordsByChapter.set(row.chapter_id as string, list);
    }

    const chapters: Chapter[] = chaptersRes.data.map((c) => ({
      id: c.id as string,
      title: c.title as string,
      description: (c.description as string) ?? "",
      seasonId: (c.season_id as string | null) ?? undefined,
      words: wordsByChapter.get(c.id as string) ?? [],
    })).filter((ch) => ch.words.length > 0);

    if (chapters.length < 10) {
      return bundledContent(weekKey);
    }

    const chapterIdsBySeason = new Map<string, string[]>();
    for (const row of scRes.data ?? []) {
      const sid = row.season_id as string;
      const list = chapterIdsBySeason.get(sid) ?? [];
      list.push(row.chapter_id as string);
      chapterIdsBySeason.set(sid, list);
    }

    let seasons: Season[] =
      (seasonsRes.data ?? []).map((s) => ({
        id: s.id as string,
        title: s.title as string,
        description: (s.description as string) ?? "",
        startsOn: (s.starts_on as string | null) ?? null,
        endsOn: (s.ends_on as string | null) ?? null,
        chapterIds:
          chapterIdsBySeason.get(s.id as string) ??
          chapters.filter((c) => c.seasonId === s.id).map((c) => c.id),
      })) ?? [];

    if (seasons.length === 0) {
      seasons = BUNDLED_SEASONS;
    }

    const featured: FeaturedContent | null = featuredRes.data
      ? {
          weekKey: featuredRes.data.week_key as string,
          wordId: (featuredRes.data.word_id as string | null) ?? null,
          announcement: (featuredRes.data.announcement as string | null) ?? null,
        }
      : null;

    const wordOfTheWeek = pickWordOfTheWeek(chapters, weekKey, featured?.wordId);

    return {
      chapters,
      seasons,
      wordOfTheWeek,
      featured,
      source: "supabase",
    };
  } catch {
    return bundledContent(weekKey);
  }
}
