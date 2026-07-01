"""MusicWorks™ V5 — Creative Master audio analysis.

Lightweight, numpy-only DSP heuristics for the Campaign Wizard's "Creative
Master" and "Creative Analysis" steps. Deliberately avoids heavy audio ML
dependencies (librosa/scipy/numba) so it stays reliable on Streamlit Cloud.

WAV uploads get full analysis (duration, tempo estimate, energy curve, hook
timestamps, mood/energy tags, best-effort structure segments). MP3/FLAC
uploads get duration-only via mutagen — there is no pure-Python, dependency-
light way to decode MP3/FLAC to PCM samples without a system binary
(ffmpeg) or a heavy ML stack, so those formats degrade gracefully rather
than risk an unreliable install.

Every numeric result here is an estimate derived from the actual waveform,
never randomized — the same file always produces the same output. Callers
(the wizard UI) are responsible for labeling these as "AI-assisted
estimates" and letting the founder edit/override them.
"""
from dataclasses import dataclass, field, asdict
from typing import Optional
import io
import wave

import numpy as np

MAX_ANALYSIS_SECONDS = 12 * 60  # cap analysis window for memory/perf reliability

MODE_MULTIPLIER = {
    "blitz": 1.3,
    "standard": 1.0,
    "growth": 1.1,
    "ministry_push": 0.9,
    "chart_push": 1.15,
}
FIXED_EVERGREEN_ASSETS = 2  # press release + church outreach — always generated, not hook-driven


@dataclass
class AudioAnalysis:
    duration_seconds: Optional[int] = None
    tempo_bpm: Optional[int] = None
    energy_curve: list = field(default_factory=list)        # ~1 value/sec, normalized 0..1
    hook_timestamps: list = field(default_factory=list)      # [{"time_seconds": int, "strength": float}]
    mood_tags: list = field(default_factory=list)            # e.g. ["dynamic", "upbeat"]
    energy_level: Optional[str] = None                       # "low" | "medium" | "high"
    structure_segments: list = field(default_factory=list)   # [{"label","start","end"}]
    degraded: bool = False
    degraded_reason: Optional[str] = None
    source: str = "manual"                                   # "waveform_analysis"|"duration_only"|"manual"

    def to_dict(self) -> dict:
        return asdict(self)


# ── Public entry point ──────────────────────────────────────────────────────

def analyze_audio(file_bytes: bytes, filename: str) -> AudioAnalysis:
    """Never raises. Returns an AudioAnalysis, degraded on any failure."""
    ext = (filename or "").lower().rsplit(".", 1)[-1] if "." in (filename or "") else ""
    try:
        if ext == "wav":
            return _analyze_wav(file_bytes)
        elif ext in ("mp3", "flac"):
            return _analyze_duration_only(file_bytes, ext)
        return AudioAnalysis(
            degraded=True,
            degraded_reason=f"Unsupported file type '.{ext}' for analysis.",
            source="manual",
        )
    except Exception as e:
        return AudioAnalysis(degraded=True, degraded_reason=f"Analysis failed: {e}", source="manual")


def suggest_deliverables(hook_count: int, duration_seconds: Optional[int],
                          campaign_mode: str = "standard") -> dict:
    """Deterministic formula deriving suggested asset counts from the
    Creative Master's detected hooks, length, and campaign strategy."""
    hooks = max(3, min(hook_count or 6, 12))
    minutes = (duration_seconds or 210) / 60
    mult = MODE_MULTIPLIER.get(campaign_mode, 1.0)

    shorts = max(4, round(hooks * 1.25 * mult))
    reels = max(3, round(hooks * 1.0 * mult))
    quote_cards = max(6, round(hooks * 1.5 * mult))
    blog_articles = max(2, round(minutes / 1.3))
    devotionals = max(2, round(minutes * mult))
    video_concepts = 3

    total = shorts + reels + quote_cards + blog_articles + devotionals + video_concepts + FIXED_EVERGREEN_ASSETS

    return {
        "detected_hooks": hooks,
        "suggested_shorts": shorts,
        "suggested_reels": reels,
        "suggested_quote_cards": quote_cards,
        "suggested_blog_articles": blog_articles,
        "suggested_devotionals": devotionals,
        "suggested_video_concepts": video_concepts,
        "estimated_total_assets": total,
    }


# ── WAV decode ───────────────────────────────────────────────────────────────

