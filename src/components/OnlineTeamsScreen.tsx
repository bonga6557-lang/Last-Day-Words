import { useCallback, useEffect, useState } from "react";
import { ArrowLeft, Copy, Play, Users } from "lucide-react";
import type { Chapter } from "../data/words";
import TeamsModeGame from "./TeamsModeGame";
import {
  supabase,
  isSupabaseConfigured,
  fetchGameRoom,
  startOnlineTeamsGame,
  updateOnlineTeamsRoom,
  leaveOnlineTeamsRoom,
  type GameRoom,
} from "../lib/supabase";
import {
  createOnlineTeamsPayload,
  parseOnlineTeamsPayload,
  type OnlineTeamsPayload,
} from "../utils/onlineTeams";

interface OnlineTeamsScreenProps {
  chapters: Chapter[];
  onBack: () => void;
}

function randomCode(): string {
  const alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789";
  let out = "";
  for (let i = 0; i < 6; i++) out += alphabet[Math.floor(Math.random() * alphabet.length)];
  return out;
}

function isCodeCollision(error: unknown): boolean {
  const err = error as { code?: string; message?: string } | null;
  return err?.code === "23505" || /duplicate key|unique/i.test(err?.message ?? "");
}

export default function OnlineTeamsScreen({ chapters, onBack }: OnlineTeamsScreenProps) {
  const allWords = chapters.flatMap((c) => c.words);
  const [code, setCode] = useState("");
  const [joinCode, setJoinCode] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [members, setMembers] = useState<{ display_name: string; team: string }[]>([]);
  const [roomId, setRoomId] = useState<string | null>(null);
  const [room, setRoom] = useState<GameRoom | null>(null);
  const [userId, setUserId] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  const refreshMembers = useCallback(async (id: string) => {
    if (!supabase) return;
    const { data } = await supabase.from("room_members").select("team, user_id").eq("room_id", id);
    const ids = (data ?? []).map((m) => m.user_id as string);
    const { data: profiles } = ids.length
      ? await supabase.from("profiles").select("id, display_name").in("id", ids)
      : { data: [] as { id: string; display_name: string }[] };
    const nameById = new Map((profiles ?? []).map((p) => [p.id, p.display_name]));
    setMembers(
      (data ?? []).map((m) => ({
        team: m.team as string,
        display_name: nameById.get(m.user_id as string) ?? "Player",
      }))
    );
  }, []);

  const refreshRoom = useCallback(async (id: string) => {
    const next = await fetchGameRoom(id);
    if (next) setRoom(next);
  }, []);

  useEffect(() => {
    if (!supabase) return;
    void supabase.auth.getUser().then(({ data }) => setUserId(data.user?.id ?? null));
  }, []);

  useEffect(() => {
    if (!supabase || !roomId) return;
    const client = supabase;
    const channel = client
      .channel(`room:${roomId}`)
      .on(
        "postgres_changes",
        { event: "*", schema: "public", table: "room_members", filter: `room_id=eq.${roomId}` },
        () => void refreshMembers(roomId)
      )
      .on(
        "postgres_changes",
        { event: "UPDATE", schema: "public", table: "game_rooms", filter: `id=eq.${roomId}` },
        () => void refreshRoom(roomId)
      )
      .subscribe();
    void refreshMembers(roomId);
    void refreshRoom(roomId);
    return () => {
      void client.removeChannel(channel);
    };
  }, [roomId, refreshMembers, refreshRoom]);

  useEffect(() => {
    return () => {
      if (!roomId || !userId) return;
      void leaveOnlineTeamsRoom(roomId, userId);
    };
  }, [roomId, userId]);

  const ensureAuth = async () => {
    if (!supabase) throw new Error("Supabase not configured");
    const { data } = await supabase.auth.getUser();
    if (!data.user) throw new Error("Sign in first (Account) to create or join a room.");
    setUserId(data.user.id);
    return data.user;
  };

  const createRoom = async () => {
    setError(null);
    setStatus(null);
    try {
      const user = await ensureAuth();
      let data: { id: string; code: string } | null = null;
      for (let attempt = 0; attempt < 5; attempt++) {
        const newCode = randomCode();
        const { data: created, error: err } = await supabase!
          .from("game_rooms")
          .insert({ code: newCode, host_id: user.id, status: "waiting" })
          .select("id, code")
          .single();
        if (!err) {
          data = created;
          break;
        }
        if (!isCodeCollision(err)) throw err;
      }
      if (!data) throw new Error("Could not create a unique room code. Try again.");
      await supabase!.from("room_members").insert({ room_id: data.id, user_id: user.id, team: "white" });
      setCode(data.code);
      setRoomId(data.id);
      setStatus(`Room ${data.code} created. Share the code with your youth group.`);
      await refreshRoom(data.id);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Could not create room");
    }
  };

  const joinRoom = async () => {
    setError(null);
    setStatus(null);
    try {
      const user = await ensureAuth();
      const normalized = joinCode.trim().toUpperCase();
      const { data: found, error: err } = await supabase!
        .from("game_rooms")
        .select("id, code")
        .eq("code", normalized)
        .maybeSingle();
      if (err) throw err;
      if (!found) throw new Error("No room with that code.");
      const { count } = await supabase!
        .from("room_members")
        .select("*", { count: "exact", head: true })
        .eq("room_id", found.id)
        .eq("team", "black");
      const team = (count ?? 0) === 0 ? "black" : "white";
      const { error: joinErr } = await supabase!
        .from("room_members")
        .upsert({ room_id: found.id, user_id: user.id, team });
      if (joinErr) throw joinErr;
      setCode(found.code);
      setRoomId(found.id);
      setStatus(`Joined room ${found.code} as ${team}.`);
      await refreshRoom(found.id);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Could not join room");
    }
  };

  const handleStartGame = async () => {
    if (!roomId || !room || userId !== room.host_id) return;
    setStarting(true);
    setError(null);
    try {
      const payload = createOnlineTeamsPayload(allWords);
      await startOnlineTeamsGame(roomId, payload as unknown as Record<string, unknown>);
      await refreshRoom(roomId);
      setStatus("Match started — pass the device between teams.");
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Could not start game");
    } finally {
      setStarting(false);
    }
  };

  const handleControlledUpdate = async (
    payload: OnlineTeamsPayload,
    scores: { white: number; black: number }
  ) => {
    if (!roomId) return;
    await updateOnlineTeamsRoom(roomId, {
      payload: payload as unknown as Record<string, unknown>,
      white_score: scores.white,
      black_score: scores.black,
      status: payload.phase === "finished" ? "finished" : "playing",
    });
  };

  const copyCode = async () => {
    if (!code) return;
    await navigator.clipboard.writeText(code);
    setStatus("Room code copied.");
  };

  const parsedPayload = room ? parseOnlineTeamsPayload(room.payload) : null;
  const isHost = Boolean(room && userId && room.host_id === userId);
  const inGame = room?.status === "playing" || room?.status === "finished";

  if (inGame && parsedPayload && room) {
    return (
      <TeamsModeGame
        chapters={chapters}
        onBack={onBack}
        controlled={{
          payload: parsedPayload,
          scores: { white: room.white_score, black: room.black_score },
          onUpdate: handleControlledUpdate,
        }}
      />
    );
  }

  return (
    <div className="max-w-lg mx-auto space-y-6 py-2 px-2">
      <div className="flex items-center justify-between pb-4 border-b border-[#e2d2ac]">
        <button onClick={onBack} className="flex items-center gap-1.5 text-sm text-[#5c4a33] font-medium cursor-pointer">
          <ArrowLeft className="w-4 h-4" /> Back
        </button>
        <h2 className="text-lg font-display font-bold tracking-[0.1em] text-[#2a2018]">ONLINE TEAMS</h2>
        <div className="w-12" />
      </div>

      {!isSupabaseConfigured && (
        <p className="text-sm text-red-800">Configure Supabase to use room codes.</p>
      )}

      <div className="pcard rounded-2xl p-6 space-y-4">
        <p className="text-sm text-[#5c4a33]">
          Create a room for Friday youth group, or join with a 6-character code. When the host starts the match, everyone in the room sees the same synced pass-and-play board.
        </p>
        <button
          onClick={createRoom}
          className="w-full flex items-center justify-center gap-2 py-3 bg-[#2a2018] text-[#f8f1e3] rounded-lg text-xs font-bold uppercase tracking-wider cursor-pointer"
        >
          <Users className="w-3.5 h-3.5" /> Create Room
        </button>

        <div className="flex gap-2">
          <input
            value={joinCode}
            onChange={(e) => setJoinCode(e.target.value.toUpperCase())}
            maxLength={6}
            placeholder="ROOM CODE"
            className="flex-1 px-3 py-2 rounded-lg border border-[#e2d2ac] bg-[#fbf5e9] text-sm font-mono tracking-widest uppercase"
          />
          <button
            onClick={joinRoom}
            className="px-4 py-2 bg-[#f0e3c8] border border-[#e2d2ac] rounded-lg text-xs font-bold uppercase cursor-pointer"
          >
            Join
          </button>
        </div>
      </div>

      {code && (
        <div className="pcard rounded-2xl p-6 text-center space-y-3">
          <div className="text-[10px] uppercase tracking-wider font-bold text-[#6b5537]">Room Code</div>
          <div className="text-4xl font-mono font-bold tracking-[0.3em] text-[#2a2018]">{code}</div>
          <button
            onClick={copyCode}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-[#92400e] cursor-pointer"
          >
            <Copy className="w-3.5 h-3.5" /> Copy code
          </button>
          {isHost && room?.status === "waiting" && (
            <button
              onClick={handleStartGame}
              disabled={starting || members.length < 1}
              className="w-full flex items-center justify-center gap-2 py-3 mt-2 bg-[#92400e] text-[#f8f1e3] rounded-lg text-xs font-bold uppercase tracking-wider cursor-pointer disabled:opacity-50"
            >
              <Play className="w-3.5 h-3.5" /> {starting ? "Starting…" : "Start Match"}
            </button>
          )}
          <div className="pt-2 space-y-1 text-left">
            {members.map((m, i) => (
              <div key={i} className="text-sm text-[#5c4a33] flex justify-between">
                <span>{m.display_name}</span>
                <span className="uppercase text-[10px] font-bold tracking-wider">{m.team}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {status && <p className="text-sm text-emerald-800 text-center">{status}</p>}
      {error && <p className="text-sm text-red-800 text-center">{error}</p>}
    </div>
  );
}
