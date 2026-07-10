import { Award, ArrowLeft, Lock, Sparkles } from "lucide-react";
import { UserProgress } from "../types";
import { STREAK_BADGES } from "../utils/streaks";
import { LEADERBOARD_BADGES } from "../utils/leaderboard";
import { COSMETICS } from "../data/cosmetics";
import { progressToNextRank } from "../data/ranks";
import { motion, useReducedMotion } from "motion/react";

interface BadgesScreenProps {
  progress: UserProgress;
  onSelectCosmetic?: (cosmeticId: string) => void;
  onBack: () => void;
}

export default function BadgesScreen({ progress, onSelectCosmetic, onBack }: BadgesScreenProps) {
  const rm = useReducedMotion();
  const earned = new Set(progress.earnedBadgeIds ?? []);
  const streak = progress.dailyChallengeStreak ?? 0;
  const unlockedCosmetics = new Set(progress.unlockedCosmetics ?? ["candle-classic"]);
  const xp = progress.xp ?? 0;
  const rankInfo = progressToNextRank(xp);

  return (
    <div className="space-y-6 max-w-2xl mx-auto py-2 px-2">
      <div className="flex items-center justify-between pb-4 border-b border-[#e2d2ac]">
        <button
          onClick={onBack}
          className="flex items-center gap-1.5 text-sm text-[#5c4a33] hover:text-[#2a2018] font-medium py-1.5 px-3 hover:bg-[#f0e3c8] rounded-lg cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" /> Back
        </button>
        <h2 className="text-lg font-display font-bold tracking-[0.1em] text-[#2a2018]">BADGES &amp; RANKS</h2>
        <div className="w-16" />
      </div>

      <div className="pcard rounded-2xl p-5 parchment-glow">
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm font-bold text-[#2a2018]">{rankInfo.current.title}</span>
          <span className="font-mono text-sm font-bold text-[#92400e]">{xp} XP</span>
        </div>
        <div className="w-full bg-[#e7d6b0] h-2 rounded-full overflow-hidden">
          <div
            className="bg-gradient-to-r from-[#b45309] to-[#f59e0b] h-full rounded-full"
            style={{ width: `${Math.round(rankInfo.ratio * 100)}%` }}
          />
        </div>
        <p className="text-[11px] text-[#6b5537] mt-2">
          {rankInfo.next
            ? `${rankInfo.xpInto} / ${rankInfo.xpNeeded} XP until ${rankInfo.next.title}`
            : "Highest rank reached"}
        </p>
      </div>

      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-[#6b5537] mb-3 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5" /> Cosmetics
        </h3>
        <div className="space-y-3">
          {COSMETICS.map((c, i) => {
            const unlocked = unlockedCosmetics.has(c.id);
            const selected =
              c.kind === "candle"
                ? (progress.selectedCandle ?? "candle-classic") === c.id
                : (progress.selectedBanner ?? "") === c.id;
            return (
              <motion.div
                key={c.id}
                initial={rm ? false : { opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: rm ? 0 : i * 0.04 }}
                className={`pcard rounded-2xl p-4 flex items-start gap-3 ${unlocked ? "" : "opacity-70"}`}
              >
                <div
                  className={`p-2.5 rounded-xl border ${
                    unlocked
                      ? "bg-[#2a2018] text-[#fbbf24] border-[#b45309]/40"
                      : "bg-[#f0e3c8] text-[#6b5537] border-[#e2d2ac]"
                  }`}
                >
                  {unlocked ? <Sparkles className="w-5 h-5" /> : <Lock className="w-5 h-5" />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h4 className="font-bold text-[#2a2018] text-sm">{c.title}</h4>
                    <span className="text-[9px] uppercase font-bold px-2 py-0.5 bg-[#f3e8cf] text-[#6b5537] rounded">
                      {c.kind}
                    </span>
                    {selected && unlocked && (
                      <span className="text-[9px] uppercase font-bold px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded">
                        Active
                      </span>
                    )}
                  </div>
                  <p className="text-xs text-[#5c4a33] mt-0.5">{c.description}</p>
                  {!unlocked && (
                    <p className="text-[10px] text-[#92400e] font-semibold mt-1">
                      Unlocks at {c.unlockRank.replace("-", " ")} rank
                    </p>
                  )}
                  {unlocked && onSelectCosmetic && !selected && (
                    <button
                      onClick={() => onSelectCosmetic(c.id)}
                      className="mt-2 text-[10px] font-bold uppercase tracking-wider text-[#92400e] hover:underline cursor-pointer"
                    >
                      Equip
                    </button>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>

      <p className="text-center text-sm text-[#5c4a33]">
        Streak milestones unlock lasting titles. Current streak:{" "}
        <strong className="text-[#92400e]">{streak} day{streak === 1 ? "" : "s"}</strong>
      </p>

      <div className="space-y-3">
        {STREAK_BADGES.map((badge, i) => {
          const unlocked = earned.has(badge.id) || streak >= badge.threshold;
          return (
            <motion.div
              key={badge.id}
              initial={rm ? false : { opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: rm ? 0 : i * 0.05 }}
              className={`pcard rounded-2xl p-5 flex items-start gap-4 ${unlocked ? "parchment-glow border-[#d8c391]" : "opacity-70"}`}
            >
              <div
                className={`p-3 rounded-xl border ${
                  unlocked
                    ? "bg-[#2a2018] text-[#fbbf24] border-[#b45309]/40"
                    : "bg-[#f0e3c8] text-[#6b5537] border-[#e2d2ac]"
                }`}
              >
                {unlocked ? <Award className="w-6 h-6" aria-hidden="true" /> : <Lock className="w-6 h-6" aria-hidden="true" />}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-display font-bold text-[#2a2018] text-lg">{badge.title}</h3>
                  {unlocked ? (
                    <span className="text-[9px] uppercase font-bold px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded">Earned</span>
                  ) : (
                    <span className="text-[9px] uppercase font-bold px-2 py-0.5 bg-[#f3e8cf] text-[#6b5537] rounded">
                      {badge.threshold} days
                    </span>
                  )}
                </div>
                <p className="text-sm text-[#5c4a33] mt-1">{badge.description}</p>
                {!unlocked && (
                  <div className="mt-2 w-full bg-[#e7d6b0] h-1.5 rounded-full overflow-hidden">
                    <div
                      className="bg-gradient-to-r from-[#b45309] to-[#f59e0b] h-full rounded-full"
                      style={{ width: `${Math.min(100, Math.round((streak / badge.threshold) * 100))}%` }}
                    />
                  </div>
                )}
              </div>
            </motion.div>
          );
        })}
      </div>

      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider text-[#6b5537] mb-3 flex items-center gap-1.5">
          <Award className="w-3.5 h-3.5" /> Weekly leaderboard
        </h3>
        <p className="text-xs text-[#5c4a33] mb-3">
          Top-three badges are live for the current SAST week and are removed if you drop below #3.
          Boards reset Sunday 00:00 SAST (end of Saturday).
        </p>
        <div className="space-y-3">
          {LEADERBOARD_BADGES.map((badge, i) => {
            const unlocked = earned.has(badge.id);
            const placeLabel = badge.threshold === 1 ? "#1" : badge.threshold === 2 ? "#2" : "#3";
            return (
              <motion.div
                key={badge.id}
                initial={rm ? false : { opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: rm ? 0 : 0.15 + i * 0.04 }}
                className={`pcard rounded-2xl p-5 flex items-start gap-4 ${unlocked ? "parchment-glow border-[#d8c391]" : "opacity-70"}`}
              >
                <div
                  className={`p-3 rounded-xl border ${
                    unlocked
                      ? "bg-[#2a2018] text-[#fbbf24] border-[#b45309]/40"
                      : "bg-[#f0e3c8] text-[#6b5537] border-[#e2d2ac]"
                  }`}
                >
                  {unlocked ? <Award className="w-6 h-6" aria-hidden="true" /> : <Lock className="w-6 h-6" aria-hidden="true" />}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 flex-wrap">
                    <h3 className="font-display font-bold text-[#2a2018] text-lg">{badge.title}</h3>
                    {unlocked ? (
                      <span className="text-[9px] uppercase font-bold px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded">
                        Earned
                      </span>
                    ) : (
                      <span className="text-[9px] uppercase font-bold px-2 py-0.5 bg-[#f3e8cf] text-[#6b5537] rounded">
                        Top {placeLabel}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-[#5c4a33] mt-1">{badge.description}</p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