def _read_wav_mono(data: bytes) -> "tuple[np.ndarray, int]":
    """Parse a WAV file via stdlib `wave` + manual PCM unpack. Returns
    (mono float32 samples normalized to [-1, 1], sample_rate)."""
    with wave.open(io.BytesIO(data), "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        sr = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    flat = _unpack_pcm(raw, sampwidth)
    if n_channels > 1:
        usable = (len(flat) // n_channels) * n_channels
        flat = flat[:usable].reshape(-1, n_channels).mean(axis=1)
    return flat.astype(np.float32), sr


def _unpack_pcm(raw: bytes, sampwidth: int) -> np.ndarray:
    """Unpack raw PCM bytes to float32 samples normalized to [-1, 1]."""
    if sampwidth == 1:
        arr = np.frombuffer(raw, dtype=np.uint8).astype(np.float32)
        return (arr - 128.0) / 128.0
    if sampwidth == 2:
        arr = np.frombuffer(raw, dtype="<i2").astype(np.float32)
        return arr / 32768.0
    if sampwidth == 3:
        # numpy has no native int24 — unpack 3-byte little-endian groups manually.
        b = np.frombuffer(raw, dtype=np.uint8)
        n = len(b) // 3
        b = b[: n * 3].reshape(n, 3)
        i32 = (
            b[:, 0].astype(np.int32)
            | (b[:, 1].astype(np.int32) << 8)
            | (b[:, 2].astype(np.int32) << 16)
        )
        neg = i32 >= (1 << 23)
        i32[neg] -= 1 << 24
        return i32.astype(np.float32) / float(1 << 23)
    if sampwidth == 4:
        arr = np.frombuffer(raw, dtype="<i4").astype(np.float32)
        return arr / 2147483648.0
    raise ValueError(f"Unsupported WAV sample width: {sampwidth * 8}-bit")


# ── Signal analysis ──────────────────────────────────────────────────────────

def _rms_energy_curve(samples: np.ndarray, sr: int, window_seconds: float = 1.0) -> np.ndarray:
    """Non-overlapping RMS windows, normalized to 0..1 by the curve's own max."""
    if samples is None or len(samples) == 0 or sr <= 0:
        return np.array([], dtype=np.float32)
    win = max(1, int(sr * window_seconds))
    n_windows = max(1, len(samples) // win)
    trimmed = samples[: n_windows * win]
    if len(trimmed) == 0:
        return np.array([], dtype=np.float32)
    reshaped = trimmed.reshape(n_windows, win)
    rms = np.sqrt(np.mean(np.square(reshaped), axis=1))
    peak = float(rms.max()) if rms.size and rms.max() > 1e-9 else 1.0
    return (rms / peak).astype(np.float32)


def _estimate_tempo(envelope: np.ndarray, envelope_rate: float) -> Optional[int]:
    """Autocorrelation-based tempo estimate on a fine-grained energy envelope,
    restricted to the 60-180 BPM plausible range."""
    if envelope is None or envelope_rate <= 0 or len(envelope) < int(envelope_rate * 2):
        return None
    x = envelope - envelope.mean()
    if np.allclose(x, 0):
        return None
    corr = np.correlate(x, x, mode="full")
    corr = corr[len(corr) // 2:]  # non-negative lags only

    lag_min = max(1, int(round(envelope_rate * 60.0 / 180.0)))  # fastest plausible tempo
    lag_max = int(round(envelope_rate * 60.0 / 60.0))            # slowest plausible tempo
    lag_max = min(lag_max, len(corr) - 1)
    if lag_max <= lag_min:
        return None

    window = corr[lag_min:lag_max + 1]
    best_lag = lag_min + int(np.argmax(window))
    if best_lag <= 0:
        return None
    bpm = 60.0 * envelope_rate / best_lag
    return int(round(bpm))


def _detect_hooks(energy_curve: np.ndarray, duration_seconds: Optional[int],
                   min_spacing_seconds: int = 8, top_n: int = 12) -> list:
    """Greedy peak-picking on the 1-second energy curve: accept the highest
    remaining peak only if it's far enough from every already-accepted peak."""
    if energy_curve is None or len(energy_curve) == 0:
        return []
    cap = max(3, min(top_n, (duration_seconds or len(energy_curve)) // 15))
    order = np.argsort(energy_curve)[::-1]

    accepted: list = []
    for idx in order:
        t = int(idx)
        if all(abs(t - a) >= min_spacing_seconds for a in accepted):
            accepted.append(t)
        if len(accepted) >= cap:
            break

    accepted.sort()
    return [{"time_seconds": t, "strength": float(energy_curve[t])} for t in accepted]


def _mood_and_energy(energy_curve: np.ndarray, tempo_bpm: Optional[int]) -> "tuple[str, list]":
    if energy_curve is None or len(energy_curve) == 0:
        return "medium", []

    mean_e = float(np.mean(energy_curve))
    var_e = float(np.var(energy_curve))

    if mean_e > 0.6:
        level = "high"
    elif mean_e > 0.35:
        level = "medium"
    else:
        level = "low"

    tags = ["dynamic" if var_e > 0.03 else "steady"]
    if tempo_bpm:
        if tempo_bpm >= 120:
            tags.append("upbeat")
        elif tempo_bpm >= 90:
            tags.append("driving")
        else:
            tags.append("reflective")

    return level, tags


def _segment_structure(energy_curve: np.ndarray, duration_seconds: Optional[int]) -> list:
    """Best-effort structural segmentation — NOT a real audio structure
    detector. Splits into 3-5 roughly equal segments snapped to nearby energy
    transitions, then labels by position (first=Intro, last=Outro) and
    relative energy (highest-energy middle segment(s) = Chorus)."""
    n = len(energy_curve) if energy_curve is not None else 0
    if not duration_seconds or duration_seconds < 20 or n < 5:
        return [{"label": "Full Song", "start": 0, "end": int(duration_seconds or n)}]

    n_segments = 5 if duration_seconds >= 150 else 3
    bounds = [round(i * n / n_segments) for i in range(n_segments + 1)]

    tolerance = max(2, n // (n_segments * 4))
    for i in range(1, n_segments):
        lo = max(0, bounds[i] - tolerance)
        hi = min(n - 1, bounds[i] + tolerance)
        if hi > lo:
            window = energy_curve[lo:hi + 1]
            diffs = np.abs(np.diff(window))
            if diffs.size:
                bounds[i] = lo + int(np.argmax(diffs))

    bounds = sorted(set(bounds))
    if len(bounds) != n_segments + 1:
        bounds = [round(i * n / n_segments) for i in range(n_segments + 1)]

    segment_energy = []
    for i in range(len(bounds) - 1):
        s, e = bounds[i], bounds[i + 1]
        seg = energy_curve[s:e] if e > s else energy_curve[s:s + 1]
        segment_energy.append(float(np.mean(seg)) if len(seg) else 0.0)

    labels = _label_segments(len(bounds) - 1, segment_energy)
    return [{"label": labels[i], "start": bounds[i], "end": bounds[i + 1]} for i in range(len(bounds) - 1)]


def _label_segments(count: int, energies: list) -> list:
    if count <= 1:
        return ["Full Song"] * max(count, 1)

    labels = [None] * count
    labels[0] = "Intro"
    labels[-1] = "Outro"

    middle_idx = list(range(1, count - 1))
    if middle_idx:
        sorted_middle = sorted(middle_idx, key=lambda i: energies[i], reverse=True)
        chorus_count = max(1, len(middle_idx) // 2)
        chorus_set = set(sorted_middle[:chorus_count])
        toggle = "Verse"
        for i in middle_idx:
            if i in chorus_set:
                labels[i] = "Chorus"
            else:
                labels[i] = toggle
                toggle = "Bridge" if toggle == "Verse" else "Verse"

    return labels


# ── Format handlers ──────────────────────────────────────────────────────────

def _analyze_wav(data: bytes) -> AudioAnalysis:
    try:
        samples, sr = _read_wav_mono(data)
    except Exception as e:
        return AudioAnalysis(degraded=True, degraded_reason=f"Could not read WAV audio: {e}", source="manual")

    if sr <= 0 or len(samples) == 0:
        return AudioAnalysis(
            degraded=True,
            degraded_reason="WAV file contained no readable audio samples.",
            source="manual",
        )

    full_duration = int(round(len(samples) / sr))

    analysis_samples = samples
    truncated = False
    max_samples = MAX_ANALYSIS_SECONDS * sr
    if len(samples) > max_samples:
        analysis_samples = samples[:max_samples]
        truncated = True

    energy_curve = _rms_energy_curve(analysis_samples, sr, window_seconds=1.0)
    envelope = _rms_energy_curve(analysis_samples, sr, window_seconds=0.02)
    tempo = _estimate_tempo(envelope, envelope_rate=1.0 / 0.02)
    hooks = _detect_hooks(energy_curve, full_duration)
    energy_level, mood_tags = _mood_and_energy(energy_curve, tempo)
    structure = _segment_structure(energy_curve, full_duration)

    return AudioAnalysis(
        duration_seconds=full_duration,
        tempo_bpm=tempo,
        energy_curve=energy_curve.tolist(),
        hook_timestamps=hooks,
        mood_tags=mood_tags,
        energy_level=energy_level,
        structure_segments=structure,
        degraded=truncated,
        degraded_reason="Analysis limited to the first 12 minutes of a longer file." if truncated else None,
        source="waveform_analysis",
    )


def _analyze_duration_only(data: bytes, ext: str) -> AudioAnalysis:
    duration = None
    try:
        if ext == "mp3":
            from mutagen.mp3 import MP3
            duration = int(MP3(io.BytesIO(data)).info.length)
        elif ext == "flac":
            from mutagen.flac import FLAC
            duration = int(FLAC(io.BytesIO(data)).info.length)
    except Exception:
        duration = None

    return AudioAnalysis(
        duration_seconds=duration,
        degraded=True,
        degraded_reason=(
            f"Full waveform analysis needs a WAV file — showing duration only for this .{ext} upload. "
            "Upload the WAV master for hook detection, tempo, and mood estimates."
        ),
        source="duration_only",
    )
